"""The regional dictionary and its phoneme API warn before their removal.

The gender lookups and the AO1990 spelling tools are not deprecated, and
tugaphone calls them on every text it normalises, so they must stay silent.
"""
import warnings

import pytest

from tugalex import TugaLexicon
from tugalex.version import VERSION_MAJOR

REMOVAL = f"tugalex {VERSION_MAJOR + 1}.0.0"


@pytest.fixture(scope="module")
def lex():
    return TugaLexicon()


def _recorded(call):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        call()
    return caught


DEPRECATED = {
    "ipa": lambda lex: lex.ipa,
    "syllables": lambda lex: lex.syllables,
    "regions": lambda lex: lex.regions,
    "possible_postags": lambda lex: lex.possible_postags,
    "lang_to_region": lambda lex: lex.lang_to_region("pt-PT"),
    "get_phonemes": lambda lex: lex.get_phonemes("casa"),
    "get_syllables": lambda lex: lex.get_syllables("casa"),
    "get": lambda lex: lex.get("casa"),
    "get_wordlist": lambda lex: lex.get_wordlist(),
    "get_ipa_map": lambda lex: lex.get_ipa_map(),
}


@pytest.mark.parametrize("name", sorted(DEPRECATED))
def test_dictionary_api_warns_once_with_removal_version(lex, name):
    caught = _recorded(lambda: DEPRECATED[name](lex))
    deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert len(deprecations) == 1, [str(w.message) for w in deprecations]
    message = str(deprecations[0].message)
    assert message.startswith(f"TugaLexicon.{name} is deprecated")
    assert REMOVAL in message
    assert "tugaphone.dialects" in message
    # the warning points at the caller, not at tugalex
    assert deprecations[0].filename == __file__


def test_deprecated_api_still_answers(lex):
    with pytest.warns(DeprecationWarning):
        assert lex.get_syllables("casa") == ["ca", "sa"]
    with pytest.warns(DeprecationWarning):
        assert lex.get("casa")["syllables"] == ["ca", "sa"]


KEPT = {
    "constructor": lambda lex: TugaLexicon(),
    "get_noun_gender": lambda lex: TugaLexicon.get_noun_gender("casa"),
    "get_given_name_gender": lambda lex: TugaLexicon.get_given_name_gender("Isabel"),
    "AO1990": lambda lex: lex.AO1990,
    "silent_p_words": lambda lex: lex.silent_p_words,
    "voiced_u_words": lambda lex: lex.voiced_u_words,
    "normalize_ao1900": lambda lex: lex.normalize_ao1900("acção"),
    "reverse_ao1900_pt": lambda lex: lex.reverse_ao1900_pt("ação"),
    "reverse_ao1900_br": lambda lex: lex.reverse_ao1900_br("frequente"),
}


@pytest.mark.parametrize("name", sorted(KEPT))
def test_kept_api_is_silent(lex, name):
    assert _recorded(lambda: KEPT[name](lex)) == []
