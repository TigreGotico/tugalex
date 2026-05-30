# tugalex — Roadmap

`tugalex` is a lexicon handler and linguistic utility for Portuguese dialects. It
loads bundled JSON resources (a base lexicon, dialect lexicons, abbreviations,
phonetic dialect maps) and exposes lookups over them.

## Phase 0 — Hardening ✅

- gh-automations CI at `@dev` (build-tests, coverage, license_check).
- pyproject-only packaging; Apache-2.0 LICENSE; `.gitignore`.
- Lexicon test suite (`test/test_lexicon.py`).

## Phase 1 — Correctness & coverage

- Expand the bundled lexicon / dialect coverage; validate JSON resources load and
  round-trip; add lookup tests per dialect.
- Document the JSON resource schema so new entries can be added as data.

## Phase 2 — Corpus integration (rescued Portuguese data)

A corpus of Portuguese wordlists and orthography data lives on the homelab bulk
tier at `/mnt/homelab/Workspace/_rescued/old-uncommitted/tugaphone/data/` (see
`research/notes/portuguese-phonetics-corpus.md`). It is the raw material for
making tugalex a real Portuguese lexicon, not just a small bundled one. **Source
of truth stays on homelab; the repo ships compressed/derived artifacts.**

Datasets and their target use here:

- **`wordlist-{ao,preao,big}-latest.txt.xz`** (~1.1–1.26M words each, ~1.7 MB
  compressed each) — the three orthographic variants: post-AO-1990 (`ao`),
  pre-reform (`preao`), and the union (`big`).
  - Ship a compressed wordlist (or a derived trie/set index) under `tugalex/data/`
    and a loader (`words(variant="ao")`), keeping the raw on homelab.
  - Powers: **membership / spell validation** (`is_word`), **OOV detection**,
    **candidate generation** (edit-distance suggestions), and lexicon-coverage
    measurement against the bundled JSON.
- **`acordo_ortografico_pt_{PT,BR}.csv`** — pre-/post-AO-1990 spelling pairs.
  - Build an **AO-1990 orthography normalizer/converter**: map text between
    pre-reform and current spelling (both pt-PT and pt-BR variants). This pairs
    with the `ao`/`preao` wordlists and is a distinct, useful public feature.
- **`scrap_ao.py`** — the scraper that regenerates the wordlists.
  - Land it as `scripts/build_wordlists.py` so the bundled data is reproducible;
    document the regen → recompress → publish flow. Route its HTTP through
    `unblock_requests` per the org transport rule.
- **`proverbios.txt`** — a small proverbs corpus → bundle as example/test data
  (`examples/` or a lookup demo), not core.

Routed elsewhere (not tugalex):

- **`examples/dialects_pt.csv`** (dialect transcription examples) → evaluation data
  for **tugaphone** / **sotaque_forcado** (G2P / accent eval), not the lexicon.
- **`estrangeirismos.pdf`** + the 75-paper `research/papers/` corpus → research
  material (homelab + `research/`), feeding **tugaphone** loanword phonology and
  the Lusophone phonemics whitepapers — not bundled in any package.

Storage discipline: large raw corpora stay on homelab; the repo carries only the
compressed wordlist(s) / derived indexes + the build script, so installs stay lean
(per the workspace storage rule).

## Phase 3 — Integration with the tuga* stack

- Serve as the shared lexicon layer for `tuga*` (tugaphone, tugatagger, tugamorph):
  tugaphone uses it for lexicon lookup before rule-based G2P; tugatagger/tugamorph
  for known-word checks. Align dialect tags with `sotaque_forcado` /
  `orthography2ipa`.
- Expose the AO normalizer as a preprocessing step other tools can call.

## Phase 4 — Datasets & publishing

- Publish the cleaned wordlists + AO-mapping as **Hugging Face datasets**
  (provenance + license noted; `scrap_ao.py` source documented), so the lexicon is
  reusable beyond this package and the data thinking is realized.
