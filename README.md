# TugaLex 🗣️

**TugaLex** is a comprehensive lexicon handler and linguistic utility for Portuguese dialects. It provides deep data on phoneme transcription (IPA), syllable segmentation, and historical/modern orthographic rules.

Designed for NLP pipelines and linguistics research, it allows you to handle the complexities of Portuguese across different regions and historical agreements with a unified API.

---

## 🌍 Supported Dialects

TugaLex maps standard ISO codes to internal regional datasets:

| ISO Code | Internal Code | Region |
| --- | --- | --- |
| `pt-PT` | `lbx` | Portugal |
| `pt-BR` | `rjx` | Brazil |
| `pt-AO` | `lda` | Angola |
| `pt-MZ` | `mpx` | Mozambique |
| `pt-TL` | `dli` | Timor-Leste |

---

## ✨ Key Features

### 1. Phonemes & Syllables

Retrieve IPA transcriptions and syllable breaks based on the word's Part-of-Speech (POS) and specific region.

```python
from tugalex import TugaLexicon

lex = TugaLexicon()

# Get both syllables and phonemes
info = lex.get("acordo", pos="NOUN", region="lbx")
# Output: {'syllables': ['a', 'cor', 'do'], 'phonemes': 'ɐˈkoɾdu'}

# POS matters!
verb_phonemes = lex.get_phonemes("acordo", pos="VERB")
# Output: 'ɐˈkɔɾdu'
verb_phonemes = lex.get_phonemes("acordo", pos="NOUN")
# Output: 'ɐˈkoɾdu'

```

### 2. Orthographic Agreement (AO1990)

Effortlessly convert text between pre-agreement and post-agreement (AO1990) standards for both Portugal and Brazil.

* **Normalize:** Old spelling → Modern spelling.
* **Reverse:** Modern spelling → Old regional spelling (PT or BR).

```python
normalized = lex.normalize_ao1900(sentence)
```

### 3. Linguistic Insights

TugaLex identifies specific linguistic phenomena programmatically:

* **Homographs:** Words that change pronunciation based on POS (e.g., *sede* (thirst) vs *sede* (headquarters)).
* **Archaic Words:** Mapping 19th-century etymological spellings to modern ones.
* **Silent Letters:** Identifying words with silent 'p' or 'c' common before the 1990 agreement.
* **Voiced 'u':** Detecting words where 'u' is pronounced in 'gue/gui/que/qui' clusters (formerly marked with a trema `ü`).

---

## 🛠 Advanced Usage

### Lazy Loading

TugaLex utilizes lazy loading for its data structures. The heavy CSV files are only read into memory when you first access properties like `.ipa`, `.syllables`, or `.regions`.

### Working with Wordlists

You can extract full regional datasets for custom modeling or validation:

```python
# Get all available words for the Brazilian dialect
br_words = lex.get_wordlist(region="rjx")

# Get a flat map of word -> phonemes for nouns in Portugal
pt_nouns = lex.get_ipa_map(pos="NOUN", region="lbx")

```

---

## 📂 Data Requirements

TugaLex ships the following datasets which contain over 100,000 entries sourced from the [Portal da Língua Portuguesa](http://www.portaldalinguaportuguesa.org).

* `regional_dict.csv`: Phoneme and syllable mappings.
* `acordo_ortografico_pt_PT.csv`: Portugal orthographic mapping.
* `acordo_ortografico_pt_BR.csv`: Brazil orthographic mapping.
