# Quickstart

`tugalex` is a lexicon handler for Portuguese dialects. One class,
`TugaLexicon`, answers three kinds of question about a Portuguese word: how is
it pronounced (IPA), how does it break into syllables, and how does it spell
across the AO1990 orthographic agreement. All data ships in the package as
CSV. There is no network access, no model files, and no API keys.

## 1. Install

```bash
pip install -e .
```

There are no third-party runtime dependencies. The datasets live under
`tugalex/data/`. `regional_dict.csv` is the large one (about 49 MB) and loads
lazily the first time you touch phonemes, syllables, or regions.

## 2. The one thing to understand

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
depending on the grammatical role. Pass the right `pos` and you get the right
vowel.

```python
print(lex.get_phonemes("acordo", pos="NOUN"))   # ɐˈkoɾdu  (the noun: an accord)
print(lex.get_phonemes("acordo", pos="VERB"))   # ɐˈkɔɾdu  (the verb: I wake up)
```

POS tags are uppercase Universal-Dependencies style: `NOUN`, `VERB`, `ADJ`,
`ADP`, and so on. Ask a word which tags it carries with
`lex.possible_postags["acordo"]`, which returns `['NOUN', 'VERB']`.

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

Pass the region code straight into the lookups:

```python
lex.get_phonemes("acordo", pos="NOUN", region="rjx")
```

## 5. Orthographic agreement (AO1990)

Convert between pre-agreement and modern spelling in both directions:

```python
lex.normalize_ao1900("acção óptimo")    # 'ação ótimo'   (old to modern)
lex.reverse_ao1900_pt("ótimo")          # 'óptimo'        (modern to old PT-PT)
lex.reverse_ao1900_br("ato")            # 'ato'           (modern to old PT-BR)
```

Words with no mapping pass through unchanged, so it is safe to run on whole
sentences.

---
[Home](../README.md) · [API reference →](api.md)
