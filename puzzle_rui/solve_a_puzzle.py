#! /usr/bin/python

"""
solve_a_puzzle.py

Solves just one puzzle, prints the results
"""

import sys
import puzzle
import solver
import components_eval
import pickle


def print_dict(d,depth=0):
    for k,v in d.items():
        if type(v)==type({}):
            print "\t"*depth,k
            print_dict(v,depth+1)
        else:
            print "\t"*depth,k,":","%.2f" % v

def solve_a_puzzle(puz_file, component_list_path,mode=1,limit=300,score_adjust=20, n=1, second_round=True):
    print puz_file
    picklefile = 'cache/' + puz_file.replace('.', '').replace('/', '') + '.dat'
    try:
        all_output, comps_eval = pickle.load(open(picklefile))
    except IOError:
        # doesn't exist
        all_output,comps_eval = components_eval.run_all_components(puz_file, component_list_path, False)
        pickle.dump((all_output, comps_eval), open(picklefile, 'w'))

    print "####################### finished component ####################### "
    
    p = puzzle.Puzzle(puz_file)
    print p.get_initial_state()
    print p.get_all_clues()
    print p.get_grid()
    solver_evaluation,solution = solver.solve_puzzle(p,all_output,mode,limit,score_adjust, n=n, second_round=second_round)
    return p.get_side_by_side_comparison(), solver_evaluation, comps_eval, solution

if __name__ == "__main__":
    if 4 <= len(sys.argv) <= 5:
        # if 5 args, we don't fill blanks
        res = solve_a_puzzle(sys.argv[1],sys.argv[2], n=int(sys.argv[3]), second_round = False if len(sys.argv)==5 else True)
     
        res = res[:-1]
        print
        for r in res:
            if type(r)==type({}):
		print "================="
                print_dict(r)
            else:
		print "================="
                print r
            print
    else:
        print "usage: ./solve_a_puzzle <puz_file_path> <component_list_path> <n>"
