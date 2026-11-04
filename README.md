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

`spx` has no ISO alias. Pass it as `region="spx"`.

The regional dictionary ships as a slim gzip extract (word, phones,
syllables, region) of the [unified Portuguese pronunciation lexicon](https://huggingface.co/datasets/TigreGotico/portuguese-unified-pronunciation-lexicon),
with 53,147 to 53,148 words in each region. Regenerate it with
`python scripts/build_regional_dict.py`. The regional dictionary has no
part of speech: each word has one pronunciation per region, and it answers
every POS query. Only the heterophonic homograph table is keyed by POS.

---

## Key Features

### 1. Phonemes & Syllables

Retrieve IPA transcriptions and syllable breaks for a word in a region. For the 27 heterophonic homographs, the part of speech (POS) selects the pronunciation.

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
lex.normalize_ao1900("acção óptimo")   # 'ação ótimo'
lex.reverse_ao1900_pt("ótimo")         # 'óptimo'
```

The conversion splits on whitespace and matches each word exactly, so a word with attached punctuation or a capital letter is not converted ([#46](https://github.com/TigreGotico/tugalex/issues/46)).

### 3. Linguistic Insights

TugaLex identifies specific linguistic phenomena programmatically:

* **Homographs:** Words that change pronunciation with POS (e.g., *acordo* the noun `ɐˈkoɾdu` vs *acordo* the verb `ɐˈkɔɾdu`). Two readings with the same POS, such as *sede* thirst vs headquarters, need [bifonia](https://github.com/TigreGotico/bifonia).
* **Archaic Words:** Mapping 19th-century etymological spellings to modern ones.
* **Silent Letters:** Identifying words with a silent 'p' in the `mpc`/`mpç`/`mpt` clusters of pre-1990 spelling. Silent 'c' detection does not exist ([#2](https://github.com/TigreGotico/tugalex/issues/2)).
* **Voiced 'u':** Detecting words where 'u' is pronounced in 'gue/gui/que/qui' clusters (formerly marked with a trema `ü`).

### 4. Noun Gender

Get the grammatical gender of a Portuguese common noun, singular or plural.
Suffix rules decide most nouns, and a list of exceptions decides the rest.

```python
TugaLexicon.get_noun_gender("lei")       # 'f'
TugaLexicon.get_noun_gender("dias")      # 'm'
TugaLexicon.get_noun_gender("artista")   # 'mf' (both genders)
```

### 5. Given-Name Gender

Get the grammatical gender of a given name, written as in running text.
The list holds regnal names, the Brazilian census names that match a
Wikidata given name, and the Wikidata given names marked Portuguese.

```python
TugaLexicon.get_given_name_gender("Isabel")   # 'f'
TugaLexicon.get_given_name_gender("Afonso")   # 'm'
TugaLexicon.get_given_name_gender("Darci")    # 'mf' (both genders)
TugaLexicon.get_given_name_gender("Raio")     # None
```

---

## Datasets

TugaLex ships the following datasets under `tugalex/data/`.

* `regional_dict.csv.gz`: phoneme and syllable mappings, 318,884 rows for 53,150 distinct words in six regions. `scripts/build_regional_dict.py` builds it from the [unified Portuguese pronunciation lexicon](https://huggingface.co/datasets/TigreGotico/portuguese-unified-pronunciation-lexicon) and keeps six of its [Portal da Língua Portuguesa](http://www.portaldalinguaportuguesa.org) regions. The scraped Portal data with all ten regional variants is the [`portuguese_phonetic_lexicon`](https://huggingface.co/datasets/TigreGotico/portuguese_phonetic_lexicon) dataset.
* `heterophonic_homographs.csv`: 27 words pronounced differently depending on POS, 55 rows.
* [`acordo_ortografico_pt_PT.csv`](https://huggingface.co/datasets/TigreGotico/AO1990_pt-PT): Portugal old orthographic spellings.
* [`acordo_ortografico_pt_BR.csv`](https://huggingface.co/datasets/TigreGotico/AO1990_pt-BR): Brazil old orthographic spellings.
* [`archaisms.csv`](https://huggingface.co/datasets/TigreGotico/archaisms_pt): normalized words from before the 20th century.

`noun_gender_exceptions.csv.gz` lists the nouns whose gender the suffix rules
get wrong or do not cover, and the nouns of both genders.
`scripts/build_noun_gender.py` regenerates it from the noun genders of the
English Wiktionary.

`given_names.csv.gz` lists given names with their gender.
`scripts/build_given_names.py` regenerates it from Wikidata (CC0) and the IBGE
2010 census first names published by datasets-br/prenomes (ODC-PDDL-1.0).
`scripts/given_name_overrides.csv` corrects the names whose Wikidata items
mislead, each with its evidence.

---

## Install

```bash
pip install --pre tugalex
```

TugaLex publishes alpha releases from the `dev` branch. Use `--pre` to get the API that this README describes. TugaLex has no third-party runtime dependencies. All datasets ship inside the package under `tugalex/data/`.

---

## Related Projects

TugaLex is one piece of the TigreGotico Portuguese NLP stack:

* [tugaphone](https://github.com/TigreGotico/tugaphone): phonemizes arbitrary Portuguese text across dialects, using TugaLex plus a rule-based fallback. tugaphone depends on TugaLex.
* [bifonia](https://github.com/TigreGotico/bifonia): picks the reading of a heterophonic homograph by meaning, including the same-POS pairs that the TugaLex homograph table cannot separate.
* [tugamorph](https://github.com/TigreGotico/tugamorph): rule-based morphological analyzer for Portuguese.
* [tugatagger](https://github.com/TigreGotico/tugatagger): Part-of-Speech tagging wrapper for Portuguese. Its `lexicon` extra installs TugaLex.
* [desacordo_ortografico](https://github.com/TigreGotico/desacordo_ortografico): detects and converts between Portuguese orthographies, including the AO1990 reform.

---

## Documentation

Read the pages in this order. Each page links to the next one.

1. [`docs/quickstart.md`](docs/quickstart.md): install, the first lookups, dialects and AO1990.
2. [`docs/api.md`](docs/api.md): every public method and property.
3. [`docs/advanced.md`](docs/advanced.md): recipes and gotchas.

Runnable scripts for each feature are in [`examples/`](examples).

---

## Development

| path | contents |
| --- | --- |
| `tugalex/__init__.py` | the `TugaLexicon` class and the noun-gender suffix rules |
| `tugalex/data/` | the packaged datasets |
| `scripts/` | the build scripts for `regional_dict.csv.gz`, `noun_gender_exceptions.csv.gz` and `given_names.csv.gz`, and their override files |
| `tests/` | the pytest suite |
| `examples/` | one runnable script per feature |
| `*.ipynb` | analysis notebooks for the phonetic lexicon and the AO1990 tables |

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python --prerelease=allow -e ".[test]"
.venv/bin/python -m pytest tests
```

CI runs the same suite on Python 3.11 to 3.14 (`.github/workflows/build-tests.yml`). The build scripts download their sources, so run them only to regenerate a dataset. Each row of `scripts/given_name_overrides.csv` carries its evidence in the `reason` column.

---

## License

TugaLex is released under the [Apache License 2.0](LICENSE).
