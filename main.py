import argparse
import glob
import os
import sys
import xml.etree.ElementTree as ET
from collections import Counter

from filters import should_keep_page
from transforms import transform_page
from wiki_xml import q


def resolve_input(path: str) -> str:
    if os.path.isdir(path):
        xml_files = [
            f for f in glob.glob(os.path.join(path, "*.xml"))
            if not f.endswith(".processed.xml")
        ]
        if len(xml_files) != 1:
            raise ValueError(f"Expected 1 xml file, got {len(xml_files)}: {xml_files}")
        return xml_files[0]
    return path


def main(args) -> int | None:
    input_path = resolve_input(args.input)
    base, ext = os.path.splitext(input_path)
    output_path = args.output or f"{base}.processed{ext}"

    tree = ET.parse(input_path)  # noqa: S314 -- trusted local dump
    root = tree.getroot()

    stats: Counter = Counter()
    kept = 0
    for page in list(root.findall(q("page"))):
        if not should_keep_page(page, stats):
            root.remove(page)
            continue
        transform_page(page, stats)
        kept += 1

    tree.write(output_path, xml_declaration=True, encoding="utf-8")

    print(f"Wrote {output_path}")
    print(f"Kept {kept} pages")
    for key, n in sorted(stats.items()):
        print(f"  {key}: {n}")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input",
        help="Path to the .xml file, or a directory containing exactly one .xml file",
        default="wikidump",
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to write the processed XML (default: alongside input with .processed suffix)",
    )
    args = parser.parse_args()

    sys.exit(main(args) or 0)
