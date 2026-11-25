"""The word list reads its own words-only file and stays silent."""
import gzip
import importlib.util
import os
import warnings

import pytest

from tugalex import TugaLexicon

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIONS = ["dli", "lbx", "lda", "mpx", "rjx", "spx"]


@pytest.fixture(scope="module")
def build():
    spec = importlib.util.spec_from_file_location(
        "build_wordlist", os.path.join(REPO_ROOT, "scripts", "build_wordlist.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("region", REGIONS)
def test_wordlist_emits_no_warning(region):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        words = TugaLexicon().get_wordlist(region)
    assert "casa" in words


def test_wordlist_holds_the_regional_differences():
    lex = TugaLexicon()
    lisbon, luanda = lex.get_wordlist("lbx"), lex.get_wordlist("lda")
    assert len(lisbon) == 53147
    assert len(luanda) == 53146
    assert lisbon == sorted(lisbon)
    # the regional dictionary lists aminoácido and arabescar for Lisbon and
    # not for Luanda, and reda for Luanda and not for Lisbon
    assert set(lisbon) ^ set(luanda) == {"aminoácido", "arabescar", "reda"}
    assert "reda" in luanda and "reda" not in lisbon


@pytest.mark.parametrize("name,opener", [("dict.csv", open), ("dict.csv.gz", gzip.open)])
def test_build_writes_each_word_with_its_regions(build, tmp_path, name, opener):
    source = tmp_path / name
    with opener(source, "wt", encoding="utf-8") as f:
        f.write("# provenance header\n"
                "word,phones,syllables,region_code\n"
                " Zebra ,zˈe|bɾɐ,ze|bra,LBX\n"
                "zebra,zˈe|bɾa,ze|bra,rjx\n"
                "abelha,ɐ|bˈɐ|ʎɐ,a|be|lha,lbx\n"
                "abelha,ɐ|bˈɐ|ʎɐ,a|be|lha,lbx\n"
                "curto,row\n")
    out = tmp_path / "words.csv.gz"
    build.main(["--dictionary", str(source), "--out", str(out)])
    with gzip.open(out, "rt", encoding="utf-8") as f:
        assert f.read() == "word,regions\nabelha,lbx\nzebra,lbx rjx\n"


def test_build_needs_a_dictionary(build, capsys):
    with pytest.raises(SystemExit):
        build.main([])
    assert "--dictionary" in capsys.readouterr().err


def test_wordlist_returns_a_copy():
    lex = TugaLexicon()
    lex.get_wordlist("lbx").clear()
    assert len(lex.get_wordlist("lbx")) == 53147


def test_unknown_region_raises():
    with pytest.raises(ValueError, match="Unsupported dialect: xxx"):
        TugaLexicon().get_wordlist("xxx")
