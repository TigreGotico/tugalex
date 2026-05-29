# Advanced

Recipes and edges beyond the basic lookups. All snippets use only the public API
and the packaged data.

## Build a grapheme-to-phoneme map for a model

`get_ipa_map()` hands you a flat `{word: phonemes}` dictionary for one POS and
region — exactly the shape a G2P training step or a TTS front-end wants.

```python
from tugalex import TugaLexicon

lex = TugaLexicon()
nouns = lex.get_ipa_map(pos="NOUN", region="lbx")
verbs = lex.get_ipa_map(pos="VERB", region="lbx")
print(len(nouns), len(verbs))   # tens of thousands each
```

Need every POS for every word? Walk `possible_postags`:

```python
for word, tags in list(lex.possible_postags.items())[:5]:
    for tag in tags:
        print(word, tag, lex.get_phonemes(word, pos=tag))
```

## Resolve homographs correctly

A homograph carries a different transcription per POS, and the homograph table is
consulted before the regional dictionary. Always pass the POS you mean:

```python
lex.get_phonemes("para", pos="ADP")    # ˈpɐɾɐ  (the preposition "for")
lex.get_phonemes("para", pos="VERB")   # ˈpaɾɐ  (he/she stops)
```

The full table is `lex.homographs` — `{word: {POS: ipa}}`.

## Archaisms fold into pronunciation automatically

When you ask for the phonemes of a pre-20th-century spelling, it is rewritten to
its modern form first, so you still get a transcription:

```python
lex.archaic_words["pharmacia"]      # 'farmácia'
lex.get_phonemes("architecto")      # 'ɐɾ·ki·tˈɛ·tu'  (looked up as arquiteto)
```

## Round-trip orthography across the AO1990 agreement

`normalize_ao1900()` goes old → modern; the two `reverse_*` methods go modern →
old for each standard. Unmapped words pass through, so whole sentences are safe.

```python
modern = lex.normalize_ao1900("acção óptimo")   # 'ação ótimo'
back_pt = lex.reverse_ao1900_pt("ótimo")         # 'óptimo'
```

PT and BR diverge: a word can revert differently per standard, which is why there
are two reverse methods rather than one.

## Detect spelling phenomena

Two cached sets expose AO1990-related phenomena directly:

```python
sorted(lex.silent_p_words)[:3]    # words with a silent p, e.g. 'assimptota'
sorted(lex.voiced_u_words)[:3]    # words that used to carry the trema ü
```

Use them to flag tokens that need special attention in a pronunciation or
spell-checking pipeline.

## Gotchas

- **POS casing.** Lookups expect uppercase tags (`NOUN`, `VERB`, `ADJ`, `ADP`).
  A lowercase tag silently misses and you get `None`.
- **Unknown words return falsy, they do not raise.** `get_phonemes` returns
  `None` and `get_syllables` returns `[]` for words not in the dataset. An
  unsupported *region*, by contrast, raises `ValueError` from `get_syllables`,
  `get_wordlist`, `get_ipa_map`, and `lang_to_region`.
- **First touch is slow.** The first access to `ipa`, `syllables`, `regions`, or
  any method that uses them parses the large CSV. Construct one `TugaLexicon` and
  reuse it across calls.
- **More regions than the five public dialects.** `lex.regions` also contains
  internal codes such as `rjo`, `lbn`, `spx`, `map`, `spo`. Only the five in
  `lang_to_region` have ISO aliases; the rest are reachable by raw `region=`.
- **Method names read `1900`.** `normalize_ao1900` / `reverse_ao1900_pt` /
  `reverse_ao1900_br` implement the AO1990 agreement.

## Where next

- [quickstart.md](quickstart.md) — install and the core idea
- [api.md](api.md) — full signatures and return shapes
