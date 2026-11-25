"""Example — the word list of each region.

Run::

    python examples/03_wordlist.py
"""
from tugalex import TugaLexicon


def main() -> None:
    lex = TugaLexicon()
    for region in ["lbx", "rjx", "spx", "lda", "mpx", "dli"]:
        words = lex.get_wordlist(region)
        print(f"{region}: {len(words)} words, first {words[0]!r}, last {words[-1]!r}")
    lisbon, luanda = set(lex.get_wordlist("lbx")), set(lex.get_wordlist("lda"))
    print("in Lisbon, not in Luanda:", sorted(lisbon - luanda))
    print("in Luanda, not in Lisbon:", sorted(luanda - lisbon))


if __name__ == "__main__":
    main()
