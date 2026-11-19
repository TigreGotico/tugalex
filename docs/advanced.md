# Advanced

Recipes and edges beyond the basic lookups. All snippets use only the public API
and the packaged data.

## Build a grapheme-to-phoneme map for a model

> **Deprecated.** `get_ipa_map()`, `get_phonemes()` and the dictionary views `ipa`,
> `syllables`, `regions` and `possible_postags` emit a `DeprecationWarning`.
> TugaLex 3.0.0 removes them. The legacy `tugaphone.dialects`
> inventories read them and stop working then. For Portuguese
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

> **Deprecated.** `get_phonemes()` belongs to the deprecated dictionary API.
> The archaism table `archaic_words` is deprecated with the spelling
> accessors, and TugaLex 3.0.0 removes it. Its replacement is the etymological
> rows of `desacordo_ortografico/data/spelling.json`.

When you ask for the phonemes of a pre-20th-century spelling, TugaLex rewrites
it to its modern form first, so you still get a transcription:

```python
lex.get_phonemes("architecto")      # 'ɐɾ·ki·tˈɛ·tu'  (looked up as arquiteto)
```

The lookup reads the archaism table without a spelling warning.

## Modernise text for a variety

> **Deprecated.** `modern_spelling()` emits a `DeprecationWarning`, and
> TugaLex 3.0.0 removes it. Its replacement is
> `desacordo_ortografico.convert(text, source, "ao1990-pt") or "ao1990-br"`.

`desacordo_ortografico.convert()` rewrites a whole text from one norm to
another. Pass `etymological` as the source for a pre-1911 spelling and
`pt_1973` or `br_1971` for a pre-AO1990 spelling. Punctuation and capitals
stay, so you do not split the text into words first:

```python
from desacordo_ortografico import convert

convert("Pharmacia", "etymological", "ao1990-br")   # 'Farmácia'
convert("kilometro", "etymological", "ao1990-br")   # 'quilômetro'
convert("chronico", "etymological", "ao1990-pt")    # 'crónico'
convert("chronico", "etymological", "ao1990-br")    # 'crônico'
```

The two norms accent some words differently. AO1990 Base XI, 3º, writes a
stressed ⟨e⟩ or ⟨o⟩ before ⟨m⟩ or ⟨n⟩ in a proparoxytone with an acute or a
circumflex, by the vowel quality in each norm: `cómodo`/`cômodo`,
`fenómeno`/`fenômeno`.

## Round-trip orthography across the AO1990 agreement

> **Deprecated.** `normalize_ao1900()`, `reverse_ao1900_pt()` and
> `reverse_ao1900_br()` emit a `DeprecationWarning`, and TugaLex 3.0.0
> removes them. Their replacements are
> `desacordo_ortografico.convert(text, source, "ao1990-pt") or "ao1990-br"`,
> `desacordo_ortografico.convert(text, "ao1990-pt", "pt_1973")` and
> `desacordo_ortografico.convert(text, "ao1990-br", "br_1971")`.

`convert()` goes from old to modern spelling and back, one norm for each
standard. Unmapped words pass through unchanged:

```python
from desacordo_ortografico import convert

modern = convert("acção óptimo", "pt_1973", "ao1990-pt")   # 'ação ótimo'
back_pt = convert("ótimo", "ao1990-pt", "pt_1973")         # 'óptimo'
back_br = convert("ótimo", "ao1990-br", "br_1971")         # 'ótimo'
```

PT and BR diverge. A word can revert differently per standard, so each
standard has its own pre-AO1990 norm.

## Detect spelling phenomena

> **Deprecated.** `silent_p_words` and `voiced_u_words` emit a
> `DeprecationWarning`, and TugaLex 3.0.0 removes them. Their replacements
> are the pt_1973 rows and the br_1971 rows of
> `desacordo_ortografico/data/spelling.json`.

Each row of the desacordo_ortografico spelling table maps `form`, written in
the norm `era`, to `value`, written in the norm `target`. A cell with two
AO1990 forms joins them with `|`. These two sets hold the same words as the
deprecated TugaLex sets:

```python
import json
from importlib.resources import files

table = files("desacordo_ortografico").joinpath("data/spelling.json")
rows = json.loads(table.read_text(encoding="utf-8"))["rows"]

silent_p = {
    row["form"]
    for row in rows
    if row["era"] == "pt_1973"
    for cluster in ("mpc", "mpç", "mpt")
    for value in row["value"].split("|")
    if cluster in row["form"] and cluster not in value
}
voiced_u = {
    value
    for row in rows
    if row["era"] == "br_1971" and "ü" in row["form"]
    for value in row["value"].split("|")
}
sorted(silent_p)[:3]   # ['assimptota', 'assimptotismo', 'assimptótico']
sorted(voiced_u)[:3]   # ['Equídeos', 'aguentador', 'aguista']
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
- **The deprecated AO1990 methods match whole whitespace-separated words.** A
  word with attached punctuation or a capital letter is not converted, and runs
  of spaces become one space ([#46](https://github.com/TigreGotico/tugalex/issues/46)).
  `desacordo_ortografico.convert()` keeps punctuation and capitals.
- **Method names read `1900`.** The deprecated `normalize_ao1900`,
  `reverse_ao1900_pt`, and `reverse_ao1900_br` all implement the AO1990
  agreement.

---
[← API reference](api.md) · [Home](../README.md)
