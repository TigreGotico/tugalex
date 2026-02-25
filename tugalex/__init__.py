import json
import os
from functools import cached_property
from typing import Dict, List, Tuple, Optional, Set, Union

# Typing aliases for better readability
# region -> word -> POS -> phonemes
IPA_MAP = Dict[str, Dict[str, Dict[str, str]]]
# region -> word -> list of syllables
SYLLABLE_MAP = Dict[str, Dict[str, List[str]]]
# Word mapping (e.g., AO1990 old -> new)
WORD_REPLACEMENT_MAP = Dict[str, List[str]]


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
    """

    _DIALECT_REGIONS: Dict[str, str] = {
        "pt-PT": "lbx",
        "pt-BR": "rjx",
        "pt-AO": "lda",
        "pt-MZ": "mpx",
        "pt-TL": "dli",
    }

    def __init__(self, dictionary_path: Optional[str] = None) -> None:
        """
        Initialize the TugaLexicon and prepare paths for regional data.

        Args:
            dictionary_path (Optional[str]): Path to the CSV file containing regional
                phoneme and syllable mappings. If None, defaults to "regional_dict.csv"
                in the data directory.
        """
        self.dictionary_path: str = dictionary_path or os.path.join(
            os.path.dirname(__file__), "data", "regional_dict.csv"
        )
        self.ao_pt_path: str = os.path.join(
            os.path.dirname(__file__), "data", "acordo_ortografico_pt_PT.csv"
        )
        self.ao_br_path: str = os.path.join(
            os.path.dirname(__file__), "data", "acordo_ortografico_pt_BR.csv"
        )
        self.homographs_path: str = os.path.join(
            os.path.dirname(__file__), "data", "heterophonic_homographs.csv"
        )
        self.archaisms_path: str = os.path.join(
            os.path.dirname(__file__), "data", "archaisms.csv"
        )

        self.ao_pt: Dict[str, List[str]] = self._load_ao(self.ao_pt_path)
        self.ao_br: Dict[str, List[str]] = self._load_ao(self.ao_br_path)
        self.homographs: Dict[str, Dict[str, str]] = self._load_homographs(self.homographs_path)
        self.archaic_words: Dict[str, str] = self._load_archaisms(self.archaisms_path)
        # Lazy loaded attributes
        self._ipa: IPA_MAP = {}
        self._syllables: SYLLABLE_MAP = {}
        self._regions: Set[str] = set()

    @staticmethod
    def _load_archaisms(path: str) -> Dict[str, str]:
        data = {}
        with open(path, "r", encoding="utf-8") as f:
            for l in f.read().split("\n")[1:]:
                if "," not in l:
                    continue
                l = l.replace('"', "")
                parts = l.split(",", 2)
                if len(parts) != 3:
                    continue
                old_word, new_word, _ = parts
                data[old_word] = new_word
        return data

    @staticmethod
    def _load_homographs(path: str) -> Dict[str, Dict[str, str]]:
        data = {}
        with open(path, "r", encoding="utf-8") as f:
            for l in f.read().split("\n")[1:]:
                if "," not in l:
                    continue
                l = l.replace('"', "")
                parts = l.split(",", 2)
                if len(parts) != 3:
                    continue
                word, pos, ipa = parts
                if word not in data:
                    data[word] = {}
                data[word][pos] = ipa
        return data

    @staticmethod
    def _load_lang_map(path: str) -> Tuple[IPA_MAP, SYLLABLE_MAP, Set[str]]:
        """
        Load phoneme and syllable mappings from a CSV into region-indexed lookup structures.

        The CSV is expected to have columns: _, word, pos, _, phonemes, syl, region.
        - `phonemes` entries use `|` as internal separator, converted to `·`.
        - `word` and `region` values are normalized to lowercase.

        Args:
            path (str): Path to the CSV file.

        Returns:
            Tuple[IPA_MAP, SYLLABLE_MAP, Set[str]]:
                - ipa: Mapping region -> word -> POS -> phoneme string.
                - syllables: Mapping region -> word -> list of syllable segments.
                - regions: Set of all loaded region codes.
        """
        ipa: IPA_MAP = {}
        syllables: SYLLABLE_MAP = {}
        regions: Set[str] = set()

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            if not lines:
                return ipa, syllables, regions

            for line in lines[1:]:  # skip header
                parts = line.lower().split(",", 6)
                if len(parts) < 7:
                    continue
                _, word, pos, _, phonemes, syl, region = parts

                phonemes = phonemes.replace("|", "·").strip()
                word = word.strip().lower()
                region = region.strip()
                regions.add(region)

                if region not in syllables:
                    syllables[region] = {}
                if region not in ipa:
                    ipa[region] = {}
                if word not in ipa[region]:
                    ipa[region][word] = {}

                syllables[region][word] = syl.strip().replace(" ", "|").split("|")
                ipa[region][word][pos.upper()] = phonemes

        return ipa, syllables, regions

    @staticmethod
    def _load_ao(path: str) -> Dict[str, List[str]]:
        """
        Load Acordo Ortográfico mappings from a CSV file.

        Args:
            path (str): Path to the CSV file containing "old_word,new_word" pairs.

        Returns:
            Dict[str, List[str]]: Mapping of old spelling to list of new spellings.
        """
        AO: Dict[str, List[str]] = {}
        if not os.path.exists(path):
            raise FileNotFoundError(path)

        with open(path, "r", encoding="utf-8") as f:
            for l in f.read().split("\n"):
                if "," not in l:
                    continue
                l = l.replace('"', "")
                parts = l.split(",", 1)
                if len(parts) != 2:
                    continue
                old_word, new_word = parts
                AO[old_word] = new_word.split(", ")
        return AO

    @property
    def ipa(self) -> IPA_MAP:
        """
        Get the loaded IPA mapping (lazy loaded).

        Returns:
            IPA_MAP: Mapping of region -> word -> POS -> phonemes.
        """
        if not self._ipa:
            self._ipa, self._syllables, self._regions = self._load_lang_map(self.dictionary_path)
        return self._ipa

    @property
    def syllables(self) -> SYLLABLE_MAP:
        """
        Get the loaded syllable mapping (lazy loaded).

        Returns:
            SYLLABLE_MAP: Mapping of region -> word -> list of syllables.
        """
        if not self._syllables:
            self._ipa, self._syllables, self._regions = self._load_lang_map(self.dictionary_path)
        return self._syllables

    @property
    def regions(self) -> Set[str]:
        """
        Get the set of available region codes (lazy loaded).

        Returns:
            Set[str]: Set of region codes (e.g., 'lbx', 'rjx').
        """
        if not self._regions:
            self._ipa, self._syllables, self._regions = self._load_lang_map(self.dictionary_path)
        return self._regions

    def lang_to_region(self, lang: str) -> str:
        """
        Map an ISO Portuguese dialect code to the internal dataset region code.

        Parameters:
            lang (str): ISO dialect code (e.g., "pt-PT", "pt-BR").

        Returns:
            region (str): Corresponding dataset region code (e.g., "lbx", "rjx").

        Raises:
            ValueError: If the provided dialect code is not supported.
        """
        try:
            return self._DIALECT_REGIONS[lang]
        except KeyError as e:
            raise ValueError(f"Unsupported dialect: {lang}") from e

    def get_phonemes(self, word: str, pos: str = "NOUN", region: str = "lbx") -> Optional[str]:
        """
        Retrieve the phoneme transcription for a word in a specific region and part of speech.

        Parameters:
            word: The word to look up; matching is case-insensitive because entries are normalized to lowercase.
            pos: Part-of-speech tag to select the transcription variant (default: "NOUN").
            region: Region code identifying the dialect dataset (e.g., "lbx").

        Returns:
            The phoneme string for the specified word and POS in the region, or None if no entry exists.
        """
        word = word.strip().lower()

        archaic = self.archaic_words
        if word in archaic:
            word = archaic[word]

        homo = self.homographs
        if word in homo and pos in homo[word]:
            return homo[word][pos]

        return self.ipa[region].get(word, {}).get(pos)

    def get_syllables(self, word: str, region: str = "lbx") -> List[str]:
        """
        Retrieve the syllable segments for a word in the given region.

        Parameters:
            word (str): The target word, normalized to lowercase.
            region (str): Dataset region code (e.g. 'lbx', 'rjx', 'lda', 'mpx', 'dli').

        Returns:
            List[str]: List of syllable strings. Returns empty list if word not found.

        Raises:
            ValueError: If the region is not in the loaded dataset.
        """
        # Ensure data is loaded
        _ = self.syllables

        if region not in self.syllables:
            raise ValueError(f"Unsupported dialect: {region}")
        return self.syllables[region].get(word, [])

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
                - "syllables": list of syllable segments for the word in the region, or `None` if not found.
                - "phonemes": phoneme transcription for the given POS and region, or `None` if not found.
        """
        return {
            "syllables": self.get_syllables(word, region),
            "phonemes": self.get_phonemes(word, pos, region),
        }

    def get_wordlist(self, region: str = "lbx") -> List[str]:
        """
        Return a sorted list of words available for the given region.

        Parameters:
            region (str): Region code (e.g., "lbx") identifying the dataset to query.

        Returns:
            List[str]: Words available in the lexicon, sorted alphabetically.

        Raises:
            ValueError: If the dialect is unsupported.
        """
        try:
            return sorted(self.syllables[region].keys())
        except KeyError as e:
            raise ValueError(f"Unsupported dialect: {region}") from e

    def get_ipa_map(self, pos: str = "NOUN", region: str = "lbx") -> Dict[str, str]:
        """
        Get a flat dictionary mapping words to phonemes for a specific POS and region.

        Args:
            pos (str): Part of speech filter.
            region (str): Region code.

        Returns:
            Dict[str, str]: Map of {word: phonemes}.
        """
        if region not in self.ipa:
            raise ValueError(f"Unsupported dialect: {region}")
        homo = self.homographs
        return {
            **{
                word: self.ipa[region][word][pos]
                for word in self.ipa[region]
                if pos in self.ipa[region][word]
            },
            **{
                word: homo[word][pos]
                for word in homo
                if pos in homo[word]
            }}

    @cached_property
    def possible_postags(self) -> Dict[str, List[str]]:
        """
        Get all possible Part-of-Speech tags for words in the lexicon.

        Returns:
            Dict[str, List[str]]: Map of word -> list of available POS tags.
        """
        homo = self.homographs
        return {
            **{
                word: list(self.ipa["lbx"][word].keys())
                for word in self.ipa["lbx"]
            },
            **{
                word: list(homo[word].keys())
                for word in homo
            }}

    @cached_property
    def AO1990(self) -> Dict[str, List[str]]:
        """
        Get a combined dictionary of Old -> New spelling for PT and BR (AO1990).
        """
        return {
            **self.ao_pt, **self.ao_br
        }

    @cached_property
    def silent_p_words(self) -> Set[str]:
        """
        Set of words where 'p' is silent (common in mpc/mpç/mpt clusters before AO1990).

        Returns:
            Set[str]: Words containing silent 'p'.
        """
        clusters = ["mpc", "mpç", "mpt"]
        return set([old_word
                    for c in clusters
                    for old_word, new_words in self.AO1990.items()
                    for new_word in new_words
                    if c in old_word and c not in new_word])

    @cached_property
    def voiced_u_words(self) -> Set[str]:
        """
        Set of words containing the trema 'ü' (indicating voiced 'u' in 'gue'/'gui'/'que'/'qui'),
        based on the Brazilian AO dictionary.

        Returns:
            Set[str]: Words with voiced 'u'.
        """
        # all words in acordo_ortografico_pt_BR.csv containing trema 'ü'
        return set([new_word
                    for old_word, new_words in self.ao_br.items()
                    for new_word in new_words
                    if 'ü' in old_word])

    def normalize_ao1900(self, sentence: str) -> str:
        """
        Normalize a sentence to AO1990 standards.

        Args:
            sentence (str): Input sentence with potentially old spelling.

        Returns:
            str: Sentence with words replaced by their AO1990 equivalents.
        """
        words = [self.AO1990.get(w, [w])[0] for w in sentence.split()]
        return " ".join(words)

    def reverse_ao1900_pt(self, sentence: str) -> str:
        """
        Revert a sentence from AO1990 to pre-agreement PT-PT spelling.

        Args:
            sentence (str): Input sentence in modern spelling.

        Returns:
            str: Sentence using pre-AO1990 PT spelling.
        """
        reverse: Dict[str, str] = {}
        for old_word, new_words in self.ao_pt.items():
            for new_word in new_words:
                reverse[new_word] = old_word

        words = [reverse.get(w, w) for w in sentence.split()]
        return " ".join(words)

    def reverse_ao1900_br(self, sentence: str) -> str:
        """
        Revert a sentence from AO1990 to pre-agreement PT-BR spelling.

        Args:
            sentence (str): Input sentence in modern spelling.

        Returns:
            str: Sentence using pre-AO1990 BR spelling.
        """
        reverse: Dict[str, str] = {}
        for old_word, new_words in self.ao_br.items():
            for new_word in new_words:
                reverse[new_word] = old_word

        words = [reverse.get(w, w) for w in sentence.split()]
        return " ".join(words)


if __name__ == "__main__":
    ph = TugaLexicon()

    print(f"Regions available: {ph.regions}")
    print(f"Silent P words count: {len(ph.silent_p_words)}")
    print(f"Voiced U words count: {len(ph.voiced_u_words)}")
    # Regions available: {'lda', 'mpx', 'rjo', 'rjx', 'lbx', 'lbn', 'dli', 'spx', 'map', 'spo'}
    # Silent P words count: 15
    # Voiced U words count: 283

    # print(ph.possible_postags)
    print(ph.archaic_words)
    print(ph.homographs)

    phoneme_dataset = ph.get_ipa_map()
    # pprint(phoneme_dataset) # Uncomment to see full list

    print(ph.silent_p_words)
    # {'consumpção', 'perempção', 'consumptivo', 'assimptótico', 'assimptotismo', 'inconsumptibilidade',
    # 'perempto', 'consumptor', 'consumptibilidade', 'peremptoriamente', 'consumptível', 'peremptório',
    # 'assumpcionista', 'assimptota', 'peremptoriedade'}

    print(ph.voiced_u_words)
    # {'unguiforme', 'tranquilizante', 'equidilatado', 'equipendência', 'aquilégio', 'anguinha', 'brevilíngue',
    # 'liquescer', 'arguente', 'desfrequentado', 'delinquente', 'linguicídio', 'sociolinguística', 'codelinquir',
    # 'subáqueo', 'quingentaria', 'querquerno', 'equilateral', 'sociolinguista', 'quinquegenciano', 'quinquagésima',
    # 'sagui', 'contiguidade', 'inconsequência', 'anguicida', 'frequentação', 'bálsamo-tranquilo', 'cum-quíbus',
    # 'equevo', 'inequilateral', 'mandiguera', 'obsequente', 'unguento', 'sarigueia', 'arguidor', 'intranquilo',
    # 'equidistante', 'quinquagésimo', 'redarguitivo', 'frequencímetro', 'linguiforme', 'banguezeiro',
    # 'quintimetatársico', 'equipotencial', 'quinquefoliado', 'infrequência', 'frequência', 'coarguida', 'sarigué',
    # 'exequibilidade', 'equiponderante', 'consequencial', 'equitativo', 'quinquídio', 'sequestro', 'mujanguê',
    # 'anguilária', 'unguentar', 'psicolinguística', 'aquicultor', 'consequência', 'equidiferente', 'siliquiforme',
    # 'coarguido', 'sociolinguístico', 'quindecágono', 'ambiguifloro', 'centilíngue', 'tranquilizador', 'intranquilidade',
    # 'quinquedigitado', 'neurolinguístico', 'quinquênio', 'redarguição', 'delinquência', 'maniquera', 'liquidar',
    # 'equissonante', 'linguista', 'relinquir', 'arguir', 'aquifólio', 'cinquentavo', 'inequivocado', 'inequitativo',
    # 'arguitivo', 'cinquentão', 'delinquir', 'codelinquente', 'quinqueangular', 'tranquilizar', 'anguiforme',
    # 'biunguiculado', 'deliquescência', 'equiponderância', 'equiângulo', 'quinquenervado', 'quinquíduo', 'ubiquismo',
    # 'inequivalve', 'frequentar', 'exequível', 'quinquéviro', 'bilinguismo', 'consanguíneo', 'quinquevalente',
    # 'quididativo', 'quercíneo', 'equiangular', 'anguivípera', 'arguido', 'quinquenalidade', 'quingentésimo',
    # 'quinquevirado', 'redarguir', 'equissonância', 'inequiângulo', 'ensanguentado', 'quinquefólio', 'unguinoso',
    # 'quinquevirato', 'quinquelíngue', 'consequente', 'frequentador', 'sanguinolária', 'anguicomado', 'tetequera',
    # 'quinquecapsular', 'unguentário', 'altiloquente', 'sequela', 'grandiloquente', 'sequenciar', 'consequentemente',
    # 'unguentáceo', 'aquicultura', 'exiguidade', 'unguiculado', 'anguina', 'desensanguentar', 'saguiru',
    # 'relinquimento', 'aguista', 'quera', 'linguicida', 'tranquilamente', 'saguim', 'anguígena', 'quinquagenário',
    # 'sequencial', 'aquista', 'quiba', 'equipolência', 'anguissáurio', 'intranquilizador', 'equiprobabilismo',
    # 'loquela', 'neurolinguista', 'sequestrador', 'aquicaldense', 'tranquilo', 'equivalve', 'relinquição',
    # 'equidiferença', 'exiguificar', 'liquidificar', 'deliquescer', 'equimultíplice', 'codelinquência',
    # 'geográfico-linguístico', 'aguentador', 'deliquescente', 'desmilinguido', 'suaviloquente', 'quinquerreme',
    # 'eloquente', 'aquifoliácea', 'equestre', 'delinquencial', 'aquense', 'inexequível', 'eloquência',
    # 'multilinguismo', 'psicolinguista', 'quintuplinérveo', 'sanguícola', 'anguiliforme', 'pinguim', 'inconsequente',
    # 'grandiloquência', 'piraquera', 'redarguente', 'arguição', 'exequendo', 'inexequibilidade', 'falaciloquente',
    # 'unguífero', 'equíssono', 'quinquelobado', 'cinquenta', 'sequestração', 'tricinquentenário', 'cinquentenário',
    # 'queba', 'ubiquitarismo', 'bilíngue', 'tranquilidade', 'linguiça', 'changui', 'ubiquista', 'equipolente',
    # 'quinquenal', 'equipendente', 'quinquevalvular', 'inequilátero', 'equimolecularidade', 'equigranular',
    # 'quinqueviral', 'sequestre', 'vaniloquência', 'quididade', 'sequestrável', 'multilíngue', 'ambiguidade',
    # 'tranquilização', 'sequestrar', 'aquilégia', 'equisseto', 'infrequentado', 'neurolinguística', 'equimolecular',
    # 'subsequência', 'equíssimo', 'liquescente', 'aquíparo', 'longinquidade', 'equiponderar', 'quinquefido',
    # 'sanguinarina', 'vaniloquente', 'quindênio', 'sequenciação', 'quinquedentado', 'infrequente', 'ensanguentar',
    # 'consanguinidade', 'subequilateral', 'catanguera', 'obliquidade', 'psicolinguístico', 'sequência', 'ubiquidade',
    # 'aquícola', 'exequência', 'anguídeo', 'redarguidor', 'tiguera', 'altiloquência', 'equimúltiplo', 'mananguera',
    # 'liquefazer', 'subunguiculado', 'anguite', 'ubiquitário', 'querquetulano', 'Equídeos', 'inequípede', 'exequente',
    # 'iniquidade', 'equidistar', 'equidistância', 'frequentativo', 'desfrequentar', 'quinquevalve', 'liquidando',
    # 'antiguidade', 'equissetácea', 'propinquidade', 'aquífero', 'sequente', 'anguilulado', 'subsequente', 'frequente'}
