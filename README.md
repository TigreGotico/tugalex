# TugaLex

**TugaLex** is a lexicon handler and linguistic utility for Portuguese dialects. It provides data on phoneme transcription (IPA), syllable segmentation, and historical and modern orthographic rules.

It gives NLP pipelines and linguistics research a single API for the differences between Portuguese regions and historical spelling agreements.

---

## Supported Dialects

TugaLex maps standard ISO codes to internal regional datasets:

| ISO Code | Internal Code | Region |
| --- | --- | --- |
| `pt-PT` | `lbx` | Portugal (Lisbon) |
| `pt-BR` | `rjx` | Brazil (Rio de Janeiro) |
| n/a | `spx` | Brazil (São Paulo) |
| `pt-AO` | `lda` | Angola (Luanda) |
| `pt-MZ` | `mpx` | Mozambique (Maputo) |
| `pt-TL` | `dli` | Timor-Leste (Díli) |

The regional dictionary ships as a slim gzip extract (word, POS, phones,
syllables, region) of the [unified Portuguese pronunciation lexicon](https://huggingface.co/datasets/TigreGotico/portuguese-unified-pronunciation-lexicon).
Regenerate it with `python scripts/build_regional_dict.py`. Words whose
pronunciation does not vary by part of speech carry a single POS-invariant
entry that answers every POS query.

---

## Key Features

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

Convert text between pre-agreement and post-agreement (AO1990) spelling for Portugal and Brazil.

* **Normalize:** Old spelling to modern spelling.
* **Reverse:** Modern spelling to old regional spelling (PT or BR).

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

## Datasets

TugaLex ships the following datasets. Together they contain over 100,000 entries sourced from the [Portal da Língua Portuguesa](http://www.portaldalinguaportuguesa.org).

* [`regional_dict.csv`](https://huggingface.co/datasets/TigreGotico/portuguese_phonetic_lexicon): Phoneme and syllable mappings.
* [`heterophonic_homographs.csv`](https://huggingface.co/datasets/TigreGotico/heterophonic_homographs_pt): words pronounced differently depending on postag.
* [`acordo_ortografico_pt_PT.csv`](https://huggingface.co/datasets/TigreGotico/AO1990_pt-PT): Portugal old orthographic spellings.
* [`acordo_ortografico_pt_BR.csv`](https://huggingface.co/datasets/TigreGotico/AO1990_pt-BR): Brazil old orthographic spellings.
* [`archaisms.csv`](https://huggingface.co/datasets/TigreGotico/archaisms_pt): normalized words from before the 20th century.

---

## Install

```bash
pip install -e .
```

TugaLex has no third-party runtime dependencies. All datasets ship inside the package under `tugalex/data/`.

---

## Related Projects

TugaLex is one piece of the TigreGotico Portuguese NLP stack:

* [tugaphone](https://github.com/TigreGotico/tugaphone): phonemizes arbitrary Portuguese text across dialects, using TugaLex plus a rule-based fallback.
* [tugamorph](https://github.com/TigreGotico/tugamorph): rule-based morphological analyzer for Portuguese.
* [tugatagger](https://github.com/TigreGotico/tugatagger): Part-of-Speech tagging wrapper for Portuguese.
* [desacordo_ortografico](https://github.com/TigreGotico/desacordo_ortografico): detects and converts between Portuguese orthographies, including the AO1990 reform.

---

## License

TugaLex is released under the [Apache License 2.0](LICENSE).
