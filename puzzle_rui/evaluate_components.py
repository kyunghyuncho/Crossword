#! /usr/bin/python

import os
import sys

'''

Rui Zhang
July 2014
'''

def test_components(puz_dir, component_list):
    f_list = open(component_list,'r')
    for line in f_list:
        component_path = line.split()[0]
        component_name = component_path.split('/')[-1][:-3]
        #print "evaluating: " + component_path + " ...", component_name
        command = "./component_test.py " + puz_dir + " " + component_path + " > ./component_eval_results/" + component_name + ".txt"
        print "command: " + command
        os.system(command)
        


if __name__ == "__main__":
    if len(sys.argv) == 3:
        puz_dir = sys.argv[1]
        component_list = sys.argv[2]
        test_components(puz_dir,component_list)
    else:
	print "usage: ./evaluate_components.py ../recent_nyt_puz_rui/ ./component_list"
