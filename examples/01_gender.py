"""Example — the grammatical gender of common nouns and given names.

Run::

    python examples/01_gender.py
"""
from tugalex import TugaLexicon


def main() -> None:
    for noun in ["lei", "dias", "nações", "artista", "ainda"]:
        print(f"{noun:10} {TugaLexicon.get_noun_gender(noun)}")
    print()
    for name in ["Isabel", "João", "Darci", "isabel"]:
        print(f"{name:10} {TugaLexicon.get_given_name_gender(name)}")


if __name__ == "__main__":
    main()
