import argparse
import tempfile
import re
import csv

from libpytunes import Library

parser = argparse.ArgumentParser()
parser.add_argument('input', nargs=None, help='input itunes library .xml file')
parser.add_argument('output', nargs=None, help='output .csv file')
parser.add_argument('-p', '--preprocess-only', action='store_true', help='preprocess xml file only')
parser.add_argument('-n', '--no-preprocess', action='store_true', help='do not preprocess xml file')
args = parser.parse_args()


def preprocess(xml_file, output_file=None):
    substitutions = [
        (re.compile(r'<integer>(.*[\D\-/:A-z].*)</integer>'), r'<string>\1</string>'),
        (re.compile(r'<integer>(.*\..*)</integer>'), r'<real>\1</real>'),
        (re.compile(r'[\x00-\x07]'), ''),  # weird hex characters
        (re.compile(r'(Year.*>).*(\d{4}).*<'), r'\1\2<'),  # try to guess year from bad input
        (re.compile(r'(Year.*>)(.*)\.0+</'), r'\1\2</'),  # stupid Year stuff
        (re.compile(r'.*(Year.*>)[^<>]*\D[^<>]*</.*'), r''),  # stupid Year stuff
        (re.compile(r'.*>\W+</.*'), ''),   # whitespace only fields
    ]
    if output_file is None:
        output_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    else:
        output_file = open(output_file, 'w')

    # with open(xml_file, 'r') as fp_in, open('processed.xml', 'w') as tmp_file:
    with open(xml_file, 'r') as fp_in:
        for line in fp_in:
            for s in substitutions:
                line = re.sub(*s, line)
            output_file.write(line)

    try:
        output_file.close()
    except ValueError:
        pass

    return output_file.name


def main(input_file, output_file):
    lib = Library(input_file)

    for s_id, song in lib.songs.items():
        print(song.__dict__)
        exit()


if __name__ == '__main__':
    if args.no_preprocess:
        res_file = args.input
    else:
        res_file = preprocess(args.input)

    main(res_file, args.output)
