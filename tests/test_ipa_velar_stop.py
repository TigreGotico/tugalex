"""Regression test: IPA voiced velar stop must be U+0261 (ɡ), never ASCII "g".

TTS vocabularies downstream only recognize U+0261; an ASCII "g" (U+0067) in
the IPA transcription is silently dropped, deleting the /ɡ/ phoneme from
every word that contains it.
"""
import pytest

from tugalex import TugaLexicon

REGIONS = ["lbx", "rjx", "spx", "lda", "mpx", "dli"]


@pytest.fixture(scope="module")
def lex():
    return TugaLexicon()


class TestIPAVelarStop:
    def test_gato_uses_ipa_g(self, lex):
        mp = lex.get_ipa_map(region="lbx")
        assert "ɡ" in mp["gato"], mp["gato"]

    @pytest.mark.parametrize("region", REGIONS)
    def test_no_ascii_g_in_any_ipa_value(self, lex, region):
        mp = lex.get_ipa_map(region=region)
        offenders = {w: v for w, v in mp.items() if "g" in v}
        assert not offenders, (
            f"{len(offenders)} entries in region {region!r} contain ASCII "
            f"'g' (U+0067) instead of IPA 'ɡ' (U+0261), e.g. {next(iter(offenders.items()))}"
        )
