"""Tests for :class:`tugalex.TugaLexicon`.

These tests intentionally exercise only the small data files
(AO1990 PT/BR, homographs, archaisms). The phoneme/syllable maps live in a
~49 MB CSV and are loaded lazily; covering them is left to an opt-in heavy test.
"""
import pytest

from tugalex import TugaLexicon

# exercises the deprecated dictionary API; tests/test_deprecation.py covers the warning
pytestmark = pytest.mark.filterwarnings(r"ignore:TugaLexicon\.\w+ is deprecated:DeprecationWarning")


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


class TestLookupNormalization:
    def test_get_syllables_is_case_insensitive(self, lex):
        assert lex.syllables["lbx"]["casa"] == ["ca", "sa"]
        assert lex.get_syllables("  Casa ") == ["ca", "sa"]

    def test_get_returns_syllables_for_capitalized_word(self, lex):
        assert lex.get("Acordo", pos="NOUN") == lex.get("acordo", pos="NOUN")
        assert lex.get("Acordo")["syllables"] == ["a", "cor", "do"]

    def test_unknown_region_raises_value_error_everywhere(self, lex):
        with pytest.raises(ValueError):
            lex.get_phonemes("casa", region="xx")
        with pytest.raises(ValueError):
            lex.get_phonemes("para", pos="ADP", region="xx")
        with pytest.raises(ValueError):
            lex.get_syllables("casa", region="xx")
        with pytest.raises(ValueError):
            lex.get("casa", region="xx")


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


class TestModernSpelling:
    @pytest.mark.parametrize("word,lang,expected", [
        ("pharmacia", "pt-PT", "farmácia"),
        ("acção", "pt-PT", "ação"),
        ("vôo", "pt-BR", "voo"),
        ("lingüiça", "pt-BR", "linguiça"),
        ("recepção", "pt-PT", "receção"),
        ("idéia", "pt-BR", "ideia"),
        ("chronico", "pt-PT", "crónico"),
        ("chronico", "pt-BR", "crônico"),
        ("commodo", "pt-BR-x-sp", "cômodo"),
        ("phenomeno", "pt-AO", "fenómeno"),
    ])
    def test_modernises(self, lex, word, lang, expected):
        assert lex.modern_spelling(word, lang) == expected

    @pytest.mark.parametrize("word,expected", [
        ("Acção", "Ação"),
        ("ACÇÃO", "AÇÃO"),
        ("Pharmacia", "Farmácia"),
    ])
    def test_keeps_case(self, lex, word, expected):
        assert lex.modern_spelling(word) == expected

    @pytest.mark.parametrize("word", ["casa", "acupunctura", "acupuntura", "facto", "Lisboa", "A", ""])
    def test_valid_spelling_unchanged(self, lex, word):
        assert lex.modern_spelling(word) == word

    @pytest.mark.parametrize("word,lang,expected", [
        ("liqüefato", "pt-BR", "liquefato"),
        ("onilíngüe", "pt-BR", "onilingue"),
        ("electropunctura", "pt-PT", "eletropunctura"),
    ])
    def test_several_forms_take_the_closest(self, lex, word, lang, expected):
        assert lex.modern_spelling(word, lang) == expected

    def test_keeps_the_case_of_the_table(self, lex):
        assert lex.modern_spelling("arco-de-deus") == "arco de Deus"

    @pytest.mark.parametrize("word,lang,expected", [
        ("equinóides", "pt-PT", "equinoides"),
        ("eqüídeos", "pt-BR", "equídeos"),
        ("Eqüídeos", "pt-BR", "Equídeos"),
    ])
    def test_first_letter_follows_the_written_word(self, lex, word, lang, expected):
        assert lex.modern_spelling(word, lang) == expected

    @pytest.mark.parametrize("lang", ["pt_BR.UTF-8", "pt_BR@euro"])
    def test_posix_locale_strings(self, lex, lang):
        assert lex.modern_spelling("chronico", lang) == "crônico"

    @pytest.mark.parametrize("lang", ["pt_BR", "pt-Latn-BR", "PT-BR", "pt-BR-x-rj"])
    def test_brazilian_tags(self, lex, lang):
        assert lex.modern_spelling("chronico", lang) == "crônico"

    def test_archaism_target_is_accented(self, lex):
        assert lex.modern_spelling("parochia") == "paróquia"

    def test_each_variety_uses_its_own_table(self, lex):
        # recepção is the AO1990 pt-BR spelling and a pre-AO1990 pt-PT spelling.
        assert lex.modern_spelling("recepção", "pt-BR") == "recepção"
        assert lex.modern_spelling("lingüiça", "pt-PT") == "lingüiça"

    def test_brazilian_form_only_where_accent_differs(self, lex):
        differ = {old for old in lex.archaic_words if lex.archaic_words[old] != lex.archaic_words_br[old]}
        assert differ == {"chronico", "chronometro", "kilometro", "photometro", "pseudonymo",
                          "thermometro", "phenomeno", "anonymo", "chronica", "commodo"}


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

    def test_header_row_is_not_an_entry(self, lex):
        assert "old_form" not in lex.ao_pt
        assert "old_form" not in lex.ao_br

    def test_every_old_form_of_a_row_maps_to_its_new_forms(self, lex):
        # "liquefacção, liquefação, liqüefacção, liqüefação","liquefação, liquefacção"
        for old in ("liquefacção", "liquefação", "liqüefacção", "liqüefação"):
            assert lex.ao_br[old] == ["liquefação", "liquefacção"]
        # "alcaguete, alcagüete",alcaguete
        assert lex.ao_br["alcagüete"] == ["alcaguete"]
        assert lex.normalize_ao1900("alcaguete alcagüete") == "alcaguete alcaguete"

    def test_new_br_forms_carry_no_trema(self, lex):
        # AO1990 abolished the trema, so no new spelling keeps a ü.
        with_trema = {old: news for old, news in lex.ao_br.items()
                      if any("ü" in n for n in news)}
        assert with_trema == {}


class TestPhenomena:
    def test_silent_p_words(self, lex):
        words = lex.silent_p_words
        assert isinstance(words, set)
        assert len(words) > 0

    def test_voiced_u_words(self, lex):
        words = lex.voiced_u_words
        assert isinstance(words, set)
        assert len(words) > 0
