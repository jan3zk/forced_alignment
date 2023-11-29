import sys
from utils import intervals_from_trs

def fragmentize_trs(trs_path, out_dir):
	trs_intervals = intervals_from_trs(trs_path):

if __name__ == '__main__':
    # Set up argument parsing
    if len(sys.argv) < 2:
        print("Usage: python fragmentize_trs.py [trs_path] [out_dir]")
        sys.exit(1)

    fragmentize_trs(trs_path, out_dir)