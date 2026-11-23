# Datasets and related projects

<!-- agent-hint
covers: the data files that ship in the wheel, the scripts that rebuild them, and the repositories that use TugaLex
source: `tugalex/data/`, `scripts/`, `pyproject.toml`
generated: no
verify: diff <(ls tugalex/data | LC_ALL=C sort) <(grep -o '^| `[A-Za-z_.]*` ' docs/datasets.md | tr -d '|` ' | LC_ALL=C sort) && d=$(mktemp -d) && sed '/^```/d' docs/datasets.md > $d/d.txt && python -I -m doctest $d/d.txt
see: `api.md`, `index.md`
-->

This page lists the datasets under `tugalex/data/`, says how to rebuild each one, and names the projects that read TugaLex. All data ships inside the wheel, and no call reads the network.

## Files in the wheel

| File | Holds |
| --- | --- |
| `regional_dict.csv.gz` | The phoneme and syllable mappings: 318,872 rows for 53,148 distinct words in six regions, with 53,144 to 53,147 words in each region. Deprecated with the regional dictionary. |
| `words.csv.gz` | The word forms of `regional_dict.csv.gz` with the regions that list each one, and no pronunciations. `get_wordlist` reads it, and it stays when the regional dictionary goes. |
| `heterophonic_homographs.csv` | 27 words pronounced differently depending on POS, 55 rows with the columns `word,pos,ipa`. |
| `acordo_ortografico_pt_PT.csv` | Pre-AO1990 Portugal spellings and their AO1990 forms: 4,757 rows. Deprecated. |
| `acordo_ortografico_pt_BR.csv` | Pre-AO1990 Brazil spellings and their AO1990 forms: 2,123 rows. Deprecated. |
| `archaisms.csv` | Normalised words from before the 20th century and their modern forms: 5,522 rows. Deprecated. |
| `noun_gender_exceptions.csv.gz` | The nouns whose gender the suffix rules get wrong or do not cover, the nouns of both genders, and the words that are never nouns, with an empty gender: 23,615 rows. |
| `given_names.csv.gz` | Given names with their gender: 10,387 rows. |

The spelling files are also published as the Hugging Face datasets [AO1990_pt-PT](https://huggingface.co/datasets/TigreGotico/AO1990_pt-PT), [AO1990_pt-BR](https://huggingface.co/datasets/TigreGotico/AO1990_pt-BR) and [archaisms_pt](https://huggingface.co/datasets/TigreGotico/archaisms_pt).

## Check the counts

Count the rows of a packaged file with the standard library:

```python
>>> import csv, gzip
>>> from importlib.resources import files
>>> data = files("tugalex") / "data"
>>> with gzip.open(data / "given_names.csv.gz", "rt", encoding="utf-8") as f:
...     len(list(csv.DictReader(f)))
10387
>>> with gzip.open(data / "noun_gender_exceptions.csv.gz", "rt", encoding="utf-8") as f:
...     len(list(csv.DictReader(f)))
23615
>>> with (data / "archaisms.csv").open(encoding="utf-8") as f:
...     len(list(csv.DictReader(f)))
5522
```

## Regions

| ISO code | Region | Place |
| --- | --- | --- |
| `pt-PT` | `lbx` | Portugal (Lisbon) |
| `pt-BR` | `rjx` | Brazil (Rio de Janeiro) |
| none | `spx` | Brazil (São Paulo) |
| `pt-AO` | `lda` | Angola (Luanda) |
| `pt-MZ` | `mpx` | Mozambique (Maputo) |
| `pt-TL` | `dli` | Timor-Leste (Díli) |

The regional dictionary is a gzip extract with the columns word, phones, syllables and region code. It comes from the [unified Portuguese pronunciation lexicon](https://huggingface.co/datasets/TigreGotico/portuguese-unified-pronunciation-lexicon) and keeps six of its [Portal da Língua Portuguesa](http://www.portaldalinguaportuguesa.org) regions.

The regional dictionary has no part of speech. Each word has one pronunciation for each region, and it answers every POS query. Only the heterophonic homograph table is keyed by POS.

The scraped Portal data with all ten regional variants is the [`portuguese_phonetic_lexicon`](https://huggingface.co/datasets/TigreGotico/portuguese_phonetic_lexicon) dataset.

## Rebuild a dataset

Three build scripts download their sources, and `build_wordlist.py` reads a local dictionary file (`--dictionary PATH`). Run them only to regenerate a dataset.

```bash
python scripts/build_regional_dict.py
python scripts/build_wordlist.py
python scripts/build_noun_gender.py
python scripts/build_given_names.py
```

- `build_regional_dict.py` reads the lexicon revision that the script pins and checks its sha256.
- `build_wordlist.py` reads the regional dictionary and writes `words.csv.gz` with no timestamp, so the same input gives the same bytes.
- `build_noun_gender.py` reads the noun genders of the English Wiktionary.
- `build_given_names.py` reads Wikidata (CC0) and the IBGE 2010 census first names published by datasets-br/prenomes (ODC-PDDL-1.0).

Four override files correct the sources: `scripts/noun_gender_overrides.csv`, `scripts/given_name_overrides.csv` and `scripts/regional_dict_additions.csv` with `scripts/regional_dict_errata.csv`. Each row of `scripts/given_name_overrides.csv` carries its evidence in the `reason` column.

## Related projects

TugaLex is one piece of the TigreGotico Portuguese NLP stack.

- [tugaphone](https://github.com/TigreGotico/tugaphone) phonemizes Portuguese text for each dialect. It runs the lect specs of [orthography2ipa](https://github.com/TigreGotico/orthography2ipa) and the lexicons of `o2i-lexicons`. It depends on TugaLex, and its text normalisation reads the TugaLex noun and given-name genders. Its legacy `tugaphone.dialects` inventories read the deprecated regional dictionary.
- [bifonia](https://github.com/TigreGotico/bifonia) picks the reading of a heterophonic homograph by meaning, including the same-POS pairs that the TugaLex homograph table cannot separate.
- [tugamorph](https://github.com/TigreGotico/tugamorph) is a rule-based morphological analyser for Portuguese.
- [tugatagger](https://github.com/TigreGotico/tugatagger) wraps part-of-speech tagging for Portuguese. Its `lexicon` extra installs TugaLex.
- [desacordo_ortografico](https://github.com/TigreGotico/desacordo_ortografico) detects and converts between Portuguese orthographies. It reads the TugaLex word list, and its spelling table holds the archaism and AO1990 rows that the deprecated TugaLex spelling accessors return.

---
[← Advanced](advanced.md) · [Home](index.md)
