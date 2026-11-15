"""The word list reads its own words-only file and is not deprecated."""
import importlib.util
import os
import warnings

import pytest

from tugalex import TugaLexicon

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICTIONARY = os.path.join(REPO_ROOT, "tugalex", "data", "regional_dict.csv.gz")
WORDS = os.path.join(REPO_ROOT, "tugalex", "data", "words.csv.gz")
REGIONS = ["dli", "lbx", "lda", "mpx", "rjx", "spx"]


@pytest.fixture(scope="module")
def build():
    spec = importlib.util.spec_from_file_location(
        "build_wordlist", os.path.join(REPO_ROOT, "scripts", "build_wordlist.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("region", REGIONS)
def test_wordlist_emits_no_deprecation_warning(region):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        words = TugaLexicon().get_wordlist(region)
    assert "casa" in words


def test_wordlist_does_not_read_the_regional_dictionary(monkeypatch):
    def refuse(path):
        raise AssertionError(f"get_wordlist read the regional dictionary {path}")

    monkeypatch.setattr(TugaLexicon, "_load_lang_map", staticmethod(refuse))
    lex = TugaLexicon(dictionary_path=os.path.join(REPO_ROOT, "missing.csv.gz"))
    lisbon, luanda = lex.get_wordlist("lbx"), lex.get_wordlist("lda")
    assert len(lisbon) == 53147
    assert len(luanda) == 53146
    # the regional dictionary lists aminoácido and arabescar for Lisbon and
    # not for Luanda, and reda for Luanda and not for Lisbon
    assert {"aminoácido", "arabescar"} <= set(lisbon)
    assert not {"aminoácido", "arabescar"} & set(luanda)
    assert "reda" in luanda and "reda" not in lisbon
    assert lex._ipa == {}


@pytest.mark.parametrize("region", REGIONS)
def test_wordlist_holds_the_words_of_the_regional_dictionary(region):
    _, syllables, _ = TugaLexicon._load_lang_map(DICTIONARY)
    assert TugaLexicon().get_wordlist(region) == sorted(syllables[region])


def test_words_file_is_the_build_output(build, tmp_path):
    out = tmp_path / "words.csv.gz"
    build.main(["--dictionary", DICTIONARY, "--out", str(out)])
    with open(WORDS, "rb") as shipped:
        assert out.read_bytes() == shipped.read()


def test_wordlist_returns_a_copy():
    lex = TugaLexicon()
    lex.get_wordlist("lbx").clear()
    assert len(lex.get_wordlist("lbx")) == 53147


def test_unknown_region_raises():
    with pytest.raises(ValueError, match="Unsupported dialect: xxx"):
        TugaLexicon().get_wordlist("xxx")
