import csv
import gzip
import os
import re
import warnings
from collections import defaultdict
from difflib import SequenceMatcher
from functools import cached_property, lru_cache
from typing import Dict, List, Tuple, Optional, Set, Union

from tugalex.version import VERSION_MAJOR

# region -> word -> POS -> phonemes
IPA_MAP = Dict[str, Dict[str, Dict[str, str]]]
# region -> word -> list of syllables
SYLLABLE_MAP = Dict[str, Dict[str, List[str]]]
# Word mapping (e.g., AO1990 old -> new)
WORD_REPLACEMENT_MAP = Dict[str, List[str]]


#: The release that removes the regional pronunciation dictionary and its phoneme API.
DICTIONARY_REMOVAL_VERSION = f"{VERSION_MAJOR + 1}.0.0"


def _warn_dictionary(name: str, stacklevel: int = 3) -> None:
    warnings.warn(
        f"TugaLexicon.{name} is deprecated and will be removed in tugalex "
        f"{DICTIONARY_REMOVAL_VERSION}, together with the regional pronunciation "
        "dictionary it reads. The legacy tugaphone.dialects inventories read "
        "this dictionary and go away with it. For Portuguese pronunciation, use "
        "orthography2ipa with the pt-PT lexicon of o2i-lexicons "
        "(orthography2ipa.use_packaged_lexicons).",
        DeprecationWarning,
        stacklevel=stacklevel,
    )


#: The release that removes the archaism and AO1990 spelling accessors.
SPELLING_REMOVAL_VERSION = f"{VERSION_MAJOR + 1}.0.0"

_TABLE = "desacordo_ortografico/data/spelling.json"
_TO_AO1990 = 'desacordo_ortografico.convert(text, source, "ao1990-pt") or "ao1990-br"'

# The desacordo_ortografico name that replaces each deprecated spelling accessor.
_SPELLING_REPLACEMENTS: Dict[str, str] = {
    "archaic_words": f"the etymological rows of {_TABLE}",
    "archaic_words_br": f"the etymological rows of {_TABLE}",
    "ao_pt": f"the pt_1973 rows of {_TABLE}",
    "ao_br": f"the br_1971 rows of {_TABLE}",
    "AO1990": f"the pt_1973 and br_1971 rows of {_TABLE}",
    "silent_p_words": f"the pt_1973 rows of {_TABLE}",
    "voiced_u_words": f"the br_1971 rows of {_TABLE}",
    "modern_spelling": _TO_AO1990,
    "normalize_ao1900": _TO_AO1990,
    "reverse_ao1900_pt": 'desacordo_ortografico.convert(text, "ao1990-pt", "pt_1973")',
    "reverse_ao1900_br": 'desacordo_ortografico.convert(text, "ao1990-br", "br_1971")',
}


def _warn_spelling(name: str) -> None:
    warnings.warn(
        f"TugaLexicon.{name} is deprecated and will be removed in tugalex "
        f"{SPELLING_REMOVAL_VERSION}. desacordo_ortografico owns the spelling "
        f"tables: use {_SPELLING_REPLACEMENTS[name]}.",
        DeprecationWarning,
        stacklevel=3,
    )


_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
NOUN_GENDER_PATH = os.path.join(_DATA_DIR, "noun_gender_exceptions.csv.gz")
GIVEN_NAMES_PATH = os.path.join(_DATA_DIR, "given_names.csv.gz")
WORDLIST_PATH = os.path.join(_DATA_DIR, "words.csv.gz")
REGIONAL_DICT_PATH = os.path.join(_DATA_DIR, "regional_dict.csv.gz")

# Suffix rules for the gender of a Portuguese noun, singular or plural. The
# first match wins. Each rule is right for at least 80% of the nouns it
# matches in the source of noun_gender_exceptions.csv.gz (see
# scripts/build_noun_gender.py); the exceptions file lists the nouns the
# rules get wrong or do not cover, and the closed-class words.
NOUN_GENDER_SUFFIXES: Tuple[Tuple[str, str], ...] = (
    ("f", r"ç(?:ão|ões)$"),
    ("f", r"s(?:ão|ões)$"),
    ("f", r"dades?$"),
    ("f", r"tudes?$"),
    ("f", r"(?:gem|gens)$"),
    ("f", r"ezas?$"),
    ("f", r"ises?$"),
    ("m", r"(?<!ã)os?$"),
    ("m", r"(?:or|ores)$"),
    ("m", r"umes?$"),
    ("m", r"gramas?$"),
    ("f", r"as?$"),
)
_NOUN_GENDER_PATTERNS = tuple((gender, re.compile(suffix)) for gender, suffix in NOUN_GENDER_SUFFIXES)


def suffix_noun_gender(word: str) -> Optional[str]:
    """The gender that the suffix rules alone give a noun, or None."""
    return next((gender for gender, suffix in _NOUN_GENDER_PATTERNS if suffix.search(word)), None)


@lru_cache(maxsize=1)
def _noun_gender_exceptions() -> Dict[str, str]:
    with gzip.open(NOUN_GENDER_PATH, "rt", encoding="utf-8", newline="") as f:
        return {row["word"]: row["gender"] for row in csv.DictReader(f)}


@lru_cache(maxsize=1)
def _given_names() -> Dict[str, str]:
    with gzip.open(GIVEN_NAMES_PATH, "rt", encoding="utf-8", newline="") as f:
        return {row["name"]: row["gender"] for row in csv.DictReader(f)}


@lru_cache(maxsize=1)
def _wordlists() -> Dict[str, List[str]]:
    """Region code -> sorted word forms, read from words.csv.gz."""
    wordlists: Dict[str, List[str]] = defaultdict(list)
    with gzip.open(WORDLIST_PATH, "rt", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            for region in row["regions"].split():
                wordlists[region].append(row["word"])
    return dict(wordlists)


class TugaLexicon:
    """
    A lexicon handler for Portuguese dialects, supporting phoneme transcription,
    syllable segmentation, and orthographic agreement rules (AO1990).

    Supports:
        - pt-PT (Portugal)
        - pt-BR (Brazil)
        - pt-AO (Angola)
        - pt-MZ (Mozambique)
        - pt-TL (Timor-Leste)

    The regional pronunciation dictionary and its phoneme API (``ipa``,
    ``syllables``, ``regions``, ``possible_postags``, ``lang_to_region``,
    ``get_phonemes``, ``get_syllables``, ``get`` and ``get_ipa_map``) are
    deprecated and emit a ``DeprecationWarning``. They are removed in
    ``DICTIONARY_REMOVAL_VERSION``.

    The archaism and AO1990 spelling accessors (``archaic_words``,
    ``archaic_words_br``, ``ao_pt``, ``ao_br``, ``AO1990``, ``silent_p_words``,
    ``voiced_u_words``, ``modern_spelling``, ``normalize_ao1900``,
    ``reverse_ao1900_pt`` and ``reverse_ao1900_br``) are deprecated too. They
    return the frozen tugalex tables and are removed in
    ``SPELLING_REMOVAL_VERSION``. desacordo_ortografico owns the spelling table.

    The word list (``get_wordlist``) and the noun and given-name gender lookups
    stay.
    """

    _DIALECT_REGIONS: Dict[str, str] = {
        "pt-PT": "lbx",
        "pt-BR": "rjx",
        "pt-AO": "lda",
        "pt-MZ": "mpx",
        "pt-TL": "dli",
    }

    def __init__(self, dictionary_path: Optional[str] = None) -> None:
        """Load the spelling and homograph tables; the pronunciation dictionary loads on first use.

        ``dictionary_path`` is a CSV, optionally gzip-compressed, with the
        columns ``word, phones, syllables, region_code``. The default is
        ``data/regional_dict.csv.gz``, an extract of
        TigreGotico/portuguese-unified-pronunciation-lexicon built by
        ``scripts/build_regional_dict.py``.
        """
        self.dictionary_path: str = dictionary_path or REGIONAL_DICT_PATH
        self.ao_pt_path: str = os.path.join(_DATA_DIR, "acordo_ortografico_pt_PT.csv")
        self.ao_br_path: str = os.path.join(_DATA_DIR, "acordo_ortografico_pt_BR.csv")
        self.homographs_path: str = os.path.join(_DATA_DIR, "heterophonic_homographs.csv")
        self.archaisms_path: str = os.path.join(_DATA_DIR, "archaisms.csv")

        self._ao_pt: Dict[str, List[str]] = self._load_ao(self.ao_pt_path)
        self._ao_br: Dict[str, List[str]] = self._load_ao(self.ao_br_path)
        self.homographs: Dict[str, Dict[str, str]] = self._load_homographs(self.homographs_path)
        self._archaic_words, self._archaic_words_br = self._load_archaisms(self.archaisms_path)
        self._ipa: IPA_MAP = {}
        self._syllables: SYLLABLE_MAP = {}
        self._regions: Set[str] = set()

    @staticmethod
    def _load_archaisms(path: str) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Load the pre-1911 spellings as two maps to their pt-PT and pt-BR modern forms."""
        pt: Dict[str, str] = {}
        br: Dict[str, str] = {}
        with open(path, "r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                pt[row["archaic"]] = row["modern"]
                br[row["archaic"]] = row["modern_pt_BR"] or row["modern"]
        return pt, br

    @staticmethod
    def _load_homographs(path: str) -> Dict[str, Dict[str, str]]:
        """Read ``word,pos,ipa`` rows into word -> POS -> IPA; quotes are dropped."""
        data = {}
        with open(path, encoding="utf-8") as f:
            for line in f.read().split("\n")[1:]:
                parts = line.replace('"', "").split(",", 2)
                if len(parts) == 3:
                    word, pos, ipa = (part.strip() for part in parts)
                    data.setdefault(word, {})[pos] = ipa
        return data

    @staticmethod
    def _load_lang_map(path: str) -> Tuple[IPA_MAP, SYLLABLE_MAP, Set[str]]:
        """Read a pronunciation CSV into region -> word maps of IPA and syllables, and the set of regions.

        The CSV (gzip when the name ends in ``.gz``) has the columns ``word,
        phones, syllables, region_code``; ``#`` lines (the provenance header)
        are skipped. ``word`` and ``region_code`` are lowercased, and the ``|``
        syllable separator of ``phones`` becomes ``·``. The lexicon is POS-free:
        each word has one pronunciation, under the ``""`` POS key; the
        homographs table holds the POS-keyed ones.
        """
        ipa: IPA_MAP = {}
        syllables: SYLLABLE_MAP = {}
        regions: Set[str] = set()

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8") as f:
            reader = csv.reader(line for line in f if not line.startswith("#"))
            next(reader, None)  # header
            for parts in reader:
                if len(parts) < 4:
                    continue
                word, phonemes, syl, region = parts[:4]
                word = word.strip().lower()
                region = region.strip().lower()
                regions.add(region)
                ipa.setdefault(region, {}).setdefault(word, {})[""] = phonemes.replace("|", "·").strip()
                syllables.setdefault(region, {})[word] = syl.strip().replace(" ", "|").split("|")

        return ipa, syllables, regions

    @staticmethod
    def _load_ao(path: str) -> Dict[str, List[str]]:
        """Read an ``old_form,new_form`` CSV into old spelling -> new spellings.

        Either field may be a quoted, comma-separated list of spellings; every
        old spelling maps to all the new spellings of its row.
        """
        ao: Dict[str, List[str]] = {}
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # header
            for row in reader:
                if len(row) != 2:
                    continue
                old_forms, new_forms = row
                new_words = [w.strip() for w in new_forms.split(",")]
                for old_word in old_forms.split(","):
                    ao[old_word.strip()] = list(new_words)
        return ao

    @property
    def ipa(self) -> IPA_MAP:
        """
        Get the loaded IPA mapping (lazy loaded).

        Returns:
            IPA_MAP: Mapping of region -> word -> POS -> phonemes.

        Deprecated: removed in ``DICTIONARY_REMOVAL_VERSION``.
        """
        _warn_dictionary("ipa")
        self._load_dictionary()
        return self._ipa

    @property
    def syllables(self) -> SYLLABLE_MAP:
        """
        Get the loaded syllable mapping (lazy loaded).

        Returns:
            SYLLABLE_MAP: Mapping of region -> word -> list of syllables.

        Deprecated: removed in ``DICTIONARY_REMOVAL_VERSION``.
        """
        _warn_dictionary("syllables")
        self._load_dictionary()
        return self._syllables

    @property
    def regions(self) -> Set[str]:
        """
        Get the set of available region codes (lazy loaded).

        Returns:
            Set[str]: Set of region codes (e.g., 'lbx', 'rjx').

        Deprecated: removed in ``DICTIONARY_REMOVAL_VERSION``.
        """
        _warn_dictionary("regions")
        self._load_dictionary()
        return self._regions

    def _load_dictionary(self) -> None:
        if not self._ipa:
            self._ipa, self._syllables, self._regions = self._load_lang_map(self.dictionary_path)

    def lang_to_region(self, lang: str) -> str:
        """
        Map an ISO Portuguese dialect code to the internal dataset region code.

        Parameters:
            lang (str): ISO dialect code (e.g., "pt-PT", "pt-BR").

        Returns:
            region (str): Corresponding dataset region code (e.g., "lbx", "rjx").

        Raises:
            ValueError: If the provided dialect code is not supported.

        Deprecated: removed in ``DICTIONARY_REMOVAL_VERSION``.
        """
        _warn_dictionary("lang_to_region")
        try:
            return self._DIALECT_REGIONS[lang]
        except KeyError as e:
            raise ValueError(f"Unsupported dialect: {lang}") from e

    def get_phonemes(self, word: str, pos: str = "NOUN", region: str = "lbx") -> Optional[str]:
        """
        Retrieve the phoneme transcription for a word in a specific region and part of speech.

        Parameters:
            word: The word to look up; matching is case-insensitive because entries are normalized to lowercase.
            pos: Uppercase part-of-speech tag (default: "NOUN"). It selects the
                entry of a heterophonic homograph, whose pronunciation is
                region-independent. The regional dictionary is POS-free, so for
                every other word (and for a tag the homograph has no entry for)
                the POS does not change the answer.
            region: Region code identifying the dialect dataset (e.g., "lbx").

        Returns:
            The phoneme string, or None if no entry exists. An archaic spelling
            is rewritten to its modern form before the lookup.

        Raises:
            ValueError: If the region is not in the loaded dataset.

        Deprecated: removed in ``DICTIONARY_REMOVAL_VERSION``.
        """
        _warn_dictionary("get_phonemes")
        return self._get_phonemes(word, pos, region)

    def _get_phonemes(self, word: str, pos: str, region: str) -> Optional[str]:
        self._load_dictionary()
        if region not in self._ipa:
            raise ValueError(f"Unsupported dialect: {region}")
        word = word.strip().lower()
        word = self._archaic_words.get(word, word)

        homograph = self.homographs.get(word, {})
        if pos in homograph:
            return homograph[pos]

        # The lexicon is POS-free: POS only selects a homograph entry above.
        entry = self._ipa[region].get(word, {})
        return entry.get(pos) or entry.get("")

    def get_syllables(self, word: str, region: str = "lbx") -> List[str]:
        """
        Retrieve the syllable segments for a word in the given region.

        Parameters:
            word (str): The target word; matching is case-insensitive because entries are normalized to lowercase.
            region (str): Dataset region code (e.g. 'lbx', 'rjx', 'lda', 'mpx', 'dli').

        Returns:
            List[str]: List of syllable strings. Returns empty list if word not found.

        Raises:
            ValueError: If the region is not in the loaded dataset.

        Deprecated: removed in ``DICTIONARY_REMOVAL_VERSION``.
        """
        _warn_dictionary("get_syllables")
        return self._get_syllables(word, region)

    def _get_syllables(self, word: str, region: str) -> List[str]:
        self._load_dictionary()
        if region not in self._syllables:
            raise ValueError(f"Unsupported dialect: {region}")
        return self._syllables[region].get(word.strip().lower(), [])

    def get(
            self, word: str, pos: str = "NOUN", region: str = "lbx"
    ) -> Dict[str, Union[Optional[str], List[str]]]:
        """
        Retrieve both syllable segmentation and phoneme transcription for a word in a given region and part of speech.

        Parameters:
            word (str): The lookup word (case-insensitive).
            pos (str): Part-of-speech tag to select the phoneme variant (default: "NOUN").
            region (str): Region code to query (e.g. "lbx") (default: "lbx").

        Returns:
            dict: A mapping with keys:
                - "syllables": list of syllable segments for the word in the region, or an empty list if not found.
                - "phonemes": phoneme transcription for the given POS and region, or `None` if not found.

        Deprecated: removed in ``DICTIONARY_REMOVAL_VERSION``.
        """
        _warn_dictionary("get")
        return {
            "syllables": self._get_syllables(word, region),
            "phonemes": self._get_phonemes(word, pos, region),
        }

    def get_wordlist(self, region: str = "lbx") -> List[str]:
        """
        Return a sorted list of the word forms known for the given region.

        With the packaged dictionary, the list comes from
        ``data/words.csv.gz``, the word forms of the Portal da Língua
        Portuguesa regional dictionary with no pronunciations, and the call
        does not warn. With a custom ``dictionary_path``, the list holds the
        words of that dictionary, and the call emits the dictionary
        ``DeprecationWarning``: custom dictionaries go in
        ``DICTIONARY_REMOVAL_VERSION``.

        Parameters:
            region (str): Region code (e.g., "lbx") identifying the dataset to query.

        Returns:
            List[str]: Lowercase word forms of the region, sorted alphabetically.

        Raises:
            ValueError: If the dialect is unsupported.
            FileNotFoundError: If a custom ``dictionary_path`` does not exist.
        """
        try:
            if self.dictionary_path != REGIONAL_DICT_PATH:
                _warn_dictionary("dictionary_path")
                self._load_dictionary()
                return sorted(self._syllables[region])
            return list(_wordlists()[region])
        except KeyError as e:
            raise ValueError(f"Unsupported dialect: {region}") from e

    def get_ipa_map(self, pos: str = "NOUN", region: str = "lbx") -> Dict[str, str]:
        """
        Get a flat dictionary mapping words to phonemes for a specific POS and region.

        Every word of the regional dictionary appears with its POS-free
        pronunciation. *pos* only selects which homograph-table entries
        replace those pronunciations.

        Args:
            pos (str): Uppercase part-of-speech tag for the homograph entries.
            region (str): Region code.

        Returns:
            Dict[str, str]: Map of {word: phonemes}.

        Raises:
            ValueError: If the region is not in the loaded dataset.

        Deprecated: removed in ``DICTIONARY_REMOVAL_VERSION``.
        """
        _warn_dictionary("get_ipa_map")
        self._load_dictionary()
        if region not in self._ipa:
            raise ValueError(f"Unsupported dialect: {region}")
        homo = self.homographs
        table = {}
        for word, entry in self._ipa[region].items():
            # the lexicon is POS-free; POS only selects homograph overrides
            value = entry.get(pos) or entry.get("")
            if value:
                table[word] = value
        table.update({
            word: homo[word][pos]
            for word in homo
            if pos in homo[word]
        })
        return table

    @cached_property
    def possible_postags(self) -> Dict[str, List[str]]:
        """
        Get all possible Part-of-Speech tags for words in the lexicon.

        Returns:
            Dict[str, List[str]]: Map of word -> list of available POS tags.
                A heterophonic homograph lists its homograph-table tags. Every
                other word of the ``lbx`` dictionary lists ``[""]``, the key
                of its POS-free entry.

        Deprecated: removed in ``DICTIONARY_REMOVAL_VERSION``.
        """
        # cached_property adds a frame between the caller and this getter
        _warn_dictionary("possible_postags", stacklevel=4)
        self._load_dictionary()
        homo = self.homographs
        return {
            **{
                word: list(entry.keys())
                for word, entry in self._ipa["lbx"].items()
            },
            **{
                word: list(homo[word].keys())
                for word in homo
            }}

    @staticmethod
    def get_noun_gender(word: str) -> Optional[str]:
        """The gender of a Portuguese common noun, singular or plural, in any letter case.

        Returns "m", "f", "mf" for a noun of both genders (a common-gender noun
        such as "artista", or one whose gender changes with its meaning, such as
        "rádio"), or None. The exceptions list decides first, then the suffix
        rules (``NOUN_GENDER_SUFFIXES``). A determiner, pronoun, article or
        contraction gets its own gender ("uma", "da" f; "um", "do" m). A word
        that Wiktionary lists only in a closed class with no gender ("ainda",
        "para", "cada") is listed with none and gets None, as does an unlisted
        word that no rule matches.
        """
        word = word.lower()
        exceptions = _noun_gender_exceptions()
        if word in exceptions:
            return exceptions[word] or None
        return suffix_noun_gender(word)

    @staticmethod
    def get_given_name_gender(name: str) -> Optional[str]:
        """The gender of a given name such as "Isabel" or "João": "m", "f", "mf" ("Darci"), or None if not listed.

        The list holds regnal names ("Pio", "Isabel"), the Brazilian census
        names that match a Wikidata given name, and the Wikidata given names
        marked Portuguese (see ``scripts/build_given_names.py``). The match is
        exact: a name is written as in running text, with its capital letter
        and accents, so "isabel" and "joão" are not found.
        """
        return _given_names().get(name)

    @property
    def archaic_words(self) -> Dict[str, str]:
        """
        Pre-1911 spelling -> its modern pt-PT spelling, from ``archaisms.csv``.

        Deprecated: removed in ``SPELLING_REMOVAL_VERSION``.
        """
        _warn_spelling("archaic_words")
        return self._archaic_words

    @property
    def archaic_words_br(self) -> Dict[str, str]:
        """
        Pre-1911 spelling -> its modern pt-BR spelling, from ``archaisms.csv``.

        Deprecated: removed in ``SPELLING_REMOVAL_VERSION``.
        """
        _warn_spelling("archaic_words_br")
        return self._archaic_words_br

    @property
    def ao_pt(self) -> Dict[str, List[str]]:
        """
        Pre-AO1990 pt-PT spelling -> its AO1990 spellings.

        Deprecated: removed in ``SPELLING_REMOVAL_VERSION``.
        """
        _warn_spelling("ao_pt")
        return self._ao_pt

    @property
    def ao_br(self) -> Dict[str, List[str]]:
        """
        Pre-AO1990 pt-BR spelling -> its AO1990 spellings.

        Deprecated: removed in ``SPELLING_REMOVAL_VERSION``.
        """
        _warn_spelling("ao_br")
        return self._ao_br

    @property
    def AO1990(self) -> Dict[str, List[str]]:
        """
        Get a combined dictionary of Old -> New spelling for PT and BR (AO1990).

        Deprecated: removed in ``SPELLING_REMOVAL_VERSION``.
        """
        _warn_spelling("AO1990")
        return self._ao1990

    @cached_property
    def _ao1990(self) -> Dict[str, List[str]]:
        return {**self._ao_pt, **self._ao_br}

    @property
    def silent_p_words(self) -> Set[str]:
        """
        Set of words where 'p' is silent (common in mpc/mpç/mpt clusters before AO1990).

        Returns:
            Set[str]: Words containing silent 'p'.

        Deprecated: removed in ``SPELLING_REMOVAL_VERSION``.
        """
        _warn_spelling("silent_p_words")
        return self._silent_p_words

    @cached_property
    def _silent_p_words(self) -> Set[str]:
        return {old_word
                for cluster in ("mpc", "mpç", "mpt")
                for old_word, new_words in self._ao1990.items()
                for new_word in new_words
                if cluster in old_word and cluster not in new_word}

    @property
    def voiced_u_words(self) -> Set[str]:
        """
        Set of words with a voiced 'u' in 'gue'/'gui'/'que'/'qui': the modern
        spellings of the words whose pre-AO1990 Brazilian spelling has the
        trema 'ü', based on the Brazilian AO dictionary.

        Returns:
            Set[str]: Modern spellings of words with voiced 'u'.

        Deprecated: removed in ``SPELLING_REMOVAL_VERSION``.
        """
        _warn_spelling("voiced_u_words")
        return self._voiced_u_words

    @cached_property
    def _voiced_u_words(self) -> Set[str]:
        return {new_word
                for old_word, new_words in self._ao_br.items()
                for new_word in new_words
                if "ü" in old_word}

    @cached_property
    def _ao_by_lowercase(self) -> Dict[bool, Dict[str, List[str]]]:
        """The pt-PT (``False``) and pt-BR (``True``) AO1990 tables, keyed in lowercase."""
        return {
            brazilian: {old.lower(): news for old, news in table.items()}
            for brazilian, table in ((False, self._ao_pt), (True, self._ao_br))
        }

    def modern_spelling(self, word: str, lang: str = "pt-PT") -> str:
        """
        Return the modern spelling of one word in the variety of ``lang``.

        A pre-1911 etymological spelling (``pharmacia``) maps to its modern
        form, and a spelling from before the 1990 agreement (``acção``) maps to
        its AO1990 form. The tables of the variety apply: pt-BR for a tag with
        the region ``BR``, pt-PT for every other tag. A word that is already a
        valid AO1990 spelling stays as written; pt-PT keeps both forms of a
        word such as ``sector`` and ``setor``. When the agreement gives more
        than one form, the form closest to the written word is used, so no
        consonant is added or dropped that the writer did not write. A
        word in capitals stays in capitals, and the first letter follows the
        written word. A capital inside the table entry stays (``arco de Deus``).

        AO1990 removed the hyphen from some compounds, so the result can be
        several words: ``acha-de-armas`` gives ``acha de armas``.

        Args:
            word (str): One word, with no punctuation attached.
            lang (str): The language tag of the text, such as ``pt-BR`` or
                ``pt_BR``.

        Returns:
            str: The modern spelling, or ``word`` unchanged.

        Deprecated: removed in ``SPELLING_REMOVAL_VERSION``.
        """
        _warn_spelling("modern_spelling")
        subtags = re.split(r"[.@]", lang)[0].replace("_", "-").lower().split("-x-")[0].split("-")
        brazilian = "br" in subtags[1:]
        lowered = word.lower()
        archaic = self._archaic_words_br if brazilian else self._archaic_words
        modern = archaic.get(lowered, lowered)
        forms = self._ao_by_lowercase[brazilian].get(modern, [modern])
        if modern not in (form.lower() for form in forms):
            modern = max(forms, key=lambda form: SequenceMatcher(None, lowered, form.lower()).ratio())
        if modern == lowered:
            return word
        if word.isupper():
            return modern.upper()
        first = modern[:1].upper() if word[:1].isupper() else modern[:1].lower()
        return first + modern[1:]

    def normalize_ao1900(self, sentence: str) -> str:
        """
        Normalize a sentence to AO1990 standards.

        The sentence is split on whitespace and each word is looked up exactly
        as written, so a word with attached punctuation or a capital letter is
        not converted. The words are joined with single spaces.

        Args:
            sentence (str): Input sentence with potentially old spelling.

        Returns:
            str: Sentence with words replaced by their AO1990 equivalents.

        Deprecated: removed in ``SPELLING_REMOVAL_VERSION``.
        """
        _warn_spelling("normalize_ao1900")
        words = [self._ao1990.get(w, [w])[0] for w in sentence.split()]
        return " ".join(words)

    def reverse_ao1900_pt(self, sentence: str) -> str:
        """
        Revert a sentence from AO1990 to pre-agreement PT-PT spelling.

        The sentence is split on whitespace and each word is looked up exactly
        as written, so a word with attached punctuation or a capital letter is
        not converted. The words are joined with single spaces.

        Args:
            sentence (str): Input sentence in modern spelling.

        Returns:
            str: Sentence using pre-AO1990 PT spelling.

        Deprecated: removed in ``SPELLING_REMOVAL_VERSION``.
        """
        _warn_spelling("reverse_ao1900_pt")
        reverse: Dict[str, str] = {}
        for old_word, new_words in self._ao_pt.items():
            for new_word in new_words:
                reverse[new_word] = old_word

        words = [reverse.get(w, w) for w in sentence.split()]
        return " ".join(words)

    def reverse_ao1900_br(self, sentence: str) -> str:
        """
        Revert a sentence from AO1990 to pre-agreement PT-BR spelling.

        The sentence is split on whitespace and each word is looked up exactly
        as written, so a word with attached punctuation or a capital letter is
        not converted. The words are joined with single spaces.

        Args:
            sentence (str): Input sentence in modern spelling.

        Returns:
            str: Sentence using pre-AO1990 BR spelling.

        Deprecated: removed in ``SPELLING_REMOVAL_VERSION``.
        """
        _warn_spelling("reverse_ao1900_br")
        reverse: Dict[str, str] = {}
        for old_word, new_words in self._ao_br.items():
            for new_word in new_words:
                reverse[new_word] = old_word

        words = [reverse.get(w, w) for w in sentence.split()]
        return " ".join(words)

