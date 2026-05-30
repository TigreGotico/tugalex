# TODO — tugalex

## Bugs

- [x] CSV loaders (`_load_homographs`, `_load_archaisms`, `_load_ao`) split on `\n`
  but the data files use CRLF, leaving a trailing `\r` on the last field. This made
  homograph POS keys like `VERB\r`, so `get_phonemes("para", pos="VERB")` returned
  `None`. Fixed by stripping each field on load.

## Open issues

- [ ] #8 Dicionário de Estrangeirismos (enhancement)
- [ ] #7 Dicionário de nomes deverbais (enhancement)
- [ ] #6 Dicionário de Gentílicos e Topónimos (enhancement)
- [ ] #2 Add `silent_c_words` detection to match documentation claims

## Gaps

- [x] No test suite — added `tests/test_lexicon.py` (dialect mapping, homographs,
  archaisms, AO1990 round-trips, phenomena).
- [x] No CI — added the `OpenVoiceOS/gh-automations@dev` reusable workflow set
  (build-tests, coverage, lint, license-check, pip-audit, release-preview,
  repo-health, release/publish).
- [x] No `.gitignore` — added.
- [x] `setup.py` had empty `license`/`description` and no packaging metadata —
  replaced with `pyproject.toml` (Apache-2.0, dynamic version from
  `tugalex/version.py`).
- [x] Reusable workflows pinned `@master` of `TigreGotico/gh-automations` —
  now `OpenVoiceOS/gh-automations@dev`.
- [ ] `silent_c_words` is documented in the README but not implemented (see #2).
- [ ] `regional_dict.csv` is ~49 MB committed in-tree; consider sourcing it from the
  HuggingFace dataset at install/runtime instead of shipping it in the package.
- [ ] The two analysis notebooks (~3.4 MB) live at the repo root; consider moving
  them to `docs/` or stripping outputs.
- [ ] CSV parsing is hand-rolled; switching to the `csv` module would make the
  loaders robust to quoting/escaping as well as line endings.

## Code TODOs

None found in source.
