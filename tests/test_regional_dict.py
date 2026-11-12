"""The shipped regional dictionary and the lexicon revision it is built from."""
import gzip
import importlib.util
import io
import os

import pytest

from tugalex import TugaLexicon

pytestmark = pytest.mark.filterwarnings(r"ignore:TugaLexicon\.\w+ is deprecated:DeprecationWarning")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICTIONARY = os.path.join(REPO_ROOT, "tugalex", "data", "regional_dict.csv.gz")
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


def test_build_reads_the_cleaned_lexicon_revision(build):
    assert build.REVISION == "676e91fcb45280de9077ec0f895630a7de7b4a12"
    assert build.GOLD_URL.endswith(
        f"/resolve/{build.REVISION}/portuguese_pronunciation_lexicon.jsonl")


def test_shipped_dictionary_is_built_from_the_pinned_source(build):
    with gzip.open(DICTIONARY, "rt", encoding="utf-8") as fh:
        assert fh.readline() == f"# source sha256={build.SOURCE_SHA256}\n"


def test_build_refuses_a_download_with_another_sha256(build, tmp_path, monkeypatch):
    monkeypatch.setattr(build.urllib.request, "urlopen",
                        lambda url: io.BytesIO(b'{"word": "a"}\n'))
    with pytest.raises(SystemExit, match="expected " + build.SOURCE_SHA256):
        build.main(["--out", str(tmp_path / "out.csv.gz")])
    assert not (tmp_path / "out.csv.gz").exists()


@pytest.mark.parametrize("region", REGIONS)
def test_no_entry_has_an_empty_syllable(lex, region):
    offenders = {word: entry[""] for word, entry in lex.ipa[region].items()
                 if any(not s for r in entry[""].split("$$") for s in r.split("·"))}
    assert not offenders, sorted(offenders.items())[:5]


@pytest.mark.parametrize("region", REGIONS)
@pytest.mark.parametrize("word", ["birr", "rem", "microfarad", "microvolt"])
def test_unrepairable_word_has_no_entry(lex, word, region):
    assert lex.get_phonemes(word, region=region) is None


# nasal vowels are written decomposed: vowel + U+0303
@pytest.mark.parametrize("word, region, phones", [
    ("contrabordo", "lbx", "ko\u0303·tɾa·bˈɔɾ·du"),
    ("desbordo", "lbx", "dɨz·bˈɔɾ·du"),
    ("contrabordo", "spx", "ko\u0303·tɽa·bˈɔɽ·du"),
    ("abordagem", "spx", "a·boɾ·dˈa·ʒeɲ"),
    ("descolagem", "lbx", "dɨʃ·ku·lˈa·ʒɐ̃j"),
    ("data-valor", "lbx", "dˌa·tɐ·vɐ·lˈoɾ"),
    ("ciente", "lbx", "sjˈe\u0303t"),
])
def test_entry(lex, word, region, phones):
    assert lex.get_phonemes(word, region=region) == phones
