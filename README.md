# av-wiki-process

Processes a mediawiki XML dump of the Axiom Verge fandom wiki into something importable by a vanilla mediawiki instance.

Fandom-specific namespaces (Forum, User blog, Message Wall, Thread, Board, Board Thread, Map) are preserved - the destination wiki is expected to declare them via `$wgExtraNamespaces` and lock them via `$wgNamespaceProtection`. Wikitext cleanup focuses on Fandom-only tags that vanilla mediawiki can't render.

## Usage

```sh
uv sync
uv run python main.py                  # reads ./wikidump, writes <input>.processed.xml
uv run python main.py -i path/to/dump.xml -o out.xml
```

A directory argument is auto-resolved by globbing for the single non-`.processed.xml` file inside it.

## Layout

- `main.py` - core program logic: parse -> filter -> transform -> write
- `wiki_xml.py` - namespace helpers for ElementTree.
- `transforms.py` - per-revision wikitext transforms.
- `filters.py` - page-level filtering.
