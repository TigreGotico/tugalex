"""Regression test: IPA voiced velar stop must be U+0261 (ɡ), never ASCII "g".

TTS vocabularies downstream only recognize U+0261; an ASCII "g" (U+0067) in
the IPA transcription is silently dropped, deleting the /ɡ/ phoneme from
every word that contains it.
"""
from tugalex import TugaLexicon


def test_gosto_uses_ipa_g():
    assert "ɡ" in TugaLexicon().homographs["gosto"]["NOUN"]


def test_no_ascii_g_in_any_homograph():
    offenders = {(word, pos): ipa
                 for word, tags in TugaLexicon().homographs.items()
                 for pos, ipa in tags.items() if "g" in ipa}
    assert not offenders
