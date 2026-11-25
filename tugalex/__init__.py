import csv
import gzip
import os
import re
from collections import defaultdict
from functools import lru_cache
from typing import Dict, List, Tuple, Optional

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
NOUN_GENDER_PATH = os.path.join(_DATA_DIR, "noun_gender_exceptions.csv.gz")
GIVEN_NAMES_PATH = os.path.join(_DATA_DIR, "given_names.csv.gz")
WORDLIST_PATH = os.path.join(_DATA_DIR, "words.csv.gz")

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
    A lexicon of Portuguese: the word list of the regional pronunciation
    dictionary of the Portal da Língua Portuguesa, the gender of common nouns
    and given names, and the pronunciations of the heterophonic homographs.

    The word list covers six regions: ``lbx`` (Lisbon, Portugal), ``rjx``
    (Rio de Janeiro, Brazil), ``spx`` (São Paulo, Brazil), ``lda`` (Luanda,
    Angola), ``mpx`` (Maputo, Mozambique) and ``dli`` (Dili, Timor-Leste).
    """

    def __init__(self) -> None:
        """Load the homograph table."""
        self.homographs_path: str = os.path.join(_DATA_DIR, "heterophonic_homographs.csv")
        self.homographs: Dict[str, Dict[str, str]] = self._load_homographs(self.homographs_path)

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

    def get_wordlist(self, region: str = "lbx") -> List[str]:
        """
        Return a sorted list of the word forms known for the given region.

        The list comes from ``data/words.csv.gz``, the word forms of the
        Portal da Língua Portuguesa regional dictionary with no pronunciations.

        Parameters:
            region (str): Region code (e.g., "lbx") identifying the dataset to query.

        Returns:
            List[str]: Lowercase word forms of the region, sorted alphabetically.

        Raises:
            ValueError: If the dialect is unsupported.
        """
        try:
            return list(_wordlists()[region])
        except KeyError as e:
            raise ValueError(f"Unsupported dialect: {region}") from e

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
