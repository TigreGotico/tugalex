# Advanced

<!-- agent-hint
covers: recipes for grapheme-to-phoneme maps, homographs, spelling tables and the edge cases of the lookups
source: `tugalex/__init__.py`, `tests/test_lexicon.py`
generated: no
verify: d=$(mktemp -d) && sed '/^```/d' docs/advanced.md > $d/v.txt && python -I -m doctest $d/v.txt
see: `api.md`, `quickstart.md`, `index.md`
-->

This page gives recipes and edge cases beyond the basic lookups. The recipes use the public API and the packaged data. Most of them use deprecated names, and each recipe says which name goes away in 3.0.0 and what replaces it.

## Build a grapheme-to-phoneme map for a model

> **Deprecated.** `get_ipa_map()`, `get_phonemes()` and the dictionary views `ipa`, `syllables`, `regions` and `possible_postags` emit a `DeprecationWarning`. TugaLex 3.0.0 removes them. The legacy `tugaphone.dialects` inventories read them and stop working then. For Portuguese pronunciation, use orthography2ipa with the pt-PT lexicon of `o2i-lexicons`.

`get_ipa_map()` returns a flat `{word: phonemes}` dictionary for one POS and region. This is the shape that a G2P training step or a TTS front end wants.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> nouns = lex.get_ipa_map(pos="NOUN", region="lbx")
>>> verbs = lex.get_ipa_map(pos="VERB", region="lbx")
>>> len(nouns), len(verbs)
(53147, 53147)
```

To get every POS for every word, walk `possible_postags`. A word outside the homograph table carries the single tag `""`, its POS-free entry.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> for word, tags in list(lex.possible_postags.items())[:2]:
...     for tag in tags:
...         print(word, repr(tag), lex.get_phonemes(word, pos=tag))
a '' ɐ
a-propósito '' ɐ·pɾu·pˈɔ·zi·tu
```

## Resolve homographs

A homograph has a different transcription for each POS. `homographs` holds the table as `{word: {POS: ipa}}`, and it is not deprecated.

```python
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.homographs["para"]["ADP"]
'ˈpɐɾɐ'
>>> lex.homographs["para"]["VERB"]
'ˈpaɾɐ'
```

`get_phonemes()` consults the homograph table before the regional dictionary, so it needs the POS you mean. The first is the preposition "for", and the second is "he stops".

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.get_phonemes("para", pos="ADP")
'ˈpɐɾɐ'
>>> lex.get_phonemes("para", pos="VERB")
'ˈpaɾɐ'
```

Two readings with the same POS, such as *sede* thirst and *sede* headquarters, need [bifonia](https://github.com/TigreGotico/bifonia).

## Look up an archaism

> **Deprecated.** `get_phonemes()` belongs to the deprecated dictionary API. The archaism table `archaic_words` is deprecated with the spelling accessors, and TugaLex 3.0.0 removes it. Its replacement is the etymological rows of `desacordo_ortografico/data/spelling.json`.

When you ask for the phonemes of a pre-20th-century spelling, TugaLex rewrites it to its modern form first, so you still get a transcription. The lookup reads the archaism table without a spelling warning.

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> TugaLexicon().get_phonemes("architecto")
'ɐɾ·ki·tˈɛ·tu'
```

## Modernise text for a variety

> **Deprecated.** `modern_spelling()` emits a `DeprecationWarning`, and TugaLex 3.0.0 removes it. Its replacement is `desacordo_ortografico.convert(text, source, "ao1990-pt") or "ao1990-br"`.

`desacordo_ortografico.convert()` rewrites a whole text from one norm to another. Pass `etymological` as the source for a pre-1911 spelling, and `pt_1973` or `br_1971` for a pre-AO1990 spelling. Punctuation and capitals stay, so you do not split the text into words first.

```python
>>> from desacordo_ortografico import convert
>>> convert("Pharmacia", "etymological", "ao1990-br")
'Farmácia'
>>> convert("kilometro", "etymological", "ao1990-br")
'quilômetro'
>>> convert("chronico", "etymological", "ao1990-pt")
'crónico'
>>> convert("chronico", "etymological", "ao1990-br")
'crônico'
```

The two norms accent some words differently. AO1990 Base XI, 3º, writes a stressed ⟨e⟩ or ⟨o⟩ before ⟨m⟩ or ⟨n⟩ in a proparoxytone with an acute or a circumflex, by the vowel quality in each norm: `cómodo` and `cômodo`, `fenómeno` and `fenômeno`.

## Round-trip orthography across the AO1990 agreement

> **Deprecated.** `normalize_ao1900()`, `reverse_ao1900_pt()` and `reverse_ao1900_br()` emit a `DeprecationWarning`, and TugaLex 3.0.0 removes them. Their replacements are `desacordo_ortografico.convert(text, source, "ao1990-pt") or "ao1990-br"`, `desacordo_ortografico.convert(text, "ao1990-pt", "pt_1973")` and `desacordo_ortografico.convert(text, "ao1990-br", "br_1971")`.

`convert()` goes from old to modern spelling and back, with one norm for each standard. Unmapped words pass through unchanged.

```python
>>> from desacordo_ortografico import convert
>>> convert("acção óptimo", "pt_1973", "ao1990-pt")
'ação ótimo'
>>> convert("ótimo", "ao1990-pt", "pt_1973")
'óptimo'
>>> convert("ótimo", "ao1990-br", "br_1971")
'ótimo'
```

Portugal and Brazil diverge. A word can revert differently for each standard, so each standard has its own pre-AO1990 norm.

## Detect spelling phenomena

> **Deprecated.** `silent_p_words` and `voiced_u_words` emit a `DeprecationWarning`, and TugaLex 3.0.0 removes them. Their replacements are the pt_1973 rows and the br_1971 rows of `desacordo_ortografico/data/spelling.json`.

Each row of the desacordo_ortografico spelling table maps `form`, written in the norm `era`, to `value`, written in the norm `target`. A cell with two AO1990 forms joins them with `|`. These two sets hold the same words as the deprecated TugaLex sets.

```python
>>> import json
>>> from importlib.resources import files
>>> table = files("desacordo_ortografico").joinpath("data/spelling.json")
>>> rows = json.loads(table.read_text(encoding="utf-8"))["rows"]
>>> silent_p = {
...     row["form"]
...     for row in rows
...     if row["era"] == "pt_1973"
...     for cluster in ("mpc", "mpç", "mpt")
...     for value in row["value"].split("|")
...     if cluster in row["form"] and cluster not in value
... }
>>> voiced_u = {
...     value
...     for row in rows
...     if row["era"] == "br_1971" and "ü" in row["form"]
...     for value in row["value"].split("|")
... }
>>> sorted(silent_p)[:3]
['assimptota', 'assimptotismo', 'assimptótico']
>>> sorted(voiced_u)[:3]
['Equídeos', 'aguentador', 'aguista']
```

Use them to flag tokens that need special attention in a pronunciation or spell-checking pipeline.

## Gotchas

The first four gotchas concern the deprecated dictionary API.

- **POS casing.** The homograph table uses uppercase tags (`NOUN`, `VERB`, `ADJ`, `ADP`). A lowercase tag misses the homograph table and falls back to the POS-free regional entry, silently.
- **Unknown words return falsy values, they do not raise.** `get_phonemes` returns `None` and `get_syllables` returns `[]` for a word that is not in the dataset. An unsupported region raises `ValueError` from `get_phonemes`, `get_syllables`, `get_wordlist`, `get_ipa_map` and `lang_to_region`.
- **The first touch is slow.** The first access to `ipa`, `syllables`, `regions`, or any method that uses them parses the large CSV. Construct one `TugaLexicon` and reuse it across calls.
- **Two transcription styles.** The homograph table writes the stress mark before the syllable (`ɐˈkoɾdu`). The regional dictionary marks syllables with `·` and writes the stress mark before the vowel (`ɐ·kˈoɾ·du`).
- **Method names read `1900`.** The deprecated `normalize_ao1900`, `reverse_ao1900_pt` and `reverse_ao1900_br` all implement the AO1990 agreement.
- **The deprecated AO1990 methods match whole whitespace-separated words.** A word with attached punctuation or a capital letter is not converted, and runs of spaces become one space. `desacordo_ortografico.convert()` keeps punctuation and capitals.

The POS casing gotcha, shown:

```python
>>> import warnings
>>> warnings.simplefilter("ignore")
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.get_phonemes("acordo", pos="noun")
'ɐ·kˈoɾ·du'
>>> lex.get_phonemes("acordo", pos="NOUN")
'ɐˈkoɾdu'
```

---
[← API reference](api.md) · [Home](index.md) · [Datasets →](datasets.md)
