# API reference

<!-- agent-hint
covers: every public name of tugalex with its signature, default and return value, and the replacement for each deprecated name
source: `tugalex/__init__.py`, `tests/test_deprecation.py`
generated: no
verify: d=$(mktemp -d) && sed '/^```/d' docs/api.md > $d/a.txt && python -I -m doctest $d/a.txt
see: `quickstart.md`, `advanced.md`, `index.md`
-->

This page lists the public names of `tugalex`. The package has one class, `TugaLexicon`, and a few module constants. The regional dictionary and the spelling accessors are deprecated, and [Deprecated names](#deprecated-names) lists them with their replacements.

```python
>>> from tugalex import TugaLexicon
```

## `TugaLexicon(dictionary_path=None)`

| Arg | Type | Default | Meaning |
| --- | --- | --- | --- |
| `dictionary_path` | `Optional[str]` | `None` | Path to a regional CSV, plain or gzip (by the `.gz` extension), with the columns `word,phones,syllables,region_code`. Lines that start with `#` are skipped. `None` uses the packaged `data/regional_dict.csv.gz`. |

Construction loads the small CSVs eagerly: the AO1990 tables, the homographs and the archaisms. The large `regional_dict.csv.gz` loads lazily on first access to phonemes, syllables or regions, then it stays cached on the instance. A custom `dictionary_path` is deprecated with the dictionary, and `get_wordlist` warns when it reads one.

## Word list

### `get_wordlist(region="lbx") -> List[str]`

Every word form known for a region, lowercase and sorted. It raises `ValueError` for an unknown region. The word list is not deprecated. With the packaged dictionary it reads `tugalex/data/words.csv.gz`, which holds the word forms of the regional dictionary and no pronunciations, and it does not warn. With a custom `dictionary_path` it returns the words of that dictionary and emits the dictionary `DeprecationWarning`.

```python
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> len(lex.get_wordlist("lbx"))
53147
>>> len(lex.get_wordlist("spx"))
53145
```

Region codes are `lbx` (Portugal), `rjx` (Brazil, Rio de Janeiro), `spx` (Brazil, São Paulo), `lda` (Angola), `mpx` (Mozambique) and `dli` (Timor-Leste).

## Noun gender

### `TugaLexicon.get_noun_gender(word) -> Optional[str]`

The grammatical gender of a Portuguese common noun, singular or plural, in any letter case. It is a static method and needs no instance.

It returns `"m"` or `"f"`, `"mf"` for a noun of both genders, or `None`. It returns `None` for a word that Wiktionary lists only in a closed class and with no gender, and when no rule applies and the word is not listed. A noun of both genders is a common-gender noun (`"o/a artista"`), a noun whose gender changes with its meaning (`"o rádio"`, the set; `"a rádio"`, the station), or a noun whose gender differs between Portugal and Brazil.

The exceptions file `tugalex/data/noun_gender_exceptions.csv.gz` decides first. Then the suffix rules in `tugalex.NOUN_GENDER_SUFFIXES` apply, in order. The suffixes `-ção`, `-são`, `-dade`, `-tude`, `-gem`, `-eza` and `-ise` are feminine. The suffixes `-o` (not `-ão`), `-or` and `-ume` are masculine, and `-a` is feminine. Plural forms of each suffix match too. The exceptions file also lists the closed-class words. A determiner, pronoun, article or contraction has its own gender (`uma`, `da`: `"f"`; `um`, `do`: `"m"`). A word that Wiktionary lists only in a closed class and with no gender, such as an adverb or a preposition, has an empty gender. These words get `None`, and the suffix rules do not apply to them.

```python
>>> from tugalex import TugaLexicon
>>> TugaLexicon.get_noun_gender("lei")
'f'
>>> TugaLexicon.get_noun_gender("dias")
'm'
>>> TugaLexicon.get_noun_gender("nações")
'f'
>>> TugaLexicon.get_noun_gender("artista")
'mf'
>>> TugaLexicon.get_noun_gender("zzk") is None
True
>>> TugaLexicon.get_noun_gender("ainda") is None
True
```

`lei` and `dias` come from the exceptions file, `nações` from the suffix `-ção`. `ainda` is an adverb, so the exceptions file gives it no gender.

### `suffix_noun_gender(word) -> Optional[str]`

The gender that the suffix rules alone give a word, or `None`. It ignores the exceptions file.

```python
>>> from tugalex import suffix_noun_gender
>>> suffix_noun_gender("nações")
'f'
>>> suffix_noun_gender("zzk") is None
True
```

`scripts/build_noun_gender.py` regenerates the exceptions file. It compares the suffix rules with the noun genders of the English Wiktionary and keeps the nouns that the rules get wrong or do not cover, and every noun of both genders. A determiner, pronoun, article, numeral or contraction with a gender keeps that gender, also when the word has a noun entry (`as`, `toda`: `"f"`). Otherwise a word with a noun entry gets the gender of that entry, also when it is a pronoun or an adverb too (`caso`: "o caso"). The script also keeps, with an empty gender, the words that Wiktionary lists only as an adverb, preposition, conjunction, pronoun, determiner, article, contraction or interjection and with no gender, where the suffix rules give a gender. `scripts/noun_gender_overrides.csv` sets the gender of forms that a rare sense would make both-gender: a loanword (`cores`: "a cor", beside the computing term "o core") or an insult (`banana`: "o banana", a weakling). It also sets, with a Priberam citation, the gender of nouns that the English Wiktionary lists only in a closed class (`contra`: "o contra"). An override with an empty gender lets the usual sense decide when a rare noun sense would give a gender (`agora`: "now", beside "o agora").

## Given-name gender

### `TugaLexicon.get_given_name_gender(name) -> Optional[str]`

The grammatical gender of a given name. It is a static method and needs no instance. It returns `"m"` or `"f"`, `"mf"` for a name that both sexes bear, or `None` for a name that is not on the list. The match is exact: write the name as in running text, with its capital letter and accents.

```python
>>> from tugalex import TugaLexicon
>>> TugaLexicon.get_given_name_gender("Isabel")
'f'
>>> TugaLexicon.get_given_name_gender("isabel") is None
True
```

The list is `tugalex/data/given_names.csv.gz`. `scripts/build_given_names.py` regenerates it from Wikidata and the IBGE 2010 census first names, and `scripts/given_name_overrides.csv` corrects the names whose Wikidata items mislead.

## Homographs

### `homographs: Dict[str, Dict[str, str]]`

The POS-dependent pronunciations of the 27 heterophonic homographs, shaped as `{word: {POS: ipa}}`. The table has 55 rows. It is region-independent and not deprecated.

```python
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.homographs["para"]
{'ADP': 'ˈpɐɾɐ', 'VERB': 'ˈpaɾɐ'}
>>> len(lex.homographs), sum(len(tags) for tags in lex.homographs.values())
(27, 55)
```

## Module constants

| Name | Value |
| --- | --- |
| `DICTIONARY_REMOVAL_VERSION` | `"3.0.0"`, the release that removes the regional dictionary and its phoneme API |
| `SPELLING_REMOVAL_VERSION` | `"3.0.0"`, the release that removes the spelling accessors |
| `NOUN_GENDER_SUFFIXES` | the ordered suffix rules of `get_noun_gender`, as `(gender, regex)` pairs |

Both removal versions come from the major version of the package plus one.

## Deprecated names

Every name in this section emits a `DeprecationWarning` and goes away in 3.0.0.

### The regional dictionary

> **Deprecated.** These lookups and the dictionary views `ipa`, `syllables`, `regions` and `possible_postags` emit a `DeprecationWarning`. TugaLex 3.0.0 (`tugalex.DICTIONARY_REMOVAL_VERSION`) removes them. The legacy `tugaphone.dialects` inventories read them and stop working then. For Portuguese pronunciation, use orthography2ipa with the pt-PT lexicon of `o2i-lexicons`.

ISO dialect codes map to region codes through `lang_to_region()`:

| ISO | Region |
| --- | --- |
| `pt-PT` | `lbx` |
| `pt-BR` | `rjx` |
| `pt-AO` | `lda` |
| `pt-MZ` | `mpx` |
| `pt-TL` | `dli` |

The packaged dataset has one more region than the five mapped above: `spx` (São Paulo). Inspect `lex.regions` for the full set, and pass a raw code as `region=`.

#### `get(word, pos="NOUN", region="lbx") -> dict`

Both syllables and phonemes in one call. The dict has the keys `"syllables"` (`List[str]`, empty if unknown) and `"phonemes"` (`Optional[str]`, `None` if unknown).

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.get("acordo", pos="NOUN", region="lbx")
{'syllables': ['a', 'cor', 'do'], 'phonemes': 'ɐˈkoɾdu'}
```

#### `get_phonemes(word, pos="NOUN", region="lbx") -> Optional[str]`

The IPA transcription, or `None` when there is no entry. Matching is case-insensitive. It raises `ValueError` if `region` is not in the loaded dataset. The lookup order is:

1. If the word is an archaism, TugaLex first rewrites it to its modern form.
2. If the word is a heterophonic homograph with an entry for `pos`, that pronunciation wins.
3. Otherwise TugaLex consults the regional dictionary for `region`. That dictionary has one POS-free pronunciation per word, so `pos` does not change the answer.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.get_phonemes("acordo", pos="NOUN")
'ɐˈkoɾdu'
>>> lex.get_phonemes("acordo", pos="VERB")
'ɐˈkɔɾdu'
>>> lex.get_phonemes("architecto")
'ɐɾ·ki·tˈɛ·tu'
>>> lex.get_phonemes("zzzzk") is None
True
```

The archaism `architecto` is looked up as `arquiteto`.

#### `get_syllables(word, region="lbx") -> List[str]`

The syllable segments of the word, or an empty list if unknown. Matching is case-insensitive. It raises `ValueError` if `region` is not in the loaded dataset.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> TugaLexicon().get_syllables("casa")
['ca', 'sa']
```

#### `get_ipa_map(pos="NOUN", region="lbx") -> Dict[str, str]`

A flat `{word: phonemes}` map for one POS and region, merging the regional dictionary with the homograph table. It raises `ValueError` for an unknown region.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> g2p = TugaLexicon().get_ipa_map(pos="NOUN")
>>> len(g2p)
53147
>>> g2p["acordo"]
'ɐˈkoɾdu'
```

#### `lang_to_region(lang) -> str`

Map an ISO dialect code to its region code. It raises `ValueError` for an unsupported dialect.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> TugaLexicon().lang_to_region("pt-BR")
'rjx'
```

#### Dictionary views

| Name | Type | Meaning |
| --- | --- | --- |
| `ipa` | `Dict[region, Dict[word, Dict[POS, str]]]` | Lazy IPA map. |
| `syllables` | `Dict[region, Dict[word, List[str]]]` | Lazy syllable map. |
| `regions` | `Set[str]` | All region codes present in the loaded dataset. |
| `possible_postags` | `Dict[word, List[str]]` | POS tags available per word, cached. A word outside the homograph table has `['']`. |

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> sorted(lex.regions)
['dli', 'lbx', 'lda', 'mpx', 'rjx', 'spx']
>>> lex.possible_postags["acordo"]
['NOUN', 'VERB']
```

### The spelling accessors

> **Deprecated.** desacordo_ortografico owns the spelling table. The four methods and the seven properties below emit a `DeprecationWarning` and return the frozen TugaLex tables. TugaLex 3.0.0 (`tugalex.SPELLING_REMOVAL_VERSION`) removes them. The warning of each name gives its replacement.

| Deprecated name | Replacement |
| --- | --- |
| `modern_spelling`, `normalize_ao1900` | `desacordo_ortografico.convert(text, source, "ao1990-pt") or "ao1990-br"` |
| `reverse_ao1900_pt` | `desacordo_ortografico.convert(text, "ao1990-pt", "pt_1973")` |
| `reverse_ao1900_br` | `desacordo_ortografico.convert(text, "ao1990-br", "br_1971")` |
| `archaic_words`, `archaic_words_br` | the etymological rows of `desacordo_ortografico/data/spelling.json` |
| `ao_pt`, `silent_p_words` | the pt_1973 rows of `desacordo_ortografico/data/spelling.json` |
| `ao_br`, `voiced_u_words` | the br_1971 rows of `desacordo_ortografico/data/spelling.json` |
| `AO1990` | the pt_1973 and br_1971 rows of `desacordo_ortografico/data/spelling.json` |

The method names read `1900`, and they implement the AO1990 agreement.

`normalize_ao1900` and the two `reverse_*` methods split the sentence on whitespace, look up each word exactly as written, and join the result with single spaces. A word with attached punctuation or a capital letter is not converted. `modern_spelling` takes one word and keeps its case.

#### `modern_spelling(word, lang="pt-PT") -> str`

Rewrite one word to its modern spelling in the variety of `lang`. A pre-1911 spelling maps to its modern form, and a pre-AO1990 spelling maps to its AO1990 form. A Brazilian tag uses the pt-BR tables, and every other tag uses the pt-PT tables. A word that is already a valid AO1990 spelling stays as written. When the agreement gives several forms, the form closest to the written word wins. A word in capitals stays in capitals, the first letter follows the written word, and a capital inside the table entry stays. AO1990 removed the hyphen from some compounds, so the result can be several words (`acha-de-armas` gives `acha de armas`). Strip punctuation from the word first.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.modern_spelling("Acção")
'Ação'
>>> lex.modern_spelling("chronico", "pt-PT")
'crónico'
>>> lex.modern_spelling("chronico", "pt-BR")
'crônico'
>>> lex.modern_spelling("sector")
'sector'
>>> lex.modern_spelling("acha-de-armas")
'acha de armas'
```

#### `normalize_ao1900(sentence) -> str`

Rewrite each word to its modern AO1990 spelling. Unknown words pass through. A word with attached punctuation or a capital letter passes through too.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.normalize_ao1900("acção óptimo")
'ação ótimo'
>>> lex.normalize_ao1900("Acção, óptimo!")
'Acção, óptimo!'
```

#### `reverse_ao1900_pt(sentence) -> str`

Modern spelling back to pre-agreement pt-PT.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> TugaLexicon().reverse_ao1900_pt("ótimo")
'óptimo'
```

#### `reverse_ao1900_br(sentence) -> str`

Modern spelling back to pre-agreement pt-BR.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> TugaLexicon().reverse_ao1900_br("ato")
'ato'
```

#### Spelling properties

| Name | Type | Meaning |
| --- | --- | --- |
| `archaic_words` | `Dict[old, new]` | Pre-1911 spelling to its modern pt-PT spelling. |
| `archaic_words_br` | `Dict[old, new]` | Pre-1911 spelling to its modern pt-BR spelling. |
| `ao_pt` | `Dict[old, List[str]]` | Pre-AO1990 pt-PT spelling to its AO1990 spellings. |
| `ao_br` | `Dict[old, List[str]]` | Pre-AO1990 pt-BR spelling to its AO1990 spellings. |
| `AO1990` | `Dict[old, List[str]]` | Combined pt-PT and pt-BR old-to-new spelling map, cached. |
| `silent_p_words` | `Set[str]` | Words with a silent `p` in the `mpc`, `mpç` and `mpt` clusters, cached. |
| `voiced_u_words` | `Set[str]` | Words where `u` is voiced in `gue`, `gui`, `que` and `qui` (the former trema), cached. |

The seven properties are read-only. An assignment such as `lex.AO1990 = {}` raises `AttributeError`.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> len(lex.AO1990), len(lex.silent_p_words), len(lex.voiced_u_words)
(5475, 15, 324)
```

---
[← Quickstart](quickstart.md) · [Home](index.md) · [Advanced →](advanced.md)
