#!/usr/bin/env python3
"""Regenerate tugalex's word list from a regional pronunciation dictionary.

``TugaLexicon.get_wordlist`` reads ``tugalex/data/words.csv.gz``. The file
holds the word forms of a regional dictionary and no pronunciations: one row
per word, with the codes of the regions whose dictionary lists it.

The dictionary is a CSV, gzip-compressed when its name ends in ``.gz``, with
the columns ``word, phones, syllables, region_code``. Lines that start with
``#`` are skipped, and the words and region codes are lowercased and stripped.
The shipped word list comes from the six-region extract of
TigreGotico/portuguese-unified-pronunciation-lexicon that tugalex 2.x ships
as ``tugalex/data/regional_dict.csv.gz``.

The output is a gzip-compressed CSV with a ``word,regions`` header, sorted by
word, with the region codes space-separated and sorted. The gzip header
carries no timestamp, so the same input and Python version give the same
bytes::

    python scripts/build_wordlist.py --dictionary PATH [--out PATH]
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO_ROOT, "tugalex", "data", "words.csv.gz")


def word_regions(dictionary: str) -> dict:
    """word -> sorted region codes whose dictionary entries list it."""
    opener = gzip.open if dictionary.endswith(".gz") else open
    with opener(dictionary, "rt", encoding="utf-8") as f:
        reader = csv.reader(line for line in f if not line.startswith("#"))
        next(reader, None)  # header
        pairs = {(row[3].strip().lower(), row[0].strip().lower()) for row in reader if len(row) >= 4}
    regions: dict = {}
    for region, word in sorted(pairs):
        regions.setdefault(word, []).append(region)
    return regions


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dictionary", required=True)
    parser.add_argument("--out", default=OUT)
    args = parser.parse_args(argv)
    regions = word_regions(args.dictionary)
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["word", "regions"])
    writer.writerows((word, " ".join(regions[word])) for word in sorted(regions))
    with open(args.out, "wb") as fh:
        fh.write(gzip.compress(buf.getvalue().encode("utf-8"), compresslevel=9, mtime=0))
    print(f"wrote {args.out}: {len(regions)} words "
          f"({os.path.getsize(args.out) / 1e3:.0f} kB)", file=sys.stderr)


if __name__ == "__main__":
    main()
