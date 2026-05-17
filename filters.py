import xml.etree.ElementTree as ET
from collections import Counter

from wiki_xml import q

EMPTY_MSG_WALL_NS = "1200"  # Message Wall stub pages, mostly empty placeholders


def should_keep_page(page: ET.Element, stats: Counter) -> bool:
    ns_elem = page.find(q("ns"))
    ns = ns_elem.text if ns_elem is not None else None

    if ns == EMPTY_MSG_WALL_NS:
        revisions = page.findall(q("revision"))
        all_empty = True
        for rev in revisions:
            text_elem = rev.find(q("text"))
            if text_elem is not None and (text_elem.text or "").strip():
                all_empty = False
                break
        if all_empty:
            stats["dropped_empty_message_wall"] += 1
            return False

    return True
