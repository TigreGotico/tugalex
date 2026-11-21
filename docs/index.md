# TugaLex documentation

<!-- agent-hint
covers: every documentation page in reading order, with what the reader gets from each
source: `docs/`
generated: no
verify: diff <(ls docs/*.md | xargs -n1 basename | grep -v '^index.md$' | LC_ALL=C sort) <(grep -o '^| \[[^]]*\]([a-z_]*\.md)' docs/index.md | sed 's/.*(\(.*\))/\1/' | LC_ALL=C sort)
see: `../README.md`, `../AGENTS.md`
-->

TugaLex is a lexicon library for Portuguese: a word list, noun and given-name gender, and homograph pronunciations. These pages show each lookup and list every public name.

| Page | You get |
| --- | --- |
| [quickstart.md](quickstart.md) | Install, then each lookup with its real output, and the deprecated calls with their replacements |
| [api.md](api.md) | Every public name with its signature, default and return value, and the replacement for each deprecated name |
| [advanced.md](advanced.md) | Recipes for G2P maps, homographs and spelling tables, and the edge cases of the lookups |
| [datasets.md](datasets.md) | The data files in the wheel, how to rebuild them, and the projects that use TugaLex |

## Pick a starting page

| You want to | Start with |
| --- | --- |
| Get the gender of a noun or a name | [quickstart.md](quickstart.md) |
| Look up a method, a default or a deprecated name | [api.md](api.md) |
| Replace a deprecated call before 3.0.0 | [api.md](api.md#deprecated-names) |
| Rebuild a dataset | [datasets.md](datasets.md) |
| Change the repository | [AGENTS.md](../AGENTS.md) |

Runnable scripts for each feature are in [examples/](../examples).

---
[Home](../README.md) · [Quickstart →](quickstart.md)
