"""Example — convert spelling across the AO1990 orthographic agreement.

The spelling accessors are deprecated: they emit a DeprecationWarning and are
removed in tugalex 3.0.0. desacordo_ortografico.convert(text, source, target)
replaces them::

    from desacordo_ortografico import convert

    convert("acção óptimo", "pt_1973", "ao1990-pt")   # 'ação ótimo'
    convert("ótimo", "ao1990-pt", "pt_1973")          # 'óptimo'
    convert("ato", "ao1990-br", "br_1971")            # 'ato'

Run::

    python examples/04_ao1990.py
"""
from tugalex import TugaLexicon


def main() -> None:
    lex = TugaLexicon()

    old = "acção óptimo"
    modern = lex.normalize_ao1900(old)
    print(f"old    : {old}")
    print(f"modern : {modern}")
    print()

    # Reverse modern spelling back to each pre-agreement standard.
    print("revert 'ótimo' to PT-PT:", lex.reverse_ao1900_pt("ótimo"))
    print("revert 'ato'   to PT-BR:", lex.reverse_ao1900_br("ato"))
    print()

    print("AO1990 entries loaded:", len(lex.AO1990))


if __name__ == "__main__":
    main()
