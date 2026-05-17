import re
import xml.etree.ElementTree as ET
from collections import Counter

from wiki_xml import q

# Simple find/replace passes for Fandom-only tags. Each entry compiles to a
# transform that does `pattern.sub(replacement, text)`
TAG_STRIPS = [
    ("strip_bloglist", r"<bloglist\b[^>]*>.*?</bloglist>", "<!-- bloglist removed (Fandom-only) -->"),
    ("strip_forum_tag", r"<forum\b[^>]*>.*?</forum>", "<!-- forum listing removed (Fandom-only) -->"),
]


def _tag_strip(pattern: str, replacement: str):
    compiled = re.compile(pattern, re.DOTALL | re.IGNORECASE)
    return lambda text: compiled.sub(replacement, text)


_AC_METADATA_RE = re.compile(r"<ac_metadata\b([^>]*)>.*?</ac_metadata>", re.DOTALL | re.IGNORECASE)
_AC_TITLE_RE = re.compile(r'\btitle\s*=\s*"([^"]*)"', re.IGNORECASE)


def extract_ac_metadata(text: str) -> str:
    # Fandom attaches the human-readable thread title via `title=` on this tag;
    # the page name itself is machine-generated (@comment-USERID-TIMESTAMP), so
    # promote the title to a heading rather than dropping it on the floor
    title: str | None = None

    def replace(match: re.Match[str]) -> str:
        nonlocal title
        if title is None:
            attr_match = _AC_TITLE_RE.search(match.group(1))
            if attr_match:
                candidate = attr_match.group(1).strip()
                if candidate:
                    title = candidate
        return ""

    stripped = _AC_METADATA_RE.sub(replace, text)
    if title is None:
        return stripped
    # `=` in a title would break heading parsing
    safe_title = title.replace("=", "-")
    return f"== {safe_title} ==\n\n{stripped.lstrip()}"


_CHOOSE_RE = re.compile(r"<choose\b[^>]*>.*?</choose>", re.DOTALL | re.IGNORECASE)


def flatten_choose(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        # The outer regex carves the block out of wikitext; the block itself is
        # well-formed XML, so parse it structurally rather than doing more regex
        try:
            choose = ET.fromstring(match.group(0))  # noqa: S314 -- local dump
        except ET.ParseError as e:
            raise ValueError(f"Could not parse <choose> block: {match.group(0)!r}") from e
        option = choose.find("option")
        if option is None:
            return ""
        parts = [option.text or ""]
        for child in option:
            parts.append(ET.tostring(child, encoding="unicode"))
        return "".join(parts)
    return _CHOOSE_RE.sub(replace, text)


WIKITEXT_TRANSFORMS = [
    *((name, _tag_strip(pattern, replacement)) for name, pattern, replacement in TAG_STRIPS),
    ("extract_ac_metadata", extract_ac_metadata),
    ("flatten_choose", flatten_choose),
]


def transform_page(page: ET.Element, stats: Counter) -> None:
    for revision in page.findall(q("revision")):
        # Skip revisions that do not have a text body
        text_elem = revision.find(q("text"))
        if text_elem is None or not text_elem.text:
            continue

        # Otherwise, sequentially apply transforms and track which ones change
        original = text_elem.text
        new_text = original
        for name, fn in WIKITEXT_TRANSFORMS:
            before = new_text
            new_text = fn(new_text)
            if new_text != before:
                stats[f"transform:{name}"] += 1
        if new_text != original:
            text_elem.text = new_text
            # The byte count attribute is stale after rewrites; recompute
            if "bytes" in text_elem.attrib:
                text_elem.attrib["bytes"] = str(len(new_text.encode("utf-8")))
