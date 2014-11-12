'''
@author: Jim
'''
import os

rootDir = '../test_month/'
rootDir = '../monday_puzzles/'
for n in range(5):
    print '####################### n =', n, ' #######################'
    for dirName, subdirList, fileList in os.walk(rootDir):
        for fname in fileList:
            if not fname.endswith('.puz'):
                continue
            fpath = rootDir + fname
            outname = 'month_n' + str(n) + '.out'
            outname = 'monday_n' + str(n) + '.out'
            cmd = 'python ./solve_a_puzzle.py ' + fpath + ' component_list ' + str(n) + ' no_second_round >> out/' + outname + ' 2>&1'
            print cmd
            os.system(cmd)