# API reference

<!-- agent-hint
covers: every public name of tugalex with its signature, default and return value
source: `tugalex/__init__.py`, `tests/test_api_surface.py`
generated: no
verify: d=$(mktemp -d) && sed '/^```/d' docs/api.md > $d/a.txt && python -I -m doctest $d/a.txt
see: `quickstart.md`, `advanced.md`, `index.md`
-->

This page lists the public names of `tugalex`. The package has one class, `TugaLexicon`, one function, `suffix_noun_gender`, and a few module constants.

```python
>>> from tugalex import TugaLexicon
```

## `TugaLexicon()`

The constructor takes no arguments. It loads the homograph table. The word list and the gender lists load on first use, and the module caches them for every instance.

## Word list

### `get_wordlist(region="lbx") -> List[str]`

Every word form known for a region, lowercase and sorted. It reads `tugalex/data/words.csv.gz`, which holds the word forms of the regional pronunciation dictionary and no pronunciations. It returns a new list on each call, and it raises `ValueError` for an unknown region.

```python
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> len(lex.get_wordlist("lbx"))
53147
>>> len(lex.get_wordlist("spx"))
53145
```

Region codes are `lbx` (Portugal), `rjx` (Brazil, Rio de Janeiro), `spx` (Brazil, São Paulo), `lda` (Angola), `mpx` (Mozambique) and `dli` (Timor-Leste).

## Noun gender

### `TugaLexicon.get_noun_gender(word) -> Optional[str]`

The grammatical gender of a Portuguese common noun, singular or plural, in any letter case. It is a static method and needs no instance.

It returns `"m"` or `"f"`, `"mf"` for a noun of both genders, or `None`. It returns `None` for a word that Wiktionary lists only in a closed class and with no gender, and when no rule applies and the word is not listed. A noun of both genders is a common-gender noun (`"o/a artista"`), a noun whose gender changes with its meaning (`"o rádio"`, the set; `"a rádio"`, the station), or a noun whose gender differs between Portugal and Brazil.

The exceptions file `tugalex/data/noun_gender_exceptions.csv.gz` decides first. Then the suffix rules in `tugalex.NOUN_GENDER_SUFFIXES` apply, in order. The suffixes `-ção`, `-são`, `-dade`, `-tude`, `-gem`, `-eza` and `-ise` are feminine. The suffixes `-o` (not `-ão`), `-or` and `-ume` are masculine, and `-a` is feminine. Plural forms of each suffix match too. The exceptions file also lists the closed-class words. A determiner, pronoun, article or contraction has its own gender (`uma`, `da`: `"f"`; `um`, `do`: `"m"`). A word that Wiktionary lists only in a closed class and with no gender, such as an adverb or a preposition, has an empty gender. These words get `None`, and the suffix rules do not apply to them.

```python
>>> from tugalex import TugaLexicon
>>> TugaLexicon.get_noun_gender("lei")
'f'
>>> TugaLexicon.get_noun_gender("dias")
'm'
>>> TugaLexicon.get_noun_gender("nações")
'f'
>>> TugaLexicon.get_noun_gender("artista")
'mf'
>>> TugaLexicon.get_noun_gender("zzk") is None
True
>>> TugaLexicon.get_noun_gender("ainda") is None
True
```

`lei` and `dias` come from the exceptions file, `nações` from the suffix `-ção`. `ainda` is an adverb, so the exceptions file gives it no gender.

### `suffix_noun_gender(word) -> Optional[str]`

The gender that the suffix rules alone give a word, or `None`. It ignores the exceptions file.

```python
>>> from tugalex import suffix_noun_gender
>>> suffix_noun_gender("nações")
'f'
>>> suffix_noun_gender("zzk") is None
True
```

`scripts/build_noun_gender.py` regenerates the exceptions file. It compares the suffix rules with the noun genders of the English Wiktionary and keeps the nouns that the rules get wrong or do not cover, and every noun of both genders. A determiner, pronoun, article, numeral or contraction with a gender keeps that gender, also when the word has a noun entry (`as`, `toda`: `"f"`). Otherwise a word with a noun entry gets the gender of that entry, also when it is a pronoun or an adverb too (`caso`: "o caso"). The script also keeps, with an empty gender, the words that Wiktionary lists only as an adverb, preposition, conjunction, pronoun, determiner, article, contraction or interjection and with no gender, where the suffix rules give a gender. `scripts/noun_gender_overrides.csv` sets the gender of forms that a rare sense would make both-gender: a loanword (`cores`: "a cor", beside the computing term "o core") or an insult (`banana`: "o banana", a weakling). It also sets, with a Priberam citation, the gender of nouns that the English Wiktionary lists only in a closed class (`contra`: "o contra"). An override with an empty gender lets the usual sense decide when a rare noun sense would give a gender (`agora`: "now", beside "o agora").

## Given-name gender

### `TugaLexicon.get_given_name_gender(name) -> Optional[str]`

The grammatical gender of a given name. It is a static method and needs no instance. It returns `"m"` or `"f"`, `"mf"` for a name that both sexes bear, or `None` for a name that is not on the list. The match is exact: write the name as in running text, with its capital letter and accents.

```python
>>> from tugalex import TugaLexicon
>>> TugaLexicon.get_given_name_gender("Isabel")
'f'
>>> TugaLexicon.get_given_name_gender("isabel") is None
True
```

The list is `tugalex/data/given_names.csv.gz`. `scripts/build_given_names.py` regenerates it from Wikidata and the IBGE 2010 census first names, and `scripts/given_name_overrides.csv` corrects the names whose Wikidata items mislead.

## Homographs

### `homographs: Dict[str, Dict[str, str]]`

The POS-dependent pronunciations of the 27 heterophonic homographs, shaped as `{word: {POS: ipa}}`. The table has 55 rows, and it is the same for every region. `homographs_path` is the path of the CSV that it comes from, `tugalex/data/heterophonic_homographs.csv`.

```python
>>> from tugalex import TugaLexicon
>>> lex = TugaLexicon()
>>> lex.homographs["para"]
{'ADP': 'ˈpɐɾɐ', 'VERB': 'ˈpaɾɐ'}
>>> len(lex.homographs), sum(len(tags) for tags in lex.homographs.values())
(27, 55)
```

## Module constants

| Name | Value |
| --- | --- |
| `NOUN_GENDER_SUFFIXES` | the ordered suffix rules of `get_noun_gender`, as `(gender, regex)` pairs |
| `NOUN_GENDER_PATH` | the path of `tugalex/data/noun_gender_exceptions.csv.gz` |
| `GIVEN_NAMES_PATH` | the path of `tugalex/data/given_names.csv.gz` |
| `WORDLIST_PATH` | the path of `tugalex/data/words.csv.gz` |

---
[← Quickstart](quickstart.md) · [Home](index.md) · [Advanced →](advanced.md)
