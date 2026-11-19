"""The regional dictionary and the spelling accessors warn before their removal.

The regional dictionary and its phoneme API go away with the dictionary.
desacordo_ortografico owns the spelling table, so the archaism and AO1990
accessors return the frozen tugalex tables until their removal. The word list
and the gender lookups are not deprecated: desacordo_ortografico reads the word
list and text2spoken reads the gender lookups, so they must stay silent.
"""
import hashlib
import importlib
import warnings
from pathlib import Path

import pytest

import tugalex
import tugalex.version
from tugalex import TugaLexicon
from tugalex.version import VERSION_MAJOR

REMOVAL = f"tugalex {VERSION_MAJOR + 1}.0.0"
DATA = Path(tugalex.__file__).parent / "data"


@pytest.fixture(scope="module")
def lex():
    return TugaLexicon()


def _recorded(call):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        call()
    return [w for w in caught if issubclass(w.category, DeprecationWarning)]


DICTIONARY = {
    "ipa": lambda lex: lex.ipa,
    "syllables": lambda lex: lex.syllables,
    "regions": lambda lex: lex.regions,
    "possible_postags": lambda lex: lex.possible_postags,
    "lang_to_region": lambda lex: lex.lang_to_region("pt-PT"),
    "get_phonemes": lambda lex: lex.get_phonemes("casa"),
    "get_syllables": lambda lex: lex.get_syllables("casa"),
    "get": lambda lex: lex.get("casa"),
    "get_ipa_map": lambda lex: lex.get_ipa_map(),
}


@pytest.mark.parametrize("name", sorted(DICTIONARY))
def test_dictionary_api_warns_once_with_removal_version(lex, name):
    deprecations = _recorded(lambda: DICTIONARY[name](lex))
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


TABLE = "desacordo_ortografico/data/spelling.json"
TO_AO1990 = 'desacordo_ortografico.convert(text, source, "ao1990-pt") or "ao1990-br"'

# name -> (the access, the replacement in desacordo_ortografico that the warning names)
SPELLING = {
    "archaic_words": (lambda lex: lex.archaic_words, f"the etymological rows of {TABLE}"),
    "archaic_words_br": (lambda lex: lex.archaic_words_br, f"the etymological rows of {TABLE}"),
    "ao_pt": (lambda lex: lex.ao_pt, f"the pt_1973 rows of {TABLE}"),
    "ao_br": (lambda lex: lex.ao_br, f"the br_1971 rows of {TABLE}"),
    "AO1990": (lambda lex: lex.AO1990, f"the pt_1973 and br_1971 rows of {TABLE}"),
    "silent_p_words": (lambda lex: lex.silent_p_words, f"the pt_1973 rows of {TABLE}"),
    "voiced_u_words": (lambda lex: lex.voiced_u_words, f"the br_1971 rows of {TABLE}"),
    "modern_spelling": (lambda lex: lex.modern_spelling("pharmacia", "pt-BR"), TO_AO1990),
    "normalize_ao1900": (lambda lex: lex.normalize_ao1900("acção"), TO_AO1990),
    "reverse_ao1900_pt": (lambda lex: lex.reverse_ao1900_pt("ação"),
                          'desacordo_ortografico.convert(text, "ao1990-pt", "pt_1973")'),
    "reverse_ao1900_br": (lambda lex: lex.reverse_ao1900_br("frequente"),
                          'desacordo_ortografico.convert(text, "ao1990-br", "br_1971")'),
}


@pytest.mark.parametrize("name", sorted(SPELLING))
def test_spelling_api_warns_once_at_the_caller(name):
    call, replacement = SPELLING[name]
    lex = TugaLexicon()
    # the second access reads a cached table and warns the same way
    for _ in range(2):
        deprecations = _recorded(lambda: call(lex))
        assert len(deprecations) == 1, [str(w.message) for w in deprecations]
        assert str(deprecations[0].message) == (
            f"TugaLexicon.{name} is deprecated and will be removed in {REMOVAL}. "
            f"desacordo_ortografico owns the spelling tables: use {replacement}."
        )
        # the warning names the line of the access in this file
        assert (deprecations[0].filename, deprecations[0].lineno) == (__file__, call.__code__.co_firstlineno)


def test_spelling_removal_version_is_the_next_major():
    assert tugalex.SPELLING_REMOVAL_VERSION == f"{VERSION_MAJOR + 1}.0.0"


@pytest.fixture
def major_5(monkeypatch):
    """tugalex imported again as if version.py said VERSION_MAJOR = 5."""
    monkeypatch.setattr(tugalex.version, "VERSION_MAJOR", 5)
    yield importlib.reload(tugalex)
    monkeypatch.undo()
    importlib.reload(tugalex)


def test_spelling_removal_version_follows_version_py(major_5):
    assert major_5.SPELLING_REMOVAL_VERSION == "6.0.0"
    deprecations = _recorded(lambda: major_5.TugaLexicon().ao_pt)
    assert len(deprecations) == 1
    assert "will be removed in tugalex 6.0.0." in str(deprecations[0].message)


def test_spelling_api_returns_the_frozen_tables(lex):
    # each expected value is a row of the CSVs that FROZEN pins
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        assert lex.archaic_words["pharmacia"] == "farmácia"
        assert lex.archaic_words_br["chronico"] == "crônico"
        assert lex.ao_pt["acção"] == ["ação"]
        assert lex.ao_br["idéia"] == ["ideia"]
        assert lex.AO1990["acção"] == ["ação"]
        # both tables hold intersectar; the pt-BR row wins the merge
        assert lex.ao_pt["intersectar"] == ["intersetar", "intersectar"]
        assert lex.AO1990["intersectar"] == ["intersetar"]
        assert "peremptório" in lex.silent_p_words
        assert "frequente" in lex.voiced_u_words
        assert lex.modern_spelling("Pharmacia", "pt-BR") == "Farmácia"
        assert lex.normalize_ao1900("acção óptimo") == "ação ótimo"
        assert lex.reverse_ao1900_pt("ótimo") == "óptimo"
        assert lex.reverse_ao1900_br("frequente") == "freqüente"


def test_phlegmao_is_the_archaic_key_of_flegmao(lex):
    # Cândido de Figueiredo, Novo Diccionário da Língua Portuguesa (1913), in
    # Dicionário Aberto: "Phlegmão, m. (V. fleimão)". VOP lists flegmão. phlegmon is
    # the French and English spelling; Dicionário Aberto has no entry for it.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        assert lex.archaic_words["phlegmão"] == "flegmão"
        assert lex.archaic_words_br["phlegmão"] == "flegmão"
        assert "phlegmon" not in lex.archaic_words


def test_antarctia_maps_to_antartia(lex):
    # Not a misspelling of antárctica. VOP lists antártia, a feminine noun, with the
    # variant antárctia. Figueiredo (1913) defines Antárctia as a genus of beetles.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        assert lex.ao_pt["antárctia"] == ["antártia"]
        assert lex.ao_pt["antárctica"] == ["antártica"]


def test_intercepto_lists_the_pt_pt_ao1990_form_first(lex):
    # VOP lemma 191893: "interceto - adjetivo", Portugal, "variante AO de : intercepto".
    # Like infecto, the row lists the AO1990 pt-PT form first and the p form second.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        assert lex.ao_pt["intercepto"] == ["interceto", "intercepto"]
        assert lex.ao_pt["infecto"] == ["infeto", "infecto"]


# The deprecated accessors return this data unchanged until their removal.
FROZEN = {
    "archaisms.csv": "46c192342e9676f36a1fcec4eef123ba3d8df2cd3e40c10a51b6334019e65742",
    "acordo_ortografico_pt_PT.csv": "248c49f0e2a1f5bd02ce3249fa3b86927b7d491f17f30902639fd43a1d4193fe",
    "acordo_ortografico_pt_BR.csv": "7ec069023e05c8b81cb8d0db60ad9b8610d66f2e64ff0d07e90ecf898e8e691e",
}


@pytest.mark.parametrize("name", sorted(FROZEN))
def test_spelling_tables_are_frozen(name):
    assert hashlib.sha256((DATA / name).read_bytes()).hexdigest() == FROZEN[name]


def test_neo_republicano_doubles_the_r(lex):
    # AO1990 Base XVI 2.º a): "Nas formações em que o prefixo ou falso prefixo termina em
    # vogal e o segundo elemento começa por r ou s, devendo estas consoantes duplicar-se".
    # The VOP lists neorrepublicano, a noun and an adjective, and has no neorepublicano.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        assert lex.ao_pt["neo-republicano"] == ["neorrepublicano"]
        assert lex.ao_br["neo-republicano"] == ["neorrepublicano"]
        assert lex.ao_pt["neo-republicanismo"] == ["neorrepublicanismo"]


KEPT = {
    "constructor": lambda lex: TugaLexicon(),
    "get_noun_gender": lambda lex: TugaLexicon.get_noun_gender("casa"),
    "get_given_name_gender": lambda lex: TugaLexicon.get_given_name_gender("Isabel"),
    "get_wordlist": lambda lex: lex.get_wordlist(),
    "get_wordlist rjx": lambda lex: lex.get_wordlist("rjx"),
}


@pytest.mark.parametrize("name", sorted(KEPT))
def test_kept_api_is_silent(lex, name):
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        KEPT[name](lex)


def test_internal_reads_of_the_spelling_tables_are_silent():
    lex = TugaLexicon()
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        # _get_phonemes looks pharmacia up in the archaism table first
        assert lex._get_phonemes("pharmacia", "NOUN", "lbx") == lex._get_phonemes("farmácia", "NOUN", "lbx")
        assert lex._ao_by_lowercase[True]["idéia"] == ["ideia"]


def test_dictionary_api_reads_no_spelling_accessor():
    deprecations = _recorded(lambda: TugaLexicon().get_phonemes("pharmacia"))
    assert [str(w.message).split()[0] for w in deprecations] == ["TugaLexicon.get_phonemes"]


EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


@pytest.mark.parametrize("name", ["04_ao1990.py", "05_phenomena.py"])
def test_example_names_the_removal_release_and_the_replacement(name):
    # An example that calls a deprecated accessor says when it goes away, in
    # the words of the warning, and what replaces it.
    doc = (EXAMPLES / name).read_text(encoding="utf-8")
    assert f"removed in {REMOVAL}" in doc
    assert "next major release" not in doc
    assert "desacordo_ortografico.convert(" in doc or "desacordo_ortografico/data/spelling.json" in doc
