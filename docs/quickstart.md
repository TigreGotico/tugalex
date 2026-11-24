# Quickstart

<!-- agent-hint
covers: how to install TugaLex and run each lookup: word list, noun gender, given-name gender and homographs
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

There are no third-party runtime dependencies. The datasets live under `tugalex/data/`, and each one loads the first time a call needs it.

## Look up the gender of a noun

`get_noun_gender` is a static method, so it needs no instance. It returns `"m"`, `"f"`, or `"mf"` for a noun of both genders. A listed exception decides first, and the suffix rules decide the rest. A word that Wiktionary lists only in a closed class and with no gender, such as `ainda` or `para`, gets `None`.

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

## Pronunciation and spelling

TugaLex has no pronunciation dictionary and no spelling conversion. For the pronunciation of Portuguese text, use [orthography2ipa](https://github.com/TigreGotico/orthography2ipa) with the lexicons of `o2i-lexicons`. To convert between Portuguese orthographies, such as pre-AO1990 and AO1990 spelling, use [desacordo_ortografico](https://github.com/TigreGotico/desacordo_ortografico).

---
[Home](index.md) · [API reference →](api.md)
