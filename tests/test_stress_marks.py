"""Stress marks in the Lisbon (lbx) lexicon.

The Portal da Língua Portuguesa's Lisbon generator writes no stress mark when
a glide precedes the stressed vowel (paciente ``pɐ.sjẽ.tɨ``). tugaphone marks
an unmarked entry by counting orthographic syllables, which puts the stress
on the wrong syllable (paciente ``ˈpɐsjẽt``). The build corrects these rows
through ``scripts/regional_dict_errata.csv`` and refuses to write an lbx entry
without exactly one primary mark.
"""
import csv
import gzip
import importlib.util
import json
import os

import pytest

from tugalex import TugaLexicon

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIONS = ["lbx", "rjx", "spx", "lda", "mpx", "dli"]


@pytest.fixture(scope="module")
def lex():
    return TugaLexicon()


@pytest.fixture(scope="module")
def build():
    spec = importlib.util.spec_from_file_location(
        "build_regional_dict",
        os.path.join(REPO_ROOT, "scripts", "build_regional_dict.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_lbx_multisyllable_has_one_primary_mark(lex):
    syllables = lex.syllables["lbx"]
    offenders = {
        word: entry[""]
        for word, entry in lex.ipa["lbx"].items()
        if len([s for s in syllables[word] if s]) >= 2
        and any(reading.count("ˈ") != 1 for reading in entry[""].split("$$"))
    }
    assert not offenders, (
        f"{len(offenders)} lbx entries lack exactly one primary mark, "
        f"e.g. {sorted(offenders.items())[:5]}")


# these entries write the nasal e as e + U+0303, not the precomposed U+1EBD
@pytest.mark.parametrize("word, phones", [
    ("paciente", "pɐ·sjˈe\u0303t"),
    ("cliente", "kljˈe\u0303t"),
    ("ciência", "sjˈe\u0303·sjɐ"),
    ("tração", "tɾɐ·sˈɐ̃w"),
    ("texto", "tˈɐʃ·tu"),
    ("tatu", "ta·tˈu"),
    ("perpetuar", "pɨɾ·pˌɛ·twˈaɾ"),
])
def test_lbx_entry(lex, word, phones):
    assert lex.get_phonemes(word, region="lbx") == phones


def test_textos_is_not_a_lexicon_entry(lex):
    # The Portal lists lemmas only; plurals come from the caller's rules.
    assert lex.get_phonemes("textos", region="lbx") is None


@pytest.mark.parametrize("region", REGIONS)
def test_tracao_is_not_seleto(lex, region):
    phones = lex.get_phonemes("tração", region=region)
    assert phones.split("·")[-1].startswith("s"), phones
    assert "l" not in phones, phones


def _gold(path, rows):
    with open(path, "w", encoding="utf-8") as fh:
        for word, phones, syllables in rows:
            fh.write(json.dumps({"word": word, "region": "pt-PT-x-lisboa",
                                 "phones": phones, "syllables": syllables}) + "\n")


def _errata(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["word", "region_code", "source_phones", "phones", "source"])
        writer.writerows(rows)


def _built(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return {r["word"]: r["phones"] for r in
                csv.DictReader(line for line in fh if not line.startswith("#"))}


def test_build_refuses_unmarked_lbx_entry(build, tmp_path):
    _gold(tmp_path / "gold.jsonl", [("paciente", "pɐ|sjẽt", "pa|ci|en|te")])
    _errata(tmp_path / "errata.csv", [])
    with pytest.raises(SystemExit, match="lack exactly one primary mark"):
        build.main(["--gold", str(tmp_path / "gold.jsonl"),
                    "--out", str(tmp_path / "out.csv.gz"),
                    "--errata", str(tmp_path / "errata.csv")])


def test_build_applies_errata(build, tmp_path):
    _gold(tmp_path / "gold.jsonl", [
        ("paciente", "pɐ|sjẽt", "pa|ci|en|te"),
        ("tração", "sɨ|lˈɛ|tu", "tra|ção"),
        ("tração", "tɾɐ|sˈɐ̃w", "tra|ção"),
    ])
    _errata(tmp_path / "errata.csv", [
        ("paciente", "lbx", "pɐ|sjẽt", "pɐ|sjˈẽt", "rule+infopedia"),
        ("tração", "lbx", "sɨ|lˈɛ|tu", "", "drop"),
    ])
    build.main(["--gold", str(tmp_path / "gold.jsonl"),
                "--out", str(tmp_path / "out.csv.gz"),
                "--errata", str(tmp_path / "errata.csv")])
    assert _built(tmp_path / "out.csv.gz") == {
        "paciente": "pɐ|sjˈẽt", "tração": "tɾɐ|sˈɐ̃w"}


def test_build_refuses_errata_without_source_row(build, tmp_path):
    _gold(tmp_path / "gold.jsonl", [("paciente", "pɐ|sjˈẽt", "pa|ci|en|te")])
    _errata(tmp_path / "errata.csv", [
        ("paciente", "lbx", "pɐ|sjẽt", "pɐ|sjˈẽt", "rule+infopedia")])
    with pytest.raises(SystemExit, match="match no source row"):
        build.main(["--gold", str(tmp_path / "gold.jsonl"),
                    "--out", str(tmp_path / "out.csv.gz"),
                    "--errata", str(tmp_path / "errata.csv")])
