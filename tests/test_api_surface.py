"""tugalex holds the word list, the gender lookups and the homograph table, and nothing else."""
from pathlib import Path

import pytest

import tugalex
from tugalex import TugaLexicon

DATA = Path(tugalex.__file__).parent / "data"


def test_public_names_of_the_class():
    public = {name for name in dir(TugaLexicon) if not name.startswith("_")}
    assert public == {"get_wordlist", "get_noun_gender", "get_given_name_gender"}


def test_public_attributes_of_an_instance():
    public = {name for name in vars(TugaLexicon()) if not name.startswith("_")}
    assert public == {"homographs", "homographs_path"}


def test_public_names_of_the_module():
    public = {name for name in vars(tugalex) if not name.startswith("_")
              and getattr(vars(tugalex)[name], "__module__", "tugalex") == "tugalex"}
    assert public >= {"TugaLexicon", "suffix_noun_gender", "NOUN_GENDER_SUFFIXES",
                      "NOUN_GENDER_PATH", "GIVEN_NAMES_PATH", "WORDLIST_PATH"}
    for removed in ("REGIONAL_DICT_PATH", "DICTIONARY_REMOVAL_VERSION", "SPELLING_REMOVAL_VERSION",
                    "IPA_MAP", "SYLLABLE_MAP", "WORD_REPLACEMENT_MAP"):
        assert not hasattr(tugalex, removed), removed


def test_constructor_takes_no_dictionary_path():
    with pytest.raises(TypeError):
        TugaLexicon(dictionary_path="dict.csv")


def test_packaged_data_files():
    assert sorted(p.name for p in DATA.iterdir() if p.is_file()) == [
        "given_names.csv.gz", "heterophonic_homographs.csv",
        "noun_gender_exceptions.csv.gz", "words.csv.gz",
    ]
