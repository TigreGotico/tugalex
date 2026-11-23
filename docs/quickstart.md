# Quickstart

<!-- agent-hint
covers: how to install TugaLex and run each lookup: word list, noun gender, given-name gender, homographs, and the deprecated dictionary and spelling calls
source: `tugalex/__init__.py:TugaLexicon`, `tugalex/data/`
generated: no
verify: d=$(mktemp -d) && sed '/^```/d' docs/quickstart.md > $d/q.txt && python -I -m doctest $d/q.txt
see: `api.md`, `advanced.md`, `index.md`
-->

This page walks through the lookups of `TugaLexicon`. All data ships in the package as CSV and gzip CSV. TugaLex needs no network access, no model files and no API keys.

## Install

```bash
pip install --pre tugalex
```

There are no third-party runtime dependencies. The datasets live under `tugalex/data/`. `regional_dict.csv.gz` is the large one, about 2.5 MB compressed. It loads the first time a call needs phonemes, syllables or regions.

## Look up the gender of a noun

`get_noun_gender` is a static method, so it needs no instance. It returns `"m"`, `"f"`, or `"mf"` for a noun of both genders. A listed exception decides first, and the suffix rules decide the rest. A word that is never a noun, such as `ainda` or `para`, gets `None`.

```python
>>> from tugalex import TugaLexicon
>>> TugaLexicon.get_noun_gender("lei")
'f'
>>> TugaLexicon.get_noun_gender("nações")
'f'
>>> TugaLexicon.get_noun_gender("artista")
'mf'
>>> TugaLexicon.get_noun_gender("zzk") is None
True
>>> TugaLexicon.get_noun_gender("para") is None
True
```

## Look up the gender of a given name

Write the name as in running text, with its capital letter and accents. The match is exact.

```python
>>> from tugalex import TugaLexicon
>>> TugaLexicon.get_given_name_gender("Isabel")
'f'
>>> TugaLexicon.get_given_name_gender("Darci")
'mf'
>>> TugaLexicon.get_given_name_gender("isabel") is None
True
```

## Read the word list

`get_wordlist(region)` returns every word form of a region, lowercase and sorted. The default region is `lbx`.

```python
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> len(lex.get_wordlist("lbx"))
53147
>>> len(lex.get_wordlist("spx"))
53145
```

## Part of speech decides a homograph

Portuguese has heterophonic homographs: the same spelling, a different sound for each grammatical role. TugaLex keys 27 of them by part of speech (POS). `homographs` maps each word to its POS and its IPA transcription.

```python
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.homographs["acordo"]
{'NOUN': 'ɐˈkoɾdu', 'VERB': 'ɐˈkɔɾdu'}
>>> len(lex.homographs)
27
```

POS tags are uppercase Universal-Dependencies style: `NOUN`, `VERB`, `ADJ`, `ADP`, and so on.

## Deprecated: phonemes, syllables and dialects

> **Deprecated.** The phoneme and syllable lookups below and the dictionary views `ipa`, `syllables`, `regions` and `possible_postags` emit a `DeprecationWarning`. TugaLex 3.0.0 removes them. The legacy `tugaphone.dialects` inventories read them and stop working then. For Portuguese pronunciation, use orthography2ipa with the pt-PT lexicon of `o2i-lexicons`.

`get()` returns the syllables and the phonemes of a word for a region. `get_syllables()` and `get_phonemes()` return one half each.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.get("acordo", pos="NOUN", region="lbx")
{'syllables': ['a', 'cor', 'do'], 'phonemes': 'ɐˈkoɾdu'}
>>> lex.get_phonemes("acordo", pos="NOUN")
'ɐˈkoɾdu'
>>> lex.get_phonemes("acordo", pos="VERB")
'ɐˈkɔɾdu'
>>> lex.get_syllables("casa")
['ca', 'sa']
```

The dataset is region-indexed. `lang_to_region()` maps a public ISO dialect code to the internal region code, and the lookups take the region code.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.lang_to_region("pt-PT"), lex.lang_to_region("pt-BR")
('lbx', 'rjx')
>>> lex.get_phonemes("acordo", pos="NOUN", region="rjx")
'ɐˈkoɾdu'
>>> lex.possible_postags["acordo"]
['NOUN', 'VERB']
```

| ISO code | Region | Place |
| --- | --- | --- |
| `pt-PT` | `lbx` | Portugal |
| `pt-BR` | `rjx` | Brazil |
| `pt-AO` | `lda` | Angola |
| `pt-MZ` | `mpx` | Mozambique |
| `pt-TL` | `dli` | Timor-Leste |
| none | `spx` | Brazil (São Paulo) |

`spx` has no ISO alias. Pass it as `region="spx"`. A word outside the homograph table has the single tag `''` in `possible_postags`, its POS-free entry.

## Deprecated: spelling conversion

> **Deprecated.** desacordo_ortografico owns the spelling table. The TugaLex spelling methods (`modern_spelling`, `normalize_ao1900`, `reverse_ao1900_pt` and `reverse_ao1900_br`) emit a `DeprecationWarning` and return the frozen TugaLex tables. TugaLex 3.0.0 removes them. The [API reference](api.md#deprecated-names) names the replacement of each one.

Install the replacement with `pip install --pre desacordo_ortografico`, and call `convert(text, source, target)`.

```python
>>> from desacordo_ortografico import convert
>>> convert("acção óptimo", "pt_1973", "ao1990-pt")
'ação ótimo'
>>> convert("ótimo", "ao1990-pt", "pt_1973")
'óptimo'
>>> convert("o ato", "ao1990-br", "br_1971")
'o ato'
>>> convert("Acção, óptimo!", "pt_1973", "ao1990-pt")
'Ação, ótimo!'
```

A word with no mapping passes through unchanged. Punctuation and capitals stay.

---
[Home](index.md) · [API reference →](api.md)
