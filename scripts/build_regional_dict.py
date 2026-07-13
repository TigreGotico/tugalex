#!/usr/bin/env python3
"""Regenerate tugalex's regional dictionary from the unified Portuguese gold.

Maintainer action (network). Downloads
``TigreGotico/portuguese-unified-pronunciation-lexicon`` and rewrites
``tugalex/data/regional_dict.csv.gz`` with ONLY the columns the loader
consumes (word, pos, phones, syllables, region_code), keeping the six
Portal da Língua Portuguesa regions tugaphone's dialect presets read.
The ``phones`` column keeps the Portal's pipe-delimited syllabified
form (the loader renders ``|`` as the ``·`` syllable mark).

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

    rows = []
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        region = REGION_MAP.get(r.get("region", ""))
        word = (r.get("word") or "").strip()
        phones = (r.get("phones") or "").strip()
        if not region or not word or not phones:
            continue
        rows.append((word, (r.get("pos") or "").strip(),
                     phones, (r.get("syllables") or "").strip(), region))
    rows.sort()

    buf = io.StringIO()
    buf.write(f"# source sha256={digest}\n")
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["word", "pos", "phones", "syllables", "region_code"])
    writer.writerows(rows)
    with gzip.open(OUT, "wt", encoding="utf-8", compresslevel=9) as fh:
        fh.write(buf.getvalue())
    print(f"wrote {OUT}: {len(rows)} rows "
          f"({os.path.getsize(OUT) / 1e6:.1f} MB)", file=sys.stderr)


if __name__ == "__main__":
    main()
