# TugaLex

**TugaLex** is a lexicon handler and linguistic utility for Portuguese dialects. It provides data on phoneme transcription (IPA), syllable segmentation, and historical and modern orthographic rules.

It gives NLP pipelines and linguistics research a single API for the differences between Portuguese regions and historical spelling agreements.

> **Deprecated: the regional pronunciation dictionary.** The phoneme and
> syllable API (`get`, `get_phonemes`, `get_syllables`, `get_ipa_map`,
> `lang_to_region`, `ipa`, `syllables`, `regions` and `possible_postags`)
> emits a `DeprecationWarning`. TugaLex 3.0.0
> (`tugalex.DICTIONARY_REMOVAL_VERSION`)
> removes it. The legacy `tugaphone.dialects` inventories read it and
> stop working then. For Portuguese pronunciation, use
> [orthography2ipa](https://github.com/TigreGotico/orthography2ipa) with the
> pt-PT lexicon of `o2i-lexicons` (`orthography2ipa.use_packaged_lexicons`).

> **Deprecated: the spelling accessors.** desacordo_ortografico owns the
> spelling table. The eleven names in the table below emit a
> `DeprecationWarning` and return the frozen TugaLex tables. TugaLex 3.0.0
> (`tugalex.SPELLING_REMOVAL_VERSION`) removes them. Each warning names the
> [desacordo_ortografico](https://github.com/TigreGotico/desacordo_ortografico)
> replacement. `convert(text, source, target)` converts text, and the rows of
> `desacordo_ortografico/data/spelling.json` hold the archaism and AO1990
> tables.
>
> | Deprecated name | Replacement |
> | --- | --- |
> | `archaic_words`, `archaic_words_br` | the etymological rows of `desacordo_ortografico/data/spelling.json` |
> | `ao_pt`, `silent_p_words` | the pt_1973 rows of `desacordo_ortografico/data/spelling.json` |
> | `ao_br`, `voiced_u_words` | the br_1971 rows of `desacordo_ortografico/data/spelling.json` |
> | `AO1990` | the pt_1973 and br_1971 rows of `desacordo_ortografico/data/spelling.json` |
> | `modern_spelling`, `normalize_ao1900` | `desacordo_ortografico.convert(text, source, "ao1990-pt") or "ao1990-br"` |
> | `reverse_ao1900_pt` | `desacordo_ortografico.convert(text, "ao1990-pt", "pt_1973")` |
> | `reverse_ao1900_br` | `desacordo_ortografico.convert(text, "ao1990-br", "br_1971")` |
>
> The seven properties in the table are read-only. An assignment such as
> `lex.ao_pt = {}` raises `AttributeError`.
>
> The word list (`get_wordlist`), the noun gender and the given-name gender
> stay.

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
with 53,144 to 53,147 words in each region. Regenerate it with
`python scripts/build_regional_dict.py`, which reads the lexicon revision
pinned in the script. The regional dictionary has no
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

The TugaLex AO1990 methods are deprecated. Convert text with
[desacordo_ortografico](https://github.com/TigreGotico/desacordo_ortografico),
which keeps punctuation and capitals:

```python
from desacordo_ortografico import convert

convert("Acção, óptimo!", "pt_1973", "ao1990-pt")       # 'Ação, ótimo!'
convert("ótimo", "ao1990-pt", "pt_1973")                # 'óptimo'
convert("Pharmacia", "etymological", "ao1990-br")       # 'Farmácia'
convert("chronico", "etymological", "ao1990-pt")        # 'crónico'
convert("chronico", "etymological", "ao1990-br")        # 'crônico'
```

[`docs/api.md`](docs/api.md) documents the deprecated TugaLex methods until
3.0.0 removes them.

### 3. Linguistic Insights

TugaLex identifies specific linguistic phenomena programmatically. The archaism, silent-letter and voiced-u sets are deprecated with the spelling accessors. The recipe in [`docs/advanced.md`](docs/advanced.md) reads the same sets from the desacordo_ortografico spelling table.

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

* `regional_dict.csv.gz`: phoneme and syllable mappings, 318,872 rows for 53,148 distinct words in six regions. `scripts/build_regional_dict.py` builds it from the [unified Portuguese pronunciation lexicon](https://huggingface.co/datasets/TigreGotico/portuguese-unified-pronunciation-lexicon) and keeps six of its [Portal da Língua Portuguesa](http://www.portaldalinguaportuguesa.org) regions. The scraped Portal data with all ten regional variants is the [`portuguese_phonetic_lexicon`](https://huggingface.co/datasets/TigreGotico/portuguese_phonetic_lexicon) dataset.
* `words.csv.gz`: the word forms of `regional_dict.csv.gz` with the regions that list each one, and no pronunciations. `get_wordlist` reads it, and it stays when the regional dictionary goes. `scripts/build_wordlist.py` builds it from the regional dictionary.
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

* [tugaphone](https://github.com/TigreGotico/tugaphone): phonemizes Portuguese text per dialect. It runs the lect specs of [orthography2ipa](https://github.com/TigreGotico/orthography2ipa) and the lexicons of `o2i-lexicons`. It depends on TugaLex, and its text normalization reads the TugaLex noun and given-name genders. Its legacy `tugaphone.dialects` inventories read the deprecated regional dictionary.
* [bifonia](https://github.com/TigreGotico/bifonia): picks the reading of a heterophonic homograph by meaning, including the same-POS pairs that the TugaLex homograph table cannot separate.
* [tugamorph](https://github.com/TigreGotico/tugamorph): rule-based morphological analyzer for Portuguese.
* [tugatagger](https://github.com/TigreGotico/tugatagger): Part-of-Speech tagging wrapper for Portuguese. Its `lexicon` extra installs TugaLex.
* [desacordo_ortografico](https://github.com/TigreGotico/desacordo_ortografico): detects and converts between Portuguese orthographies, including the AO1990 reform. It reads the TugaLex word list, and its spelling table holds the archaism and AO1990 rows that the deprecated TugaLex spelling accessors return.

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
| `scripts/` | the build scripts for `regional_dict.csv.gz`, `words.csv.gz`, `noun_gender_exceptions.csv.gz` and `given_names.csv.gz`, and their override files |
| `tests/` | the pytest suite |
| `examples/` | one runnable script per feature |
| `*.ipynb` | analysis notebooks for the phonetic lexicon and the AO1990 tables |

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python --prerelease=allow -e ".[test]"
.venv/bin/python -m pytest tests
```

CI runs the same suite on Python 3.11 to 3.14 (`.github/workflows/build-tests.yml`). On each pull request, `.github/workflows/downstream-tests.yml` installs the TugaLex of the pull request with desacordo_ortografico from its `dev` branch and runs the desacordo_ortografico suite on the same Python versions. A `DeprecationWarning` fails that job. The build scripts download their sources, so run them only to regenerate a dataset. Each row of `scripts/given_name_overrides.csv` carries its evidence in the `reason` column.

---

## License

TugaLex is released under the [Apache License 2.0](LICENSE).
