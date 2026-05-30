# Roadmap — tugalex

`tugalex` is the lexicon + phonetic-data layer of the **Tuga** Portuguese NLP stack
(`tugaphone`, `tugamorph`, `tugatagger`). It serves IPA transcriptions, syllable
segmentations, AO1990 orthography mappings, and curated linguistic phenomena
(homographs, archaisms, silent letters, voiced `u`) across the major Lusophone
dialects (pt-PT, pt-BR, pt-AO, pt-MZ, pt-TL).

## Phase 0 — Hardening (done)

- `pyproject.toml` with dynamic version from `tugalex/version.py` (Apache-2.0);
  `setup.py` removed.
- Apache-2.0 `LICENSE`, `.gitignore`, `conftest.py`.
- CI via `OpenVoiceOS/gh-automations@dev`: build-tests, coverage, lint,
  license-check, pip-audit, release-preview, repo-health, and the alpha/stable
  release + publish workflows.
- `tests/` suite, green.

## Phase 1 — Correctness & coverage

- Fixed the CRLF parsing bug that hid POS-specific homograph pronunciations.
- Next: implement `silent_c_words` to back the documented feature (#2).
- Next: broaden test coverage to the phoneme/syllable maps (heavy `regional_dict.csv`)
  behind an opt-in marker, and verify every README-advertised method exists.
- Next: harden CSV loading via the stdlib `csv` module.

## Phase 2 — Integration with the Tuga stack

- Serve as the shared curated source of truth for `tugaphone`: prefer tugalex IPA
  and syllable boundaries over tugaphone's rule-based fallback.
- Expose homograph POS variants so `tugatagger` output can drive correct
  pronunciation selection in `tugaphone`.
- Align word normalization (AO1990) so `tugamorph` / `tugatagger` analyze agreed
  spelling, and reconcile the POS tag vocabulary across the four tools.
- Consider sourcing the large phonetic lexicon from the HuggingFace dataset at
  runtime so the package stays lightweight for stack consumers.
