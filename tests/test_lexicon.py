"""Tests for :class:`tugalex.TugaLexicon`.

These tests intentionally exercise only the small data files
(AO1990 PT/BR, homographs, archaisms). The phoneme/syllable maps live in a
~49 MB CSV and are loaded lazily; covering them is left to an opt-in heavy test.
"""
import pytest

from tugalex import TugaLexicon


@pytest.fixture(scope="module")
def lex():
    return TugaLexicon()


class TestDialectMapping:
    def test_known_dialects(self, lex):
        assert lex.lang_to_region("pt-PT") == "lbx"
        assert lex.lang_to_region("pt-BR") == "rjx"
        assert lex.lang_to_region("pt-AO") == "lda"
        assert lex.lang_to_region("pt-MZ") == "mpx"
        assert lex.lang_to_region("pt-TL") == "dli"

    def test_unknown_dialect_raises(self, lex):
        with pytest.raises(ValueError):
            lex.lang_to_region("en-US")


class TestHomographs:
    def test_homograph_loaded_with_clean_keys(self, lex):
        # Regression: CRLF line endings left a trailing '\r' on the POS key
        # (e.g. 'VERB\r'), so the second variant was unreachable.
        entry = lex.homographs["para"]
        assert set(entry) == {"ADP", "VERB"}

    def test_get_phonemes_distinguishes_pos(self, lex):
        adp = lex.get_phonemes("para", pos="ADP")
        verb = lex.get_phonemes("para", pos="VERB")
        assert adp and verb
        assert adp != verb

    def test_get_phonemes_verb_variant_not_none(self, lex):
        # The CRLF bug made the VERB lookup return None.
        assert lex.get_phonemes("para", pos="VERB") is not None


class TestArchaisms:
    def test_archaic_resolution(self, lex):
        assert lex.archaic_words["architecto"] == "arquiteto"

    def test_archaic_values_have_no_trailing_whitespace(self, lex):
        for old, new in lex.archaic_words.items():
            assert old == old.strip()
            assert new == new.strip()


class TestAO1990:
    def test_normalize(self, lex):
        assert lex.normalize_ao1900("acção óptimo") == "ação ótimo"

    def test_ao_values_are_clean(self, lex):
        # Each new form must be a clean single token (no '\r', no surrounding space).
        for old, news in lex.AO1990.items():
            for n in news:
                assert n == n.strip()

    def test_reverse_pt_round_trip(self, lex):
        modern = lex.normalize_ao1900("acção")
        assert lex.reverse_ao1900_pt(modern) == "acção"

    def test_unknown_word_passthrough(self, lex):
        assert lex.normalize_ao1900("casa") == "casa"


class TestPhenomena:
    def test_silent_p_words(self, lex):
        words = lex.silent_p_words
        assert isinstance(words, set)
        assert len(words) > 0

    def test_voiced_u_words(self, lex):
        words = lex.voiced_u_words
        assert isinstance(words, set)
        assert len(words) > 0
