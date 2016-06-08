import getopt
import os
import sys

from tools.tparsing import BaseParser
from tools.utils import get_free_vars


def solve(input_file, output_file):
    parser_ = BaseParser()
    exp = parser_.parse(input_file.readline())

    for var in sorted(get_free_vars(exp)):
        output_file.write(var + "\n")


def main(argv):
    input_file = 'test2.in'
    output_file = 'test2.out'

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input_file=", "output_file="])
    except getopt.GetoptError:
        print("first.py -i <input_file> -o <output_file>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("second.py -i <input_file> -o <output_file>")
            sys.exit()
        elif opt in ("-i", "-input_file"):
            input_file = arg
        elif opt in ("-o", "-output_file"):
            output_file = arg

    script_path = os.path.dirname(__file__)
    input_ = open(os.path.join(script_path, input_file), "r")
    output_ = open(os.path.join(script_path, output_file), "w")

    solve(input_, output_)


if __name__ == "__main__":
    main(sys.argv[1:])
