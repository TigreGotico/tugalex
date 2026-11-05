# Advanced

Recipes and edges beyond the basic lookups. All snippets use only the public API
and the packaged data.

## Build a grapheme-to-phoneme map for a model

> **Deprecated.** `get_ipa_map()`, `get_phonemes()` and the dictionary views `ipa`,
> `syllables`, `regions` and `possible_postags` emit a `DeprecationWarning`.
> The next major release removes them, together with the legacy
> `tugaphone.dialects` inventories that read them. For Portuguese
> pronunciation, use orthography2ipa with the pt-PT lexicon of
> `o2i-lexicons`.

`get_ipa_map()` hands you a flat `{word: phonemes}` dictionary for one POS and
region. This is exactly the shape a G2P training step or a TTS front-end wants.

```python
from tugalex import TugaLexicon

lex = TugaLexicon()
nouns = lex.get_ipa_map(pos="NOUN", region="lbx")
verbs = lex.get_ipa_map(pos="VERB", region="lbx")
print(len(nouns), len(verbs))   # tens of thousands each
```

To get every POS for every word, walk `possible_postags`. A word outside the
homograph table carries the single tag `""`, its POS-free entry:

```python
for word, tags in list(lex.possible_postags.items())[:5]:
    for tag in tags:
        print(word, tag, lex.get_phonemes(word, pos=tag))
```

## Resolve homographs correctly

A homograph carries a different transcription per POS. The homograph table is
consulted before the regional dictionary. Always pass the POS you mean:

```python
lex.get_phonemes("para", pos="ADP")    # ˈpɐɾɐ  (the preposition "for")
lex.get_phonemes("para", pos="VERB")   # ˈpaɾɐ  (he/she stops)
```

The full table is `lex.homographs`, shaped as `{word: {POS: ipa}}`.

## Archaisms fold into pronunciation automatically

When you ask for the phonemes of a pre-20th-century spelling, TugaLex rewrites
it to its modern form first, so you still get a transcription:

```python
lex.archaic_words["pharmacia"]      # 'farmácia'
lex.get_phonemes("architecto")      # 'ɐɾ·ki·tˈɛ·tu'  (looked up as arquiteto)
```

## Round-trip orthography across the AO1990 agreement

`normalize_ao1900()` goes from old to modern spelling. The two `reverse_*`
methods go from modern back to old, one per standard. Unmapped words pass
through unchanged. Strip punctuation and lowercase the words first, because
the lookup matches each whitespace-separated word exactly.

```python
modern = lex.normalize_ao1900("acção óptimo")   # 'ação ótimo'
back_pt = lex.reverse_ao1900_pt("ótimo")         # 'óptimo'
```

PT and BR diverge. A word can revert differently per standard, which is why
there are two reverse methods instead of one.

## Detect spelling phenomena

Two cached sets expose AO1990-related phenomena directly:

```python
sorted(lex.silent_p_words)[:3]    # words with a silent p, e.g. 'assimptota'
sorted(lex.voiced_u_words)[:3]    # words that used to carry the trema ü
```

Use them to flag tokens that need special attention in a pronunciation or
spell-checking pipeline.

## Gotchas

- **POS casing.** The homograph table uses uppercase tags (`NOUN`, `VERB`,
  `ADJ`, `ADP`). A lowercase tag misses the homograph table and silently
  falls back to the POS-free regional entry: `get_phonemes("acordo", pos="noun")`
  gives `'ɐ·kˈoɾ·du'`, not the homograph entry `'ɐˈkoɾdu'`.
- **Unknown words return falsy, they do not raise.** `get_phonemes` returns
  `None` and `get_syllables` returns `[]` for words not in the dataset. An
  unsupported *region*, by contrast, raises `ValueError` from `get_phonemes`,
  `get_syllables`, `get_wordlist`, `get_ipa_map`, and `lang_to_region`.
- **First touch is slow.** The first access to `ipa`, `syllables`, `regions`, or
  any method that uses them parses the large CSV. Construct one `TugaLexicon`
  and reuse it across calls.
- **One region more than the five public dialects.** `lex.regions` also
  contains `spx` (São Paulo). Only the five in `lang_to_region` have ISO
  aliases. Reach `spx` with a raw `region=` value.
- **Two transcription styles.** The homograph table writes the stress mark
  before the syllable (`ɐˈkoɾdu`). The regional dictionary marks syllables with
  `·` and writes the stress mark before the vowel (`ɐ·kˈoɾ·du`).
- **AO1990 conversion matches whole whitespace-separated words.** A word with
  attached punctuation or a capital letter is not converted, and runs of spaces
  become one space ([#46](https://github.com/TigreGotico/tugalex/issues/46)).
- **Method names read `1900`.** `normalize_ao1900`, `reverse_ao1900_pt`, and
  `reverse_ao1900_br` all implement the AO1990 agreement.

---
[← API reference](api.md) · [Home](../README.md)
