'''
Linxi Fan
lf2422
'''
import os

rootDir = 'out_old/'
header = 'monday_'
header = 'hard_'


for dirName, subdirList, fileList in os.walk(rootDir):
    for fname in fileList:
        if not fname.endswith('.out') or not fname.startswith(header):
            continue
        fpath = rootDir + fname
        print '='*20, fpath, '='*20
        for line in open(fpath):
            line = line.strip()
            # if line.startswith('../monday_puzzles'):
            if line.startswith('../test_month'):
                print "---- FILE -----", line
            if line.startswith('runtime_before_fill'):
                print line
            if line.startswith('total_'):
                print line
            if line.startswith('matching_words'):
                print line
            if line.startswith('matching_squares'):
                print line