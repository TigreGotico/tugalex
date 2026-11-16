#!/usr/bin/env python3
"""Regenerate tugalex's word list from the regional dictionary.

``TugaLexicon.get_wordlist`` reads ``tugalex/data/words.csv.gz``. The file
holds the word forms of ``tugalex/data/regional_dict.csv.gz`` and no
pronunciations: one row per word, with the codes of the regions whose
dictionary lists it. The words come out of the dictionary loader unchanged,
lowercase and stripped, so ``get_wordlist(region)`` gives the same list as the
keys of the dictionary for that region.

The output is a gzip-compressed CSV with a ``word,regions`` header, sorted by
word, with the region codes space-separated and sorted. The gzip header
carries no timestamp, so the same input and Python version give the same
bytes::

    python scripts/build_wordlist.py [--dictionary PATH] [--out PATH]
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from tugalex import TugaLexicon  # noqa: E402

DICTIONARY = os.path.join(REPO_ROOT, "tugalex", "data", "regional_dict.csv.gz")
OUT = os.path.join(REPO_ROOT, "tugalex", "data", "words.csv.gz")


def word_regions(dictionary: str) -> dict:
    """word -> sorted region codes whose dictionary entries list it."""
    _, syllables, _ = TugaLexicon._load_lang_map(dictionary)
    regions: dict = {}
    for region in sorted(syllables):
        for word in syllables[region]:
            regions.setdefault(word, []).append(region)
    return regions


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dictionary", default=DICTIONARY)
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
