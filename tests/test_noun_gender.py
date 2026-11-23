"""Tests for :meth:`tugalex.TugaLexicon.get_noun_gender`.

The expected genders do not come from tugalex. Each noun has the same gender
in MorphoBr (LR-POR/MorphoBr, nouns/*.dict, +F or +M). For "tarde" and
"planeta", which MorphoBr lists without a gender, the gender is the Gender
feature of the UD Portuguese-Bosque treebank. Nouns of both genders are
common-gender nouns ("o/a artista") or nouns whose gender changes with the
meaning ("o capital", "a capital").
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
    ("capital", "mf"), ("rádio", "mf"),
])
def test_noun_gender(word, gender):
    assert TugaLexicon.get_noun_gender(word) == gender


@pytest.mark.parametrize("word,gender", [("Lei", "f"), ("DIA", "m")])
def test_case_insensitive(word, gender):
    assert TugaLexicon.get_noun_gender(word) == gender


@pytest.mark.parametrize("word", ["", "123", "zzk"])
def test_no_rule_and_not_listed(word):
    assert TugaLexicon.get_noun_gender(word) is None


# Words that the English Wiktionary lists as an adverb, preposition,
# conjunction, pronoun, determiner or article, and not as a noun.
@pytest.mark.parametrize("word", [
    "ainda", "embora", "contra", "para", "cada", "uma", "outra",
    "Ainda", "PARA",
])
def test_never_a_noun(word):
    assert TugaLexicon.get_noun_gender(word) is None


# Closed-class words with a noun entry in the English Wiktionary take the
# gender of that entry: "o caso", "o dado", "o mal", "o nada" (nothingness),
# "o agora" (the present time), "o fora" (a snub, Brazil), "os antes" (plural
# only), "a via", "o segundo", "as vezes", "o lá" (the note). "minha" is the
# feminine of the noun "o meu" (mine, used substantively).
@pytest.mark.parametrize("word,gender", [
    ("caso", "m"), ("dado", "m"), ("mal", "m"), ("nada", "m"), ("agora", "m"),
    ("fora", "m"), ("antes", "m"), ("via", "f"), ("segundo", "m"),
    ("vezes", "f"), ("lá", "m"), ("minha", "f"),
])
def test_noun_entry_gives_gender(word, gender):
    assert TugaLexicon.get_noun_gender(word) == gender


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
