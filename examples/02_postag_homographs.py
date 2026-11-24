"""Example — part-of-speech changes the pronunciation (heterophonic homographs).

Run::

    python examples/02_postag_homographs.py
"""
from tugalex import TugaLexicon


def main() -> None:
    lex = TugaLexicon()

    # "acordo" is the noun "an accord" or the verb "I wake up" — different vowel.
    print("acordo as NOUN:", lex.homographs["acordo"]["NOUN"])
    print("acordo as VERB:", lex.homographs["acordo"]["VERB"])
    print()

    # A few words straight from the homograph table, every variant they carry.
    for word in ["para", "pelo", "seco"]:
        variants = lex.homographs.get(word, {})
        rendered = ", ".join(f"{pos}=/{ipa}/" for pos, ipa in variants.items())
        print(f"{word:8} {rendered}")


if __name__ == "__main__":
    main()
