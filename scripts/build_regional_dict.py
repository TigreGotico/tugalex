#!/usr/bin/env python3
"""Regenerate tugalex's regional dictionary from the unified Portuguese gold.

Maintainer action (network). Downloads
``TigreGotico/portuguese-unified-pronunciation-lexicon`` and rewrites
``tugalex/data/regional_dict.csv.gz`` with ONLY the columns the loader
consumes (word, phones, syllables, region_code), keeping the six Portal
da Língua Portuguesa regions tugaphone's dialect presets read. The
``phones`` column keeps the Portal's pipe-delimited syllabified form
(the loader renders ``|`` as the ``·`` syllable mark).

POS is deliberately absent: heterophonic homographs are resolved by
meaning (bifonia) or by the dedicated homographs table, never by a
POS-keyed lexicon lookup. When a region carries several register
variants of a word, the CANONICAL one is kept — the variant with the
fewest narrow-phonetic marks (aspiration, labialization, length …),
which recovers the standard register of the merged standard/colloquial
rows.

The Portal data has defects the build corrects through
``scripts/regional_dict_errata.csv``. Each errata row names one source row
(word, region, phones) and its replacement; an empty replacement drops the
row. The ``source`` column says where the correction comes from:

- ``rule``: the Portal's Lisbon row has no stress mark, mostly where a glide
  precedes the stressed vowel (paciente ``pɐ.sjẽ.tɨ``). The mark goes on the
  vowel the orthography stresses (written accent, else the oxytone or
  paroxytone rule), before the vowel, as the Portal writes it.
- ``rule+infopedia``, ``rule+wiktionary``: as ``rule``, and the dataset's
  pt-PT row of the same word puts the stress on the same vowel.
- ``infopedia``: the Portal mark is on the wrong syllable; the dataset's
  Infopédia pt-PT row gives the stressed syllable.
- ``demote``: the Portal writes two primary marks; every one but the
  primary the orthography gives becomes ``ˌ``, as in the Portal's own
  compounds (bate-boca ``bˌa.tɨ.bˈo.kɐ``).
- ``drop``: the row transcribes another headword (tração holds *seleto*)
  or is truncated.

An errata row whose source row is absent stops the build, so a changed
source is re-checked rather than patched blindly. The build also stops when
a Lisbon entry of two or more syllables has a reading without exactly one
primary mark.

Usage::

    python scripts/build_regional_dict.py [--gold lexicon.jsonl] [--out path]
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import os
import sys
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO_ROOT, "tugalex", "data", "regional_dict.csv.gz")
ERRATA = os.path.join(REPO_ROOT, "scripts", "regional_dict_errata.csv")

GOLD_URL = (
    "https://huggingface.co/datasets/TigreGotico/"
    "portuguese-unified-pronunciation-lexicon"
    "/resolve/main/portuguese_pronunciation_lexicon.jsonl"
)

#: unified-dataset region tag -> tugalex internal region code
REGION_MAP = {
    "pt-PT-x-lisboa": "lbx",
    "pt-BR-x-riodejaneiro": "rjx",
    "pt-BR-x-saopaulo": "spx",
    "pt-AO": "lda",
    "pt-MZ-x-maputo": "mpx",
    "pt-TL-x-dili": "dli",
}


#: regions whose every entry of two or more syllables carries one primary mark
STRESS_CHECKED_REGIONS = {"lbx"}


def load_errata(path: str) -> dict:
    """(word, region_code, source_phones) -> replacement phones ("" drops)."""
    with open(path, encoding="utf-8", newline="") as fh:
        return {(r["word"], r["region_code"], r["source_phones"]): r["phones"]
                for r in csv.DictReader(fh)}


def stress_offenders(rows, regions=STRESS_CHECKED_REGIONS) -> list:
    """Rows of ``regions`` with two or more syllables and a reading (``$$``
    separates readings) that lacks exactly one primary mark."""
    return [(word, phones, region) for word, phones, syl, region in rows
            if region in regions
            and len([s for s in syl.split("|") if s]) >= 2
            and any(r.count("ˈ") != 1 for r in phones.split("$$"))]


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--gold", help="local copy of the unified lexicon "
                        "JSONL (default: download it)")
    parser.add_argument("--out", default=OUT)
    parser.add_argument("--errata", default=ERRATA)
    args = parser.parse_args(argv)
    if args.gold:
        with open(args.gold, "rb") as fh:
            raw = fh.read()
    else:
        print(f"downloading {GOLD_URL} …", file=sys.stderr)
        with urllib.request.urlopen(GOLD_URL) as resp:
            raw = resp.read()
    digest = hashlib.sha256(raw).hexdigest()
    errata = load_errata(args.errata)
    applied = set()

    _NARROW_MARKS = "ʰʷʲːˤ̥̬̃ʱ"

    def canonical_rank(phones: str):
        # standard register first: fewest narrow marks, then shortest,
        # then lexicographic (deterministic)
        return (sum(phones.count(m) for m in _NARROW_MARKS),
                len(phones), phones)

    best: dict = {}
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        region = REGION_MAP.get(r.get("region", ""))
        word = (r.get("word") or "").strip()
        phones = (r.get("phones") or "").strip()
        # the gold uses ASCII "g" (U+0067) where IPA calls for the voiced
        # velar stop "ɡ" (U+0261, distinct codepoint) — normalize here so
        # downstream TTS vocabularies, which only know U+0261, don't
        # silently drop the phoneme.
        phones = phones.replace("g", "ɡ")
        if not region or not word or not phones:
            continue
        if (word, region, phones) in errata:
            applied.add((word, region, phones))
            phones = errata[(word, region, phones)]
            if not phones:
                continue
        key = (word, region)
        cand = (phones, (r.get("syllables") or "").strip())
        if key not in best or canonical_rank(cand[0]) < canonical_rank(best[key][0]):
            best[key] = cand
    rows = sorted((w, ph, syl, reg)
                  for (w, reg), (ph, syl) in best.items())
    stale = sorted(set(errata) - applied)
    if stale:
        sys.exit(f"{len(stale)} errata rows match no source row, "
                 f"e.g. {stale[0]}; re-check them against the source")
    offenders = stress_offenders(rows)
    if offenders:
        sys.exit(f"{len(offenders)} entries lack exactly one primary mark, "
                 f"e.g. {offenders[:5]}; add errata rows for them")
    print(f"source rows corrected by errata: {len(applied)}", file=sys.stderr)

    buf = io.StringIO()
    buf.write(f"# source sha256={digest}\n")
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["word", "phones", "syllables", "region_code"])
    writer.writerows(rows)
    with gzip.open(args.out, "wt", encoding="utf-8", compresslevel=9) as fh:
        fh.write(buf.getvalue())
    print(f"wrote {args.out}: {len(rows)} rows "
          f"({os.path.getsize(args.out) / 1e6:.1f} MB)", file=sys.stderr)


if __name__ == "__main__":
    main()
