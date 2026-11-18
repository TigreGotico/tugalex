"""Tests for :class:`tugalex.TugaLexicon`.

These tests intentionally exercise only the small data files
(AO1990 PT/BR, homographs, archaisms). The phoneme/syllable maps live in a
~49 MB CSV and are loaded lazily; covering them is left to an opt-in heavy test.
"""
import csv
import re

import pytest

from tugalex import TugaLexicon

# exercises the deprecated dictionary and spelling API; tests/test_deprecation.py covers the warnings
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

    def test_gosto_verb_ends_in_its_vowel(self, lex):
        # Infopédia, "gosto": noun [ˈgoʃtu], verb (1sg of gostar) [ˈgɔʃtu], as
        # extracted in bifonia/data/infopedia_pt.csv.
        assert lex.homographs["gosto"] == {"NOUN": "ˈɡoʃtu", "VERB": "ˈɡɔʃtu"}

    def test_get_phonemes_verb_variant_not_none(self, lex):
        # The CRLF bug made the VERB lookup return None.
        assert lex.get_phonemes("para", pos="VERB") is not None


class TestArchaisms:
    def test_archaic_resolution(self, lex):
        assert lex.archaic_words["architecto"] == "arquiteto"

    @pytest.mark.parametrize("word", ["chyme", "thesouroso", "thymia"])
    def test_no_row_without_a_portuguese_word(self, lex, word):
        # chyme and thymia are not Portuguese spellings: the noun is quimo,
        # and -timia is only a combining element. Priberam has no tesouroso.
        assert word not in lex.archaic_words
        assert lex.modern_spelling(word) == word

    @pytest.mark.parametrize("archaic,modern", [
        ("della", "dela"),
        ("nella", "nela"),
        ("daquelle", "daquele"),
        ("naquelle", "naquele"),
        ("dalli", "dali"),
        ("fallava", "falava"),
        ("fallando", "falando"),
        ("appareça", "apareça"),
        ("attrahiu", "atraiu"),
        ("offendeis", "ofendeis"),
        ("collecção", "coleção"),
    ])
    def test_inflected_pre_1911_forms(self, lex, archaic, modern):
        # The modern forms are the Priberam entries: "dela", contraction of de and ela;
        # "falava", imperfect of falar; "colecção", AO1990 spelling coleção.
        assert lex.archaic_words[archaic] == modern
        assert lex.modern_spelling(archaic) == modern

    @pytest.mark.parametrize("archaic,modern", [
        ("Affonso", "Afonso"),
        ("Thereza", "Teresa"),
        ("Accacio", "Acácio"),
    ])
    def test_given_names_keep_the_capital(self, lex, archaic, modern):
        # The IRN list of admitted given names has Afonso (Afonso Henriques). Priberam gives
        # "Teresa, antropónimo" and "Acácio, antropónimo" as the origin of teresa and acácio.
        assert lex.modern_spelling(archaic) == modern

    @pytest.mark.parametrize("word", ["infecciona", "accionistas", "optimo", "caracteristica"])
    def test_pre_ao1990_spelling_is_not_an_archaism(self, lex, word):
        # infecciona and accionistas are the 1945 spellings; optimo and caracteristica
        # lack only the accent of óptimo and característica.
        assert word not in lex.archaic_words

    @pytest.mark.parametrize("word", ["emmudecer", "ennegrecer", "scisma", "scintilava"])
    def test_1911_spelling_is_not_an_archaism(self, lex, word):
        # The 1911 Formulário keeps mm and nn where pronounced (Base VII: emmalar, ennegrecer)
        # and the initial sc of scisma and scintilar (Base XI).
        assert word not in lex.archaic_words

    @pytest.mark.parametrize("word", ["kilo", "kilos", "kilolitro"])
    def test_1911_kilo_is_not_an_archaism(self, lex, word):
        """The 1911 Formulário, Base I, exception 2.ª, keeps K "na forma international
        kilo, que todavia se poderá escrever quilo". So kilo, kilos and kilolitro are
        1911 spellings. VOP lemma 131442 still lists kilo: "kilo - nome masculino ...
        variante de: quilo. Nota: Embora atestada em pelo menos uma fonte de referência
        lexicográfica, esta grafia não está de acordo com o recomendado na legislação e
        usado pela comunidade científica, quilo"."""
        assert word not in lex.archaic_words

    def test_1911_kilo_keeps_the_double_m_row(self, lex):
        """Base VII of the 1911 Formulário: "Nenhuma consoante se duplicará no interior ou
        fim de vocábulo, senão quando a pronunciação assim o exija". The mm of kilogramma
        is not pronounced double, so the 1911 form has one m, and kilogramma is a
        pre-1911 form. The note names both changes to the modern quilograma."""
        assert lex.archaic_words["kilogramma"] == "quilograma"
        with open(lex.archaisms_path, encoding="utf-8", newline="") as f:
            notes = {row["archaic"]: row["notes"] for row in csv.DictReader(f)}
        assert notes["kilogramma"] == "k→qu + mm→m"

    @pytest.mark.parametrize("archaic,modern", [("sciencia", "ciência"), ("kilometro", "quilómetro")])
    def test_unaccented_pre_1911_form_stays(self, lex, archaic, modern):
        """Before 1911 these words had no accent. 1911 writes sciência (Base XI prints it:
        "scena, sciência, scetro") and kilómetro (Base XXVI: "Todos os vocábulos cuja
        sílaba predominante seja a antepenúltima terão essa sílaba marcada com o
        competente acento escrito"). So the unaccented forms are pre-1911 spellings."""
        assert lex.archaic_words[archaic] == modern

    def test_1911_initial_sc_is_not_an_archaism(self, lex):
        """The 1911 Formulário, Base XI: "É conservado o grupo inicial sc, das seguintes
        palavras e seus derivados e afins, em que o s é mudo: scena, sciência, scetro,
        scéptico, scisma, scisão, sciático, scintilar, scelerado". scena is the 1911 form."""
        assert "scena" not in lex.archaic_words

    def test_identical_spelling_is_not_an_archaism(self, lex):
        """inflexão is the current pt-PT spelling: VOP lemma 124692 "inflexão - nome
        feminino", and Priberam "inflexão ... nome feminino"."""
        assert "inflexão" not in lex.archaic_words

    @pytest.mark.parametrize("word", ["kermesse", "ritornello"])
    def test_current_loanword_is_not_an_archaism(self, lex, word):
        """A modern pt-PT text can still write these loanwords. VOP lemma 49589:
        "ritornello ... estrangeirismo; língua de origem: italiano - forma adaptada:
        ritornelo". The VOP lacks kermesse, and Priberam has "kermesse ... nome feminino.
        O mesmo que quermesse. Origem: palavra francesa"."""
        assert word not in lex.archaic_words

    @pytest.mark.parametrize("word", ["homme", "caballo", "balza"])
    def test_foreign_word_is_not_an_archaism(self, lex, word):
        """Neither the VOP nor Priberam holds these words. homme is French: the 14 books
        have it only in a Musset line ("Et l'homme doit mourir où commence le Dieu",
        Gutenberg 23400) and in "ci-devant jeun'homme" (Gutenberg 24401). balza occurs
        only in an Italian aria ("Pieno d'amor / Mi balza il cor", Gutenberg 23400).
        caballo is Spanish and occurs in none of the books; the pre-1911 Portuguese
        form is the row cavallo."""
        assert word not in lex.archaic_words
        assert lex.modern_spelling(word) == word

    def test_pre_1911_ue_verb_form_stays(self, lex):
        """attribue is the pre-1911 Portuguese spelling of atribui. Base VII of the 1911
        Formulário writes atribuir with one t, and Base XIII abolishes ue for the
        diphthong ui "quer em nomes, quer em formas verbais". Os Maias (Gutenberg 40409)
        has "como quem attribue tudo á malicia dos Destinos"."""
        assert lex.archaic_words["attribue"] == "atribui"

    @pytest.mark.parametrize("word", ["profetiza", "tenue", "terreo", "ignez", "brizas"])
    def test_current_word_is_not_an_archaism(self, lex, word):
        # Priberam has profetiza (profetizar), ténue, térreo and briza; the IRN list admits Ignez.
        assert word not in lex.archaic_words

    @pytest.mark.parametrize("word", ["apparecerão", "assignarão", "cahirão", "sahião"])
    def test_homograph_is_not_an_archaism(self, lex, word):
        # Before 1911, -rão wrote both the future and the preterite: pg22044 has apparecerão
        # for apareceram. sahião there is the imperfect saíam, not the noun saião.
        assert word not in lex.archaic_words

    @pytest.mark.parametrize("archaic,modern", [("pélla", "pela"), ("pêllo", "pelo")])
    def test_modern_form_is_the_ao1990_form(self, lex, archaic, modern):
        # The tugalex AO1990 table maps péla to pela and pêlo to pelo.
        assert lex.archaic_words[archaic] == modern

    def test_dual_spelling_keeps_the_consonant(self, lex):
        # Priberam: pt-PT writes característica or caraterística after AO1990; the c form is written.
        assert lex.archaic_words["characteristica"] == "característica"
        assert lex.modern_spelling("characterizar") == "caracterizar"
        assert lex.archaic_words["ithericia"] == "icterícia"

    @pytest.mark.parametrize("archaic", ["comsigo", "comtigo", "comquanto", "emquanto", "emfim", "bemdito"])
    def test_pre_1911_m_before_consonant(self, lex, archaic):
        """The 1911 Formulário, Base XV: "No interior dos vocábulos é a nasalidade da vogal
        expressa por m antes de b, p, m, e por n em qualquer outra situação, [...] assim
        escreveremos circunstância, circunscrever, conquanto, com n, e não com m". The
        modern form is the key with that m written n, in pt-PT and in pt-BR."""
        modern = re.sub(r"(?<=[aeiou])m(?=[^aeioubpm])", "n", archaic)
        assert modern != archaic
        assert lex.archaic_words[archaic] == modern
        assert lex.modern_spelling(archaic) == modern
        assert lex.modern_spelling(archaic, "pt-BR") == modern

    def test_base_xv_example_words(self, lex):
        # Base XV prints circunstância and conquanto; the VOP lists consigo and enquanto.
        assert "comsigo" in lex.archaic_words
        assert lex.modern_spelling("comsigo") == "consigo"
        assert lex.modern_spelling("emquanto") == "enquanto"
        assert lex.modern_spelling("comquanto") == "conquanto"
        assert lex.modern_spelling("circumstancia") == "circunstância"

    @pytest.mark.parametrize("word", ["comprar", "embora", "amnistia"])
    def test_m_that_base_xv_keeps_is_not_an_archaism(self, lex, word):
        """Base XV keeps m before b and p (comprar, embora). The m of amnistia marks no
        nasal vowel, so Base XV does not apply; the VOP writes amnistia."""
        assert word not in lex.archaic_words
        assert lex.modern_spelling(word) == word

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
        ("Egypto", "pt-PT", "Egito"),
        ("Egipto", "pt-PT", "Egito"),
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

    def test_brazilian_form_only_where_accent_or_ao1990_consonant_differs(self, lex):
        # The pt-BR forms are the Priberam "Grafia no Brasil" notes: pt-BR writes ê/ô where
        # pt-PT writes é/ó (crónico, crônico) and keeps a c/p that AO1990 dropped in pt-PT
        # (aceção, acepção). Priberam gives conosco and indenizar for connosco and indemnizar.
        expected = {
            "accepção": "acepção", "anonyma": "anônima", "anonymas": "anônimas",
            "anonymo": "anônimo", "anonymos": "anônimos", "architectonica": "arquitetônica",
            "architectonico": "arquitetônico", "attonita": "atônita", "attonito": "atônito",
            "attonitos": "atônitos", "authomato": "autômato", "babylonicos": "babilônicos",
            "blasphemia": "blasfêmia", "blasphemias": "blasfêmias", "bohemia": "boêmia",
            "bohemias": "boêmias", "bohemio": "boêmio", "character": "caráter",
            "chronica": "crônica", "chronicas": "crônicas", "chronico": "crônico",
            "chronometro": "cronômetro", "commoda": "cômoda", "commodas": "cômodas",
            "commodo": "cômodo", "commodos": "cômodos", "comnosco": "conosco",
            "conjecturaes": "conjecturais", "decennio": "decênio", "ephemera": "efêmera",
            "ephemeras": "efêmeras", "ephemero": "efêmero", "ephemeros": "efêmeros",
            "euphonicos": "eufônicos", "excepcionaes": "excepcionais", "hellenica": "helênica",
            "homonymo": "homônimo", "hygienica": "higiênica", "hygienicas": "higiênicas",
            "hygienicos": "higiênicos", "incommodo": "incômodo", "incommodos": "incômodos",
            "incommódo": "incômodo", "incómmodo": "incômodo", "indemnisar": "indenizar",
            "indemnisação": "indenização", "insomnia": "insônia", "insomnias": "insônias",
            "jeronymo": "jerônimo", "kilometro": "quilômetro", "millenio": "milênio",
            "omnibus": "ônibus", "phenix": "fênix", "phenomeno": "fenômeno",
            "phenomenos": "fenômenos", "philarmonica": "filarmônica",
            "philarmonicas": "filarmônicas", "photometro": "fotômetro", "poney": "pônei",
            "pseudonymo": "pseudônimo", "synonimos": "sinônimos", "synonymas": "sinônimas",
            "synonymos": "sinônimos", "thermometro": "termômetro", "theutonicos": "teutônicos",
        }
        differ = {old: lex.archaic_words_br[old] for old in lex.archaic_words
                  if lex.archaic_words[old] != lex.archaic_words_br[old]}
        assert differ == expected
        by_letter = {"comnosco", "indemnisar", "indemnisação"}
        silent = re.compile(r"(?<=[aeiouáéíóú])[cp](?=[tcç])")
        for old in differ.keys() - by_letter:
            pt, br = lex.archaic_words[old], differ[old]
            assert silent.sub("", br.translate(str.maketrans("êô", "éó"))) == silent.sub("", pt), old
        assert lex.modern_spelling("chronicas", "pt-BR") == "crônicas"
        assert lex.modern_spelling("accepção", "pt-BR") == "acepção"

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

    @pytest.mark.parametrize("old,new", [
        ("correcta", ["correta"]),
        ("correctas", ["corretas"]),
        ("colectivas", ["coletivas"]),
        ("eléctricas", ["elétricas"]),
        ("nocturna", ["noturna"]),
    ])
    def test_inflections_drop_the_consonant_of_their_lemma(self, lex, old, new):
        """VOP (papers/linguistics/pt/vop-tugalex-ao/): lemma 88481 "correto - adjetivo",
        forms correto correta corretos corretas; lemma 108409 "coletivo", variante AO :
        colectivo ( Brasil); lemma 1480 "elétrico", variante AO : eléctrico ( Brasil);
        lemma 117865 "noturno", forms noturno noturna. Priberam: correta "feminino
        singular de correcto correto", coletivas "feminino plural de colectivo coletivo"."""
        assert lex.ao_pt[old] == new

    def test_inflection_of_a_dual_cell_keeps_both_forms(self, lex):
        """VOP lemma 121101 "setorial - adjetivo", forms setorial setoriais, "variante AO
        de : sectorial", a pair valid in Portugal (Base IV 1º c). Priberam, setoriais:
        "masculino e feminino plural de sectorial setorial"."""
        assert lex.ao_pt["sectorial"] == ["sectorial", "setorial"]
        assert lex.ao_pt["sectoriais"] == ["sectoriais", "setoriais"]
        assert lex.modern_spelling("sectoriais") == "sectoriais"

    def test_vop_single_spelling_wins_over_priberam_dual(self, lex):
        """VOP lemma 91422 "infecioso - adjetivo", forms infecioso infeciosa, "variante
        AO : infeccioso ( Brasil)": the c form is valid in Brazil only. Priberam gives
        the pt-PT header "infeccioso ou infecioso"; the VOP comes first."""
        assert lex.ao_pt["infecciosa"] == ["infeciosa"]

    def test_vop_dual_spelling_wins_over_priberam_single(self, lex):
        """VOP lemma 78024 "retal - adjetivo", forms retal retais, "variante AO :
        rectal", a pair valid in Portugal. Priberam, retais: "Grafia alterada pelo
        Acordo Ortográfico de 1990: retal"; the VOP comes first."""
        assert lex.ao_pt["rectais"] == ["retais", "rectais"]

    def test_brazil_only_variant_is_no_pt_pt_spelling(self, lex):
        """VOP lemma 107241 "bissetor - adjetivo", forms bissetor bissetriz bissetores
        bissetrizes, "variante AO : bissector ( Brasil)"; lemma 25915 "bissector -
        adjetivo" carries the label Brasil. pt-PT writes bissetor only (Base IV 1º b).
        Priberam gives the pt-PT header "bissetor ou bissector"; the VOP comes first."""
        assert lex.ao_pt["bissector"] == ["bissetor"]
        assert lex.ao_pt["bissectores"] == ["bissetores"]
        assert lex.modern_spelling("bissector") == "bissetor"

    def test_pair_valid_in_portugal_keeps_both_forms(self, lex):
        """VOP lemma 191936 "perfetibilidade - nome feminino", forms perfetibilidade
        perfetibilidades, "variante AO : perfectibilidade", with no Brasil tag; lemma
        14837 "perfectibilidade" has no label (Base IV 1º c). Priberam, pt-PT: "Dupla
        grafia pelo Acordo Ortográfico de 1990: perfetibilidade"."""
        assert lex.ao_pt["perfectibilidade"] == ["perfetibilidade", "perfectibilidade"]
        assert lex.ao_pt["perfectibilidades"] == ["perfetibilidades", "perfectibilidades"]
        assert lex.modern_spelling("perfectibilidade") == "perfectibilidade"

    def test_feminine_that_is_another_word_is_not_listed(self, lex):
        """Priberam, tetas: "feminino plural de teta", so tetas is no feminine of teto."""
        assert "tectas" not in lex.ao_pt

    @pytest.mark.parametrize("old", ["contracta", "contractas", "contractos", "retractos"])
    def test_dual_inflection_whose_bare_form_is_another_word_is_not_listed(self, lex, old):
        """A dual cell makes a converter write the full form for every bare form it meets.
        Priberam reads contrata and contratas as forms of contratar, contratos also as the
        noun contrato, and retratos as the noun retrato (papers/linguistics/pt/
        priberam_contrata.html, _contratas, _contratos, _retratos)."""
        assert old not in lex.ao_pt

    @pytest.mark.parametrize("old", ["tractos", "edictais", "correctores"])
    def test_inflection_whose_new_form_is_another_noun_is_not_listed(self, lex, old):
        """The AO1990 form is also a noun that never had the consonant, so a reverse
        conversion would write "maus tractos". Priberam entries: tratos, "trato" beside
        "tracto"; editais, "edital" beside "edictal"; corretores, "corretor" beside
        "corrector" (papers/linguistics/pt/priberam_tratos.html, _editais, _corretoras)."""
        assert old not in lex.ao_pt

    def test_inflection_with_a_rare_verb_reading_is_listed(self, lex):
        """VOP lemma 92989 "ator - nome masculino", forms ator atores. Priberam reads atores
        only as a form of atorar, a rare verb; the frequent noun reading keeps the row."""
        assert lex.ao_pt["actores"] == ["atores"]

    def test_modern_spelling_of_an_inflection(self, lex):
        """VOP lemma 88481 "correto - adjetivo", forms correto correta corretos corretas."""
        assert lex.modern_spelling("Correctas") == "Corretas"


class TestPhenomena:
    def test_silent_p_words(self, lex):
        words = lex.silent_p_words
        assert isinstance(words, set)
        assert len(words) > 0

    def test_voiced_u_words(self, lex):
        words = lex.voiced_u_words
        assert isinstance(words, set)
        assert len(words) > 0
