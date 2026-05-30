# tugalex — TODO

## Hardening ✅
- gh-automations CI at `@dev`; pyproject-only packaging; LICENSE; `.gitignore`.
- Lexicon test suite.

## Correctness & coverage
- [ ] Expand bundled lexicon / dialect coverage.
- [ ] Validate all JSON resources load and round-trip.
- [ ] Document the JSON resource schema.

## Corpus integration (see ROADMAP Phase 2)
Source corpus on homelab: `/mnt/homelab/Workspace/_rescued/old-uncommitted/tugaphone/data/`
- [ ] Bundle a compressed wordlist / derived index under `tugalex/data/` from
      `wordlist-{ao,preao,big}-latest.txt.xz`; add a `words(variant=...)` loader.
- [ ] `is_word` / OOV check / edit-distance candidate generation over the wordlist.
- [ ] AO-1990 orthography normalizer from `acordo_ortografico_pt_{PT,BR}.csv`
      (pre↔post reform, pt-PT + pt-BR).
- [ ] Land `scrap_ao.py` as `scripts/build_wordlists.py` (route HTTP via
      `unblock_requests`); document the regen/recompress flow.
- [ ] Bundle `proverbios.txt` as example/test data.

## Integration
- [ ] Serve as the shared lexicon layer for the tuga* stack (tugaphone lexicon
      lookup pre-G2P; tugatagger/tugamorph known-word checks).
- [ ] Align dialect tags with sotaque_forcado / orthography2ipa.

## Datasets
- [ ] Publish wordlists + AO mapping as HF datasets (provenance/license noted).

## Routed elsewhere (not tugalex)
- [ ] `examples/dialects_pt.csv` → tugaphone / sotaque_forcado eval data.
- [ ] `estrangeirismos.pdf` + research papers → research/ + tugaphone loanword work.
