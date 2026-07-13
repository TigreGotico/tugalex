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

Usage::

    python scripts/build_regional_dict.py
"""
from __future__ import annotations

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


def main() -> None:
    print(f"downloading {GOLD_URL} …", file=sys.stderr)
    with urllib.request.urlopen(GOLD_URL) as resp:
        raw = resp.read()
    digest = hashlib.sha256(raw).hexdigest()

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
        if not region or not word or not phones:
            continue
        key = (word, region)
        cand = (phones, (r.get("syllables") or "").strip())
        if key not in best or canonical_rank(cand[0]) < canonical_rank(best[key][0]):
            best[key] = cand
    rows = sorted((w, ph, syl, reg)
                  for (w, reg), (ph, syl) in best.items())

    buf = io.StringIO()
    buf.write(f"# source sha256={digest}\n")
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["word", "phones", "syllables", "region_code"])
    writer.writerows(rows)
    with gzip.open(OUT, "wt", encoding="utf-8", compresslevel=9) as fh:
        fh.write(buf.getvalue())
    print(f"wrote {OUT}: {len(rows)} rows "
          f"({os.path.getsize(OUT) / 1e6:.1f} MB)", file=sys.stderr)


if __name__ == "__main__":
    main()
