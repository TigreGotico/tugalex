#!/usr/bin/env python3
"""Regenerate tugalex's list of noun-gender exceptions.

Developer tool (network). ``TugaLexicon.get_noun_gender`` reads a noun's
gender from suffix rules (``tugalex.NOUN_GENDER_SUFFIXES``) and from
``tugalex/data/noun_gender_exceptions.csv.gz``. This script compares the
suffix rules against the genders that the English Wiktionary gives every
Portuguese common noun, as extracted by wiktextract and published by
kaikki.org, and writes the nouns the rules get wrong or do not cover. Nouns
of both genders are always written as ``mf``: a common-gender noun ("o/a
artista"), a noun whose gender changes with its meaning ("o capital"/"a
capital"), or a noun whose gender differs between Portugal and Brazil.
Nothing else from the download is kept.

The genders come from the head templates of the noun entries (``{{pt-noun|f}}``,
``{{head|pt|noun form|g=m}}``). Plurals and the feminine or masculine
counterparts come from the ``forms`` of each entry, so no plural is derived by
rule. A word gets the union of the genders of all its entries, so two
etymologies of one spelling with different genders ("capital") give ``mf``.
A gender with a usage label such as "obsolete" or "nonstandard" is dropped
when the entry also gives an unlabelled gender, and an entry whose every
sense is marginal (obsolete, archaic, poetic, a misspelling) counts only
when the word has no other entry. A gender with a regional label ("Brazil",
"Portugal") is kept, so the noun becomes ``mf``.

``scripts/noun_gender_overrides.csv`` then sets the gender of forms that a
rare loanword sense would make both-gender ("cores": "a cor", beside the
computing term "o core").

Words that are also an article, pronoun, determiner, conjunction, contraction
or letter ("a", "os", "ou", "todo") are left out. Prepositions stay, because
several of them are also common nouns ("vezes", "via", "segundo"). Proper
nouns, words with a capital letter, a space, a digit or an edge hyphen, and
one-letter words are left out too.

The output is a gzip-compressed CSV with a ``word,gender`` header, sorted::

    python scripts/build_noun_gender.py
    python scripts/build_noun_gender.py --source kaikki-Portuguese.jsonl.gz
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import re
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import IO, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tugalex import suffix_noun_gender  # noqa: E402

SOURCE_URL = "https://kaikki.org/dictionary/Portuguese/kaikki.org-dictionary-Portuguese.jsonl.gz"
SOURCE_PAGE = "https://kaikki.org/dictionary/Portuguese/index.html"
REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = REPO_ROOT / "tugalex" / "data" / "noun_gender_exceptions.csv.gz"
OVERRIDES = Path(__file__).resolve().parent / "noun_gender_overrides.csv"

CLOSED_CLASS_POS = {"article", "pron", "det", "conj", "contraction", "character"}
# An entry whose every sense carries one of these tags is marginal. A marginal
# closed-class entry ("nozes" for "nós") does not drop the noun, and a
# marginal noun entry ("cor" m, poetic "heart") gives no gender to a word that
# has an ordinary noun entry ("cor" f, "colour").
MARGINAL_SENSE_TAGS = {"alt-of", "misspelling", "misconstruction", "obsolete",
                       "archaic", "poetic"}
# Usage labels that mark a gender as a minority use beside the standard one.
MINORITY_LABELS = re.compile(r"obsolete|nonstandard|proscribed|rare|uncommon|"
                             r"less common|dated|derogatory|informal|see usage")
# Form tags that keep a form in the list; any other tag (alternative,
# diminutive, obsolete, misspelling, ...) drops it.
FORM_TAGS = {"plural", "feminine", "masculine", "Portugal", "Brazil"}
GENDER_CODES = {"m": {"m"}, "f": {"f"}, "m-p": {"m"}, "f-p": {"f"},
                "mf": {"m", "f"}, "mfbysense": {"m", "f"}, "mfequiv": {"m", "f"}}


def split_specs(arg: str) -> list[str]:
    """Split a gender argument such as ``f,m<l:rare>`` at its top-level commas."""
    specs, depth, current = [], 0, ""
    for char in arg:
        depth += char == "<"
        depth -= char == ">"
        if char == "," and depth == 0:
            specs.append(current)
            current = ""
        else:
            current += char
    return specs + [current]


def parse_genders(args: list[str]) -> set[str]:
    """The genders named by the head-template gender arguments of one entry."""
    standard, minority = set(), set()
    for spec in (s for arg in args for s in split_specs(arg)):
        code, _, label = spec.partition("<")
        genders = GENDER_CODES.get(code.strip(), set())
        if label and MINORITY_LABELS.search(label) and not re.search(r"Brazil|Portugal|Mozambique|regional", label):
            minority |= genders
        else:
            standard |= genders
    return standard or minority


def entry_genders(entry: dict) -> set[str]:
    """The genders that the head templates of a noun entry give."""
    genders = set()
    for head in entry.get("head_templates", []):
        args = head.get("args", {})
        if head.get("name") == "pt-noun":
            genders |= parse_genders([args.get("1", "")])
        elif head.get("name") == "head" and args.get("2") in ("noun", "noun form"):
            genders |= parse_genders([args[k] for k in ("g", "g2", "g3") if k in args])
    return genders


def keep(word: str) -> bool:
    """Lowercase words of two or more letters, hyphenated compounds included."""
    return len(word) > 1 and word == word.lower() and re.fullmatch(r"[^\W\d_]+(-[^\W\d_]+)*", word) is not None


def open_source(source: str) -> tuple[IO[bytes], str]:
    """Open the dump and return it with a line recording its date."""
    if not source.startswith(("http://", "https://")):
        return open(source, "rb"), f"local file {source}"
    response = urllib.request.urlopen(source)
    date = f"Last-Modified {response.headers['Last-Modified']}"
    page = urllib.request.urlopen(SOURCE_PAGE).read().decode()
    extracted = re.search(r"extracted on (\S+) from the enwiktionary dump dated (\S+)", page)
    if extracted:
        date += f"; extracted on {extracted[1]} from the enwiktionary dump dated {extracted[2]}"
    return response, date


def read_entries(stream: IO[bytes], name: str) -> Iterator[dict]:
    if name.endswith(".gz"):
        stream = gzip.GzipFile(fileobj=stream)
    for line in io.TextIOWrapper(stream, encoding="utf-8"):
        yield json.loads(line)


def is_marginal(entry: dict) -> bool:
    """Whether every sense of an entry is a marginal use."""
    return all(MARGINAL_SENSE_TAGS & set(sense.get("tags", [])) for sense in entry.get("senses", []))


def build(source: str) -> tuple[dict[str, str], str]:
    stream, date = open_source(source)
    # Genders from ordinary entries, and from entries whose every sense is
    # marginal ("cor" m, poetic "heart", beside "cor" f, "colour"). A marginal
    # gender counts only for a word that has no ordinary entry.
    genders: dict[str, set[str]] = defaultdict(set)
    marginal: dict[str, set[str]] = defaultdict(set)
    closed_class: set[str] = set()
    entries = 0
    for entry in read_entries(stream, source):
        word, pos = entry.get("word", ""), entry.get("pos")
        if pos in CLOSED_CLASS_POS and not is_marginal(entry):
            closed_class.add(word.lower())
        if pos != "noun":
            continue
        lemma = entry_genders(entry)
        if not lemma:
            continue
        entries += 1
        target = marginal if is_marginal(entry) else genders
        target[word] |= lemma
        for form in entry.get("forms", []):
            tags = set(form.get("tags", []))
            if not tags or not tags <= FORM_TAGS or not tags & {"plural", "feminine", "masculine"}:
                continue
            target[form["form"]] |= {"f"} if "feminine" in tags else {"m"} if "masculine" in tags else lemma
    lexicon = {}
    for word in genders.keys() | marginal.keys():
        gender = genders.get(word) or marginal[word]
        if keep(word) and word not in closed_class:
            lexicon[word] = "mf" if gender == {"m", "f"} else next(iter(gender))
    print(f"{entries} noun entries with a gender in, {len(lexicon)} words out "
          f"({len(closed_class & (genders.keys() | marginal.keys()))} closed-class words dropped)")
    return lexicon, date


def apply_overrides(lexicon: dict[str, str]) -> None:
    with open(OVERRIDES, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        lexicon[row["word"]] = row["gender"]
    print(f"{len(rows)} overrides applied")


def exceptions(lexicon: dict[str, str]) -> dict[str, str]:
    """The nouns whose gender the suffix rules get wrong or do not give."""
    return {word: gender for word, gender in lexicon.items() if suffix_noun_gender(word) != gender}


def write(listed: dict[str, str], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as fh:
        text = io.TextIOWrapper(fh, encoding="utf-8", newline="")
        writer = csv.writer(text, lineterminator="\n")
        writer.writerow(["word", "gender"])
        writer.writerows(sorted(listed.items()))
        text.flush()
        text.detach()
    counts = {g: sum(1 for v in listed.values() if v == g) for g in ("m", "f", "mf")}
    print(f"wrote {output} ({output.stat().st_size} bytes): {len(listed)} exceptions {counts}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", default=SOURCE_URL,
                        help="kaikki.org Portuguese JSONL dump, as a URL or a local path")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    lexicon, date = build(args.source)
    print(f"source: {args.source} ({date})")
    apply_overrides(lexicon)
    listed = exceptions(lexicon)
    print(f"{len(lexicon)} nouns in, {len(listed)} exceptions out, "
          f"{len(lexicon) - len(listed)} read correctly by the suffix rules")
    write(listed, args.output)


if __name__ == "__main__":
    main()
