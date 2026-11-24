# Advanced

<!-- agent-hint
covers: recipes for homographs and the word list, and the edge cases of the lookups
source: `tugalex/__init__.py`, `tests/test_lexicon.py`, `tests/test_wordlist.py`
generated: no
verify: d=$(mktemp -d) && sed '/^```/d' docs/advanced.md > $d/v.txt && python -I -m doctest $d/v.txt
see: `api.md`, `quickstart.md`, `index.md`
-->

This page gives recipes and edge cases beyond the basic lookups. The recipes use the public API and the packaged data.

## Resolve homographs

A homograph has a different transcription for each POS. `homographs` holds the table as `{word: {POS: ipa}}`. The first reading of *para* is the preposition "for", and the second is "he stops".

```python
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.homographs["para"]["ADP"]
'ˈpɐɾɐ'
>>> lex.homographs["para"]["VERB"]
'ˈpaɾɐ'
```

To list every reading of a word, walk its entry.

```python
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> for word in ["acordo", "seco"]:
...     for pos, ipa in lex.homographs[word].items():
...         print(word, pos, ipa)
acordo NOUN ɐˈkoɾdu
acordo VERB ɐˈkɔɾdu
seco ADJ ˈseku
seco VERB ˈsɛku
```

Two readings with the same POS, such as *sede* thirst and *sede* headquarters, need [bifonia](https://github.com/TigreGotico/bifonia).

## Compare the word lists of two regions

Each region has its own word list. A set difference shows the words that only one region lists.

```python
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lisbon, luanda = set(lex.get_wordlist("lbx")), set(lex.get_wordlist("lda"))
>>> sorted(lisbon - luanda), sorted(luanda - lisbon)
(['aminoácido', 'arabescar'], ['reda'])
```

## Gotchas

- **POS casing.** The homograph table uses uppercase tags (`NOUN`, `VERB`, `ADJ`, `ADP`). A lowercase tag is a missing key.
- **An unknown region raises.** `get_wordlist` raises `ValueError` for a region code that is not one of the six.
- **The word list is a copy.** `get_wordlist` returns a new list on each call, so a change to the list does not change the next result.
- **A given name matches exactly.** `get_given_name_gender("isabel")` is `None`, because the list writes the name as `Isabel`. `get_noun_gender` lowercases the word first.

The POS casing gotcha, shown:

```python
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.homographs["acordo"].get("noun") is None
True
>>> lex.homographs["acordo"]["NOUN"]
'ɐˈkoɾdu'
```

---
[← API reference](api.md) · [Home](index.md) · [Datasets →](datasets.md)
