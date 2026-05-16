import argparse
import glob
import os

from mwxml import Dump


def main(args):
    file_path = args.input

    if os.path.isdir(file_path):
        xml_files = glob.glob(os.path.join(file_path, '*.xml'))
        if len(xml_files) != 1:
            raise ValueError(f"Expected 1 xml file, got {len(xml_files)}: {xml_files}")
        file_path = xml_files[0]

    dump = Dump.from_file(open(file_path))

    # import bpdb
    # bpdb.set_trace()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Path to the directory containing .xml file', default='wikidump')
    args = parser.parse_args()

    main(args)
