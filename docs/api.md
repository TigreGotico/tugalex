# API reference

The whole library is one class.

```python
from tugalex import TugaLexicon
```

## `TugaLexicon(dictionary_path=None)`

| Arg | Type | Default | Meaning |
| --- | --- | --- | --- |
| `dictionary_path` | `Optional[str]` | `None` | Path to a regional CSV. `None` uses the packaged `data/regional_dict.csv`. |

Construction loads the small CSVs eagerly (AO1990 PT/BR, homographs, archaisms).
The large `regional_dict.csv` loads lazily on first access to phonemes,
syllables, or regions, then it is cached on the instance.

### Region codes

ISO dialect codes map to internal region codes through `lang_to_region()`:

| ISO | Region |
| --- | --- |
| `pt-PT` | `lbx` |
| `pt-BR` | `rjx` |
| `pt-AO` | `lda` |
| `pt-MZ` | `mpx` |
| `pt-TL` | `dli` |

The dataset carries more regions than the five mapped above (for example
`rjo`, `lbn`, `spx`, `map`, `spo`). Inspect `lex.regions` for the full set.
Pass any of those raw codes as `region=`.

## Lookup methods

### `get(word, pos="NOUN", region="lbx") -> dict`

Both syllables and phonemes in one call.

```python
lex.get("acordo", pos="NOUN", region="lbx")
# {'syllables': ['a', 'cor', 'do'], 'phonemes': 'ɐˈkoɾdu'}
```

Returns a dict with keys `"syllables"` (`List[str]`, empty if unknown) and
`"phonemes"` (`Optional[str]`, `None` if unknown).

### `get_phonemes(word, pos="NOUN", region="lbx") -> Optional[str]`

The IPA transcription, or `None` when there is no entry. Matching is
case-insensitive. Lookup order:

1. If the word is an archaism, TugaLex first rewrites it to its modern form.
2. If the word is a heterophonic homograph with an entry for `pos`, that
   pronunciation wins (homographs are region-independent).
3. Otherwise TugaLex consults the regional dictionary for `region` and `pos`.

```python
lex.get_phonemes("acordo", pos="NOUN")   # 'ɐˈkoɾdu'
lex.get_phonemes("acordo", pos="VERB")   # 'ɐˈkɔɾdu'
lex.get_phonemes("architecto")           # 'ɐɾ·ki·tˈɛ·tu'  (archaism -> arquiteto)
```

### `get_syllables(word, region="lbx") -> List[str]`

Syllable segments for the word, or an empty list if unknown. Raises
`ValueError` if `region` is not in the loaded dataset.

```python
lex.get_syllables("casa")    # ['ca', 'sa']
```

### `get_wordlist(region="lbx") -> List[str]`

Every word available for a region, sorted. Raises `ValueError` for an unknown
region.

```python
len(lex.get_wordlist("lbx"))   # 53349
```

### `get_ipa_map(pos="NOUN", region="lbx") -> Dict[str, str]`

A flat `{word: phonemes}` map for one POS and region, merging the regional
dictionary with the homograph table. Raises `ValueError` for an unknown
region.

```python
g2p = lex.get_ipa_map(pos="NOUN")
len(g2p)              # 32281
g2p["acordo"]         # 'ɐˈkoɾdu'
```

### `lang_to_region(lang) -> str`

Map an ISO dialect code to its region code. Raises `ValueError` for an
unsupported dialect.

```python
lex.lang_to_region("pt-BR")   # 'rjx'
```

## Orthographic agreement (AO1990)

### `normalize_ao1900(sentence) -> str`

Rewrite each word to its modern AO1990 spelling. Unknown words pass through.

```python
lex.normalize_ao1900("acção óptimo")   # 'ação ótimo'
```

### `reverse_ao1900_pt(sentence) -> str`

Modern spelling back to pre-agreement PT-PT.

```python
lex.reverse_ao1900_pt("ótimo")   # 'óptimo'
```

### `reverse_ao1900_br(sentence) -> str`

Modern spelling back to pre-agreement PT-BR.

```python
lex.reverse_ao1900_br("ato")   # 'ato'
```

## Properties and cached views

| Name | Type | Meaning |
| --- | --- | --- |
| `ipa` | `Dict[region, Dict[word, Dict[POS, str]]]` | Lazy IPA map. |
| `syllables` | `Dict[region, Dict[word, List[str]]]` | Lazy syllable map. |
| `regions` | `Set[str]` | All region codes present in the loaded dataset. |
| `homographs` | `Dict[word, Dict[POS, str]]` | POS-dependent pronunciations. |
| `archaic_words` | `Dict[old, new]` | Pre-20th-century spelling to modern. |
| `possible_postags` | `Dict[word, List[str]]` | POS tags available per word (cached). |
| `AO1990` | `Dict[old, List[str]]` | Combined PT + BR old-to-new spelling map (cached). |
| `silent_p_words` | `Set[str]` | Words with a silent `p` (`mpc`/`mpç`/`mpt` clusters) (cached). |
| `voiced_u_words` | `Set[str]` | Words where `u` is voiced in `gue`/`gui`/`que`/`qui` (former trema) (cached). |

```python
sorted(lex.regions)            # ['dli', 'lbn', 'lbx', 'lda', 'map', ...]
len(lex.AO1990)                # 3923
len(lex.silent_p_words)        # 15
len(lex.voiced_u_words)        # 283
lex.possible_postags["acordo"] # ['NOUN', 'VERB']
```

---
[← Quickstart](quickstart.md) · [Home](../README.md) · [Advanced →](advanced.md)
