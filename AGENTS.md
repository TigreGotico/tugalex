# tugalex: agent guide

<!-- agent-hint
covers: how to set up, test and change the repository, and the rules the code and tests enforce
source: `pyproject.toml`, `tugalex/__init__.py`, `tests/test_api_surface.py`
generated: no
verify: grep -v '^verify:' AGENTS.md | grep -o '](\([^)#]*\)' | sed 's/](//' | grep -v '^http' | while read f; do test -e "$f" || exit 1; done
see: `docs/index.md`, `README.md`
-->

`tugalex` is a Python package with one class, `TugaLexicon`. It gives the Portuguese word list, the gender of common nouns and given names, and the pronunciation of 27 heterophonic homographs, from data that ships in the wheel.

The documentation starts at [docs/index.md](docs/index.md).

## Repository map

| Path | Holds |
|---|---|
| `tugalex/__init__.py` | `TugaLexicon` and the noun-gender suffix rules ([api.md](docs/api.md)) |
| `tugalex/data/` | The packaged datasets ([datasets.md](docs/datasets.md)) |
| `scripts/` | The build scripts for the datasets and their override files |
| `tests/`, `examples/` | The pytest suite and one runnable script for each feature |
| `docs/` | The documentation |
| `*.ipynb` | An analysis notebook for the phonetic lexicon dataset on Hugging Face |

## Setup and tests

```bash
unset VIRTUAL_ENV
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python --prerelease=allow -e ".[test]"
.venv/bin/python -m pytest tests
```

Use uv, never pip. Each `verify` command calls `python`, so run `source .venv/bin/activate` first. Two build scripts download their sources, and `build_wordlist.py` reads a local dictionary file (`--dictionary PATH`). Run them only to regenerate a dataset.

## Hard rules

1. The package has no third-party runtime dependency. `dependencies` in `pyproject.toml` stays empty ([README](README.md)).
2. The word list, `get_noun_gender` and `get_given_name_gender` stay silent. The downstream workflow runs the desacordo_ortografico suite against the pull request, and a `DeprecationWarning` fails that job ([api.md](docs/api.md)).
3. Every dataset ships inside the wheel under `tugalex/data/`, and no call reads the network ([datasets.md](docs/datasets.md)).

## Before you push

1. Run the full test suite.
2. If you changed a page, run its `verify` command from the `agent-hint` comment after its H1.
3. A page you add goes in the table of `docs/index.md` and gets an `agent-hint` comment and a footer whose Home link points to the index.
