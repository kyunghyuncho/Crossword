
"""
print_puzzle
------
print .puz file in human readable format

puz file format documentation found at:
https://code.google.com/p/puz/wiki/FileFormat

Steve Wilson
Apr 2014
"""

import sys
import puzzle

def usage():
    print "usage: ./print_puzzle.py [-c] <path_to_puz_file>"
    print "-c\tonly print clues"
    print "-e\tonly print empty grid"
    print "-a\tonly print grid with answers"
    print "-j\tprint in json format"

if __name__ == "__main__":
    if len(sys.argv)==2:
        p = puzzle.Puzzle(sys.argv[1])
        print p
    elif len(sys.argv)==3:
        if sys.argv[1]=='-e':
            p = puzzle.Puzzle(sys.argv[2])
            print p.get_initial_state()
        elif sys.argv[1]=='-c':
            p = puzzle.Puzzle(sys.argv[2])
            print p.get_all_clues()
        elif sys.argv[1]=='-a':
            p = puzzle.Puzzle(sys.argv[2])
            print p.get_grid()
        elif sys.argv[1]=='-j':
            p = puzzle.Puzzle(sys.argv[2])
            print p.to_json()
        else:
            usage()
    else:
        usage()
