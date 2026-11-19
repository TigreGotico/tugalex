# Quickstart

`tugalex` is a lexicon handler for Portuguese dialects. One class,
`TugaLexicon`, answers questions about a Portuguese word: how is it
pronounced (IPA), how does it break into syllables, how does it spell across
the AO1990 orthographic agreement, and which grammatical gender a noun or a
given name has. All data ships in the package as CSV and gzip CSV. There is
no network access, no model files, and no API keys.

## 1. Install

```bash
pip install --pre tugalex
```

There are no third-party runtime dependencies. The datasets live under
`tugalex/data/`. `regional_dict.csv.gz` is the large one (about 2.5 MB
compressed) and loads lazily the first time you touch phonemes, syllables,
or regions.

## 2. The one thing to understand

> **Deprecated.** The phoneme and syllable lookups below and the dictionary views `ipa`,
> `syllables`, `regions` and `possible_postags` emit a `DeprecationWarning`.
> TugaLex 3.0.0 removes them. The legacy `tugaphone.dialects`
> inventories read them and stop working then. For Portuguese
> pronunciation, use orthography2ipa with the pt-PT lexicon of
> `o2i-lexicons`.

Everything hangs off a single object. Construct it once and reuse it. The
heavy CSV is parsed on first access and cached on the instance.

```python
from tugalex import TugaLexicon

lex = TugaLexicon()

info = lex.get("acordo", pos="NOUN", region="lbx")
print(info)   # {'syllables': ['a', 'cor', 'do'], 'phonemes': 'ɐˈkoɾdu'}
```

`get()` is the convenience call. Under it sit two focused lookups,
`get_syllables()` and `get_phonemes()`, which you can call directly when you
only need one half.

## 3. Part-of-speech matters

Portuguese has heterophonic homographs: same spelling, different sound
depending on the grammatical role. TugaLex keys 27 of them by POS. Pass the
right `pos` and you get the right vowel. For every other word the POS does
not change the answer.

```python
print(lex.get_phonemes("acordo", pos="NOUN"))   # ɐˈkoɾdu  (the noun: an accord)
print(lex.get_phonemes("acordo", pos="VERB"))   # ɐˈkɔɾdu  (the verb: I wake up)
```

POS tags are uppercase Universal-Dependencies style: `NOUN`, `VERB`, `ADJ`,
`ADP`, and so on. Ask a word which tags it carries with
`lex.possible_postags["acordo"]`, which returns `['NOUN', 'VERB']`. A word
outside the homograph table returns `['']`, its POS-free entry.

## 4. Pick a dialect

The dataset is region-indexed. Public ISO dialect codes map to internal
region codes through `lang_to_region()`:

```python
lex.lang_to_region("pt-PT")   # 'lbx'  (Portugal)
lex.lang_to_region("pt-BR")   # 'rjx'  (Brazil)
```

| ISO code | Region | Place |
| --- | --- | --- |
| `pt-PT` | `lbx` | Portugal |
| `pt-BR` | `rjx` | Brazil |
| `pt-AO` | `lda` | Angola |
| `pt-MZ` | `mpx` | Mozambique |
| `pt-TL` | `dli` | Timor-Leste |
| none | `spx` | Brazil (São Paulo) |

Pass the region code straight into the lookups:

```python
lex.get_phonemes("acordo", pos="NOUN", region="rjx")
```

## 5. Orthographic agreement (AO1990)

> **Deprecated.** desacordo_ortografico owns the spelling table. The TugaLex
> AO1990 methods (`modern_spelling`, `normalize_ao1900`, `reverse_ao1900_pt`
> and `reverse_ao1900_br`) emit a `DeprecationWarning` and return the frozen
> TugaLex tables. TugaLex 3.0.0 removes them. The
> [API reference](api.md#orthographic-agreement-ao1990) names the replacement
> of each one.

Convert between pre-agreement and modern spelling with
`desacordo_ortografico.convert(text, source, target)`. Install it with
`pip install --pre desacordo_ortografico`.

```python
from desacordo_ortografico import convert

convert("acção óptimo", "pt_1973", "ao1990-pt")   # 'ação ótimo'    (old to modern)
convert("ótimo", "ao1990-pt", "pt_1973")          # 'óptimo'        (modern to old PT-PT)
convert("o ato", "ao1990-br", "br_1971")          # 'o ato'         (modern to old PT-BR)
```

Words with no mapping pass through unchanged. Punctuation and capitals stay:
`convert("Acção, óptimo!", "pt_1973", "ao1990-pt")` gives `'Ação, ótimo!'`.

---
[Home](../README.md) · [API reference →](api.md)
