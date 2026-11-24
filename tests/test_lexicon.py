"""The heterophonic homograph table of :class:`tugalex.TugaLexicon`."""
import warnings

import pytest

from tugalex import TugaLexicon


@pytest.fixture(scope="module")
def lex():
    return TugaLexicon()


class TestHomographs:
    def test_homograph_loaded_with_clean_keys(self, lex):
        # Regression: CRLF line endings left a trailing '\r' on the POS key
        # (e.g. 'VERB\r'), so the second variant was unreachable.
        entry = lex.homographs["para"]
        assert set(entry) == {"ADP", "VERB"}

    def test_para_distinguishes_pos(self, lex):
        assert lex.homographs["para"] == {"ADP": "ˈpɐɾɐ", "VERB": "ˈpaɾɐ"}

    def test_gosto_verb_ends_in_its_vowel(self, lex):
        # Infopédia, "gosto": noun [ˈgoʃtu], verb (1sg of gostar) [ˈgɔʃtu], as
        # extracted in bifonia/data/infopedia_pt.csv.
        assert lex.homographs["gosto"] == {"NOUN": "ˈɡoʃtu", "VERB": "ˈɡɔʃtu"}

    def test_table_size(self, lex):
        # heterophonic_homographs.csv: 27 words, 55 word,pos,ipa rows
        with open(lex.homographs_path, encoding="utf-8") as f:
            rows = [line for line in f.read().split("\n")[1:] if line.strip()]
        assert len(rows) == 55
        assert len(lex.homographs) == 27
        assert sum(len(tags) for tags in lex.homographs.values()) == 55

    def test_construction_is_silent(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            TugaLexicon()
