"""Tests for :meth:`tugalex.TugaLexicon.get_noun_gender`.

The expected genders do not come from tugalex. Each noun has the same gender
in MorphoBr (LR-POR/MorphoBr, nouns/*.dict, +F or +M). For "tarde" and
"planeta", which MorphoBr lists without a gender, the gender is the Gender
feature of the UD Portuguese-Bosque treebank. Nouns of both genders are
common-gender nouns ("o/a artista") or nouns whose gender changes with the
meaning ("o capital", "a capital").
"""
import pytest

from tugalex import TugaLexicon


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
