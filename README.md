# TugaLex

<!-- agent-hint
covers: what TugaLex provides, how to install it and the first calls
source: `tugalex/__init__.py`, `tugalex/version.py`, `pyproject.toml`
generated: no
verify: d=$(mktemp -d) && sed '/^```/d' README.md > $d/r.txt && python -I -m doctest $d/r.txt
see: `docs/index.md`, `docs/quickstart.md`, `docs/api.md`, `AGENTS.md`
-->

TugaLex is a lexicon library for Portuguese. It gives the word list of the Portuguese pronunciation dictionary, the grammatical gender of a common noun, the grammatical gender of a given name, and the pronunciation of 27 words that depend on part of speech. It has no third-party runtime dependencies, and all data ships in the package.

TugaLex has no pronunciation dictionary and no spelling conversion. For pronunciation, use [orthography2ipa](https://github.com/TigreGotico/orthography2ipa). For spelling conversion, use [desacordo_ortografico](https://github.com/TigreGotico/desacordo_ortografico).

## Install

```bash
pip install --pre tugalex
```

TugaLex publishes alpha releases from the `dev` branch, so `--pre` gives the API that these pages describe. The package needs Python 3.11 or later. It has no extras, except `test`, which adds `pytest`.

## Quick start

```python
>>> from tugalex import TugaLexicon
>>> TugaLexicon.get_noun_gender("lei")
'f'
>>> TugaLexicon.get_noun_gender("artista")
'mf'
>>> TugaLexicon.get_given_name_gender("Isabel")
'f'
>>> TugaLexicon.get_given_name_gender("Raio") is None
True
>>> lex = TugaLexicon()
>>> len(lex.get_wordlist("lbx"))
53147
>>> lex.homographs["acordo"]
{'NOUN': 'ɐˈkoɾdu', 'VERB': 'ɐˈkɔɾdu'}
```

`"mf"` marks a noun or a name of both genders. `None` marks a word that the lists and the rules do not cover.

## Documentation

The documentation starts at [docs/index.md](docs/index.md). [docs/quickstart.md](docs/quickstart.md) walks through each lookup with its output. Runnable scripts for each feature are in [examples/](examples).

## Development

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python --prerelease=allow -e ".[test]"
.venv/bin/python -m pytest tests
```

[AGENTS.md](AGENTS.md) holds the repository map and the rules for changes.

## License

TugaLex is released under the [Apache License 2.0](LICENSE).
