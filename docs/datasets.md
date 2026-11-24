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
| `words.csv.gz` | The word forms of the regional pronunciation dictionary with the regions that list each one, and no pronunciations: 53,148 distinct words in six regions, with 53,144 to 53,147 words in each region. `get_wordlist` reads it. |
| `heterophonic_homographs.csv` | 27 words pronounced differently depending on POS, 55 rows with the columns `word,pos,ipa`. |
| `noun_gender_exceptions.csv.gz` | The nouns whose gender the suffix rules get wrong or do not cover, the nouns of both genders, and the closed-class words, some with an empty gender: 23,525 rows. |
| `given_names.csv.gz` | Given names with their gender: 10,387 rows. |

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
23525
>>> with gzip.open(data / "words.csv.gz", "rt", encoding="utf-8") as f:
...     len(list(csv.DictReader(f)))
53148
```

## Regions

| Place | Region |
| --- | --- |
| Portugal (Lisbon) | `lbx` |
| Brazil (Rio de Janeiro) | `rjx` |
| Brazil (São Paulo) | `spx` |
| Angola (Luanda) | `lda` |
| Mozambique (Maputo) | `mpx` |
| Timor-Leste (Díli) | `dli` |

The word list comes from a regional pronunciation dictionary with the columns word, phones, syllables and region code. That dictionary is an extract of the [unified Portuguese pronunciation lexicon](https://huggingface.co/datasets/TigreGotico/portuguese-unified-pronunciation-lexicon) and keeps six of its [Portal da Língua Portuguesa](http://www.portaldalinguaportuguesa.org) regions. TugaLex ships its word forms and none of its pronunciations.

The scraped Portal data with all ten regional variants is the [`portuguese_phonetic_lexicon`](https://huggingface.co/datasets/TigreGotico/portuguese_phonetic_lexicon) dataset.

## Rebuild a dataset

Two build scripts download their sources, and `build_wordlist.py` reads a local dictionary file (`--dictionary PATH`). Run them only to regenerate a dataset.

```bash
python scripts/build_wordlist.py --dictionary regional_dict.csv.gz
python scripts/build_noun_gender.py
python scripts/build_given_names.py
```

- `build_wordlist.py` reads a regional dictionary CSV and writes `words.csv.gz` with no timestamp, so the same input gives the same bytes. The shipped file is the output for the `tugalex/data/regional_dict.csv.gz` file of the tugalex 2.x releases.
- `build_noun_gender.py` reads the noun genders of the English Wiktionary.
- `build_given_names.py` reads Wikidata (CC0) and the IBGE 2010 census first names published by datasets-br/prenomes (ODC-PDDL-1.0).

Two override files correct the sources: `scripts/noun_gender_overrides.csv` and `scripts/given_name_overrides.csv`. Each row of `scripts/given_name_overrides.csv` carries its evidence in the `reason` column.

## Related projects

TugaLex is one piece of the TigreGotico Portuguese NLP stack.

- [tugaphone](https://github.com/TigreGotico/tugaphone) phonemizes Portuguese text for each dialect. It runs the lect specs of [orthography2ipa](https://github.com/TigreGotico/orthography2ipa) and the lexicons of `o2i-lexicons`. It depends on TugaLex, and its text normalisation reads the TugaLex noun and given-name genders.
- [bifonia](https://github.com/TigreGotico/bifonia) picks the reading of a heterophonic homograph by meaning, including the same-POS pairs that the TugaLex homograph table cannot separate.
- [tugamorph](https://github.com/TigreGotico/tugamorph) is a rule-based morphological analyser for Portuguese.
- [tugatagger](https://github.com/TigreGotico/tugatagger) wraps part-of-speech tagging for Portuguese.
- [desacordo_ortografico](https://github.com/TigreGotico/desacordo_ortografico) detects and converts between Portuguese orthographies. It reads the TugaLex word list, and its spelling table holds the archaism and AO1990 spelling rows.
- [text2spoken](https://github.com/TigreGotico/text2spoken) rewrites written text into the words that a person says when they read it aloud. Its Portuguese rules read the TugaLex word list and the noun and given-name genders.

---
[← Advanced](advanced.md) · [Home](index.md)
