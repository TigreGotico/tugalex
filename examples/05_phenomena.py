"""Example — archaisms, silent 'p', and the formerly-trema voiced 'u'.

Run::

    python examples/05_phenomena.py
"""
from tugalex import TugaLexicon


def main() -> None:
    lex = TugaLexicon()

    # Archaic spellings are rewritten to their modern form on lookup.
    print("archaisms (old -> modern):")
    for old in ["architecto", "pharmacia", "caballo"]:
        modern = lex.archaic_words.get(old, "(unmapped)")
        ipa = lex.get_phonemes(old)
        print(f"  {old:12} -> {modern:12} /{ipa}/")
    print()

    print(f"silent-p words: {len(lex.silent_p_words)}")
    print("  e.g.", sorted(lex.silent_p_words)[:4])

    print(f"voiced-u words: {len(lex.voiced_u_words)}")
    print("  e.g.", sorted(lex.voiced_u_words)[:4])


if __name__ == "__main__":
    main()
