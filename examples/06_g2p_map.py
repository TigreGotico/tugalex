"""Example — build a flat grapheme-to-phoneme map for a model front-end.

Run::

    python examples/06_g2p_map.py
"""
from tugalex import TugaLexicon


def main() -> None:
    lex = TugaLexicon()

    g2p = lex.get_ipa_map(pos="NOUN", region="lbx")
    print(f"NOUN g2p entries: {len(g2p)}")

    # Transcribe a small inline sentence, word by word, falling back gracefully.
    sentence = "o acordo da casa"
    print(f"\ntranscribing: {sentence!r}")
    for word in sentence.split():
        ipa = g2p.get(word) or lex.get_phonemes(word, pos="NOUN") or "?"
        print(f"  {word:8} -> /{ipa}/")


if __name__ == "__main__":
    main()
