"""Tests for :meth:`tugalex.TugaLexicon.get_given_name_gender`.

The expected genders do not come from tugalex. The regnal names have the sex
of the rulers who bore them (Wikidata P21: Isabel I of Castile, Urraca of
León, Pius XII, Malcolm III of Scotland). The other names have the gender of
their Wikidata given-name item, and the names in
``scripts/given_name_overrides.csv`` have the evidence written in that file.
"""
import csv
import gzip
from pathlib import Path

import pytest

from tugalex import GIVEN_NAMES_PATH, TugaLexicon

OVERRIDES = Path(__file__).resolve().parent.parent / "scripts" / "given_name_overrides.csv"


@pytest.mark.parametrize("name,gender", [
    ("Maria", "f"), ("Isabel", "f"), ("Beatriz", "f"), ("Catarina", "f"),
    ("Leonor", "f"), ("Urraca", "f"), ("Inês", "f"), ("Joana", "f"),
    ("Afonso", "m"), ("Pedro", "m"), ("Sebastião", "m"), ("Clemente", "m"),
    ("Pio", "m"), ("Malcolm", "m"), ("João", "m"), ("Dinis", "m"),
    ("Darci", "mf"),
    # names whose Wikidata items mislead; see scripts/given_name_overrides.csv
    ("Rui", "m"), ("Simone", "f"), ("Elisabete", "f"),
])
def test_given_name_gender(name, gender):
    assert TugaLexicon.get_given_name_gender(name) == gender


@pytest.mark.parametrize("word", [
    "Raio", "Geração", "Sala", "Anexo", "século", "isabel", "joão", "Da", "Vi",
])
def test_word_that_is_not_a_listed_name(word):
    assert TugaLexicon.get_given_name_gender(word) is None


def test_data_file_is_sorted_unique_and_well_formed():
    with gzip.open(GIVEN_NAMES_PATH, "rt", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    names = [row["name"] for row in rows]
    assert names == sorted(set(names))
    assert {row["gender"] for row in rows} == {"m", "f", "mf"}
    assert all(len(name) >= 3 and name[0].isupper() and " " not in name for name in names)


def test_every_override_is_in_the_data_file():
    with OVERRIDES.open(encoding="utf-8", newline="") as f:
        overrides = list(csv.DictReader(f))
    assert overrides
    for row in overrides:
        assert row["reason"]
        assert TugaLexicon.get_given_name_gender(row["name"]) == row["gender"]
