"""Tests for :meth:`tugalex.TugaLexicon.get_noun_gender`.

The expected genders do not come from tugalex. Each noun has the same gender
in MorphoBr (LR-POR/MorphoBr, nouns/*.dict, +F or +M). For "tarde" and
"planeta", which MorphoBr lists without a gender, the gender is the Gender
feature of the UD Portuguese-Bosque treebank. Nouns of both genders are
common-gender nouns ("o/a artista") or nouns whose gender changes with the
meaning ("o rádio", the set; "a rádio", the station).
"""
import csv
import gzip

import pytest

from tugalex import NOUN_GENDER_PATH, TugaLexicon, suffix_noun_gender


@pytest.mark.parametrize("word,gender", [
    # feminine nouns that no suffix rule reads as feminine
    ("lei", "f"), ("leis", "f"), ("vez", "f"), ("vezes", "f"), ("mãe", "f"),
    ("flor", "f"), ("flores", "f"), ("cor", "f"), ("luz", "f"), ("ponte", "f"),
    ("tarde", "f"),
    # masculine nouns in -a
    ("dia", "m"), ("dias", "m"), ("mapa", "m"), ("problema", "m"),
    ("problemas", "m"), ("sistema", "m"), ("clima", "m"), ("programa", "m"),
    ("planeta", "m"),
    # nouns that the suffix rules read correctly
    ("casa", "f"), ("casas", "f"), ("nação", "f"), ("nações", "f"),
    ("cidade", "f"), ("imagem", "f"), ("imagens", "f"), ("carro", "m"),
    ("metros", "m"), ("professor", "m"),
    # a loanword sense does not make a common noun both-gender
    ("cores", "f"), ("meta", "f"), ("média", "f"),
    # "crises" is also the plural of the rare "cris" (eclipse, kris);
    # MorphoBr: crise+N+F+PL
    ("crises", "f"),
    # nouns of both genders
    ("artista", "mf"), ("artistas", "mf"), ("estudante", "mf"),
    ("rádio", "mf"),
])
def test_noun_gender(word, gender):
    assert TugaLexicon.get_noun_gender(word) == gender


@pytest.mark.parametrize("word,gender", [("Lei", "f"), ("DIA", "m")])
def test_case_insensitive(word, gender):
    assert TugaLexicon.get_noun_gender(word) == gender


@pytest.mark.parametrize("word", ["", "123", "zzk"])
def test_no_rule_and_not_listed(word):
    assert TugaLexicon.get_noun_gender(word) is None


# Words whose usual sense is a closed-class word with no gender: adverbs,
# prepositions, pronouns, conjunctions, interjections ("caramba"), neuter
# contractions ("disso" = de + isso) and words of invariable gender ("qual",
# "você"). A rare noun sense ("o agora", "o nada", "um senão") does not
# decide: scripts/noun_gender_overrides.csv gives those words an empty gender,
# citing Priberam. "pra" and "pa" are the informal "para".
@pytest.mark.parametrize("word", [
    "ainda", "embora", "para", "cada", "caramba", "disso", "disto", "daquilo",
    "Ainda", "PARA", "pra", "pa", "ou", "porém", "senão", "mais", "agora",
    "nada", "eu", "si", "bastante", "qual", "você", "vocês",
])
def test_closed_class_only(word):
    assert TugaLexicon.get_noun_gender(word) is None


# Determiners, pronouns, articles and contractions keep their grammatical
# gender, also when the word has a noun entry ("o as", "os quanta").
# Contractions take the gender of their article or pronoun part ("da" = de +
# a, "ao" = a + o).
@pytest.mark.parametrize("word,gender", [
    ("uma", "f"), ("umas", "f"), ("as", "f"), ("esta", "f"), ("outra", "f"),
    ("toda", "f"), ("todas", "f"), ("quanta", "f"), ("minha", "f"), ("ela", "f"),
    ("um", "m"), ("os", "m"), ("este", "m"), ("todo", "m"), ("ele", "m"),
    ("da", "f"), ("na", "f"), ("pela", "f"), ("numa", "f"), ("dessa", "f"),
    ("do", "m"), ("no", "m"), ("ao", "m"), ("dos", "m"),
])
def test_agreeing_word_keeps_gender(word, gender):
    assert TugaLexicon.get_noun_gender(word) == gender


# Other closed-class words with a noun entry in the English Wiktionary take
# the gender of that entry: "o caso", "o dado", "o mal", "o fora" (a snub,
# Brazil), "os antes" (plural only), "a via", "o segundo", "as vezes", "o lá"
# (the note).
@pytest.mark.parametrize("word,gender", [
    ("caso", "m"), ("dado", "m"), ("mal", "m"), ("fora", "m"), ("antes", "m"),
    ("via", "f"), ("segundo", "m"), ("vezes", "f"), ("lá", "m"),
])
def test_noun_entry_gives_gender(word, gender):
    assert TugaLexicon.get_noun_gender(word) == gender


# Masculine nouns that the English Wiktionary lists without a noun entry.
# scripts/noun_gender_overrides.csv sets them, citing Priberam: "o alto"
# (the highest point), "o rápido" (rapids), "o positivo", "o contra", "o
# hosana".
@pytest.mark.parametrize("word", ["alto", "rápido", "positivo", "contra", "hosana"])
def test_noun_from_dictionary(word):
    assert TugaLexicon.get_noun_gender(word) == "m"


# The usual sense decides. "mas" is usually the conjunction "but" (Priberam
# lists "conjunção adversativa" first), so the override gives it an empty
# gender: "Tenho 2 mas não chegam" has no noun after the number. "ás" is
# usually the noun "o ás" (the ace); "ás" for "às" is an obsolete spelling.
@pytest.mark.parametrize("word,gender", [("mas", None), ("Mas", None), ("ás", "m")])
def test_usual_sense_decides(word, gender):
    assert TugaLexicon.get_noun_gender(word) == gender


# "a capital" (the city, the capital letter) is the usual sense. "o capital"
# (money) is rarer, and a determiner before the number still decides it.
@pytest.mark.parametrize("word", ["capital", "capitais"])
def test_capital_is_feminine(word):
    assert TugaLexicon.get_noun_gender(word) == "f"


# The fruit is feminine. The masculine readings are rare senses ("o banana",
# a weakling; the surname "Laranja"), so scripts/noun_gender_overrides.csv
# sets them to "f".
@pytest.mark.parametrize("word", ["banana", "bananas", "laranja", "laranjas"])
def test_fruit_is_feminine(word):
    assert TugaLexicon.get_noun_gender(word) == "f"


def test_non_noun_rows_override_a_suffix_rule():
    """Every empty-gender row is a word that the suffix rules give a gender."""
    with gzip.open(NOUN_GENDER_PATH, "rt", encoding="utf-8", newline="") as f:
        non_nouns = [row["word"] for row in csv.DictReader(f) if not row["gender"]]
    assert "ainda" in non_nouns
    assert [w for w in non_nouns if suffix_noun_gender(w) is None] == []
