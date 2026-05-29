"""Example — the same word across Portuguese dialects.

Run::

    python examples/03_dialects.py
"""
from tugalex import TugaLexicon


def main() -> None:
    lex = TugaLexicon()

    dialects = ["pt-PT", "pt-BR", "pt-AO", "pt-MZ", "pt-TL"]
    word = "acordo"

    print(f"phonemes of {word!r} (NOUN) by dialect:")
    for iso in dialects:
        region = lex.lang_to_region(iso)
        ipa = lex.get_phonemes(word, pos="NOUN", region=region)
        print(f"  {iso} ({region}): {ipa or '(no entry)'}")

    print()
    print("all region codes in the dataset:", sorted(lex.regions))


if __name__ == "__main__":
    main()
