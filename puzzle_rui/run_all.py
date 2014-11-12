'''
@author: Jim
'''
import os

rootDir = '../monday_puzzles/'
rootDir = '../test_month/'
for n in range(5):
    print '####################### n =', n, ' #######################'
    for dirName, subdirList, fileList in os.walk(rootDir):
        for fname in fileList:
            if not fname.endswith('.puz'):
                continue
            fpath = rootDir + fname
            outname = 'monday_n' + str(n) + '.out'
            outname = 'month_n' + str(n) + '.out'
            cmd = 'python ./solve_a_puzzle.py ' + fpath + ' component_list ' + str(n) + ' >> out/' + outname
            print cmd
            os.system(cmd)