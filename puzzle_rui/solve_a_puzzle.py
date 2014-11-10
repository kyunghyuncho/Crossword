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

def solve_a_puzzle(puz_file, component_list_path,mode=1,limit=300,score_adjust=20):
    print puz_file
    all_output, comps_eval = pickle.load(open('interesult.dat'))
#     all_output,comps_eval = components_eval.run_all_components(puz_file, component_list_path, False)
#     print "####################### finished component ####################### "
#     print "all_output", all_output raw_input('continue')
#     print "comps_eval", comps_eval raw_input('continue')
#     pickle.dump((all_output, comps_eval), open('interesult.dat', 'w'))
    
    p = puzzle.Puzzle(puz_file)
    print p.get_initial_state()
    print p.get_all_clues()
    print p.get_grid()
    solver_evaluation,solution = solver.solve_puzzle(p,all_output,mode,limit,score_adjust)
    return p.get_side_by_side_comparison(), solver_evaluation, comps_eval, solution

if __name__ == "__main__":
    if len(sys.argv) == 3:
        res = solve_a_puzzle(sys.argv[1],sys.argv[2])        
     
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
        print "usage: ./solve_a_puzzle <puz_file_path> <component_list_path>"
