"""Example — phonemes and syllables for a Portuguese word.

This example uses the deprecated dictionary API, which emits a
DeprecationWarning and is removed in the next major release.

Run::

    python examples/01_lookup.py
"""
from tugalex import TugaLexicon


def main() -> None:
    lex = TugaLexicon()

    for word in ["acordo", "casa", "trabalho", "coração"]:
        info = lex.get(word, pos="NOUN", region="lbx")
        syl = "-".join(info["syllables"]) or "(unknown)"
        ipa = info["phonemes"] or "(unknown)"
        print(f"{word:12} {syl:18} /{ipa}/")


if __name__ == "__main__":
    main()
