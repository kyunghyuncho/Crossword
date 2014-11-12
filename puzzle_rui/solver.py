#! /usr/bin/python

## @package solver.py
# Solves a puzzle using components to generate candidates
#
# Steve Wilson
# Edited: Rui Zhang
# Apr 2014
# July 2014

import sys
import re
import argparse
import string
import subprocess
import random
import time
import csp.csp as csp
import puzzle
import copy
from component_thread import myThread
from optparse import Values

# @param puz the puzzle object
# @param candidates_file input file of candidate answers
# @param limit only take the top <limit> answers
def generate_all_candidates(puz,limit,score_adjust,candidates_output=None):
    print 
    print "======================== Merge All candidats answers ================"
    data = []
    if candidates_output:
        data = candidates_output.split('\n')
    else:
        data = sys.stdin()
    answers_given = {}
    for line in data:
#         print "line", line
        if line == "":
            continue
        clue_id = None
        answer = None
        component_source = None
        score = 1
        try:
            items = line.split('\t')
            assert len(items) in [2,3,4]
        except:
#            raise IOError("format not recognized for line: "+line)
            continue
        else:
            if len(items) >= 2:
                clue_id,answer = items[:2]
            if len(items) >= 3:
                score = float(items[2])
            if len(items) == 4:
                component_source = items[3]
                score += score_adjust
            else:
                print "==========================abnormal length====================="	

        # make sure answer given is correct length
        assert len(answer) == puz.entries[clue_id].length

        if clue_id not in answers_given:
            answers_given[clue_id] = []
        skip = False
        for i in range(len(answers_given[clue_id])):
            if answer.upper() == answers_given[clue_id][i][0]:
                answers_given[clue_id][i]=(answer.upper(),float(score)+answers_given[clue_id][i][1],answers_given[clue_id][i][2]+[component_source])
                skip=True
        if not skip:
            answers_given[clue_id].append((answer.upper(),float(score),[component_source]))


    candidates = {}
    unanswered_clues = []
    for k in puz.entries.keys():
        if k in answers_given:
            candidates[k] = [x[0] for x in sorted(answers_given[k],key=lambda x:x[1], reverse=True)[:limit]]
        else:
	    #give unanswered_clue candidates as "-----"
            unanswered_clues.append(k)
            candidates[k] = []
            candidates[k].append('-'*puz.entries[k].length)

    puz.all_candidates = answers_given
    weights_dict = {}

    for k,answers in answers_given.items():
        weights_dict[k] = {}
        for answer in answers:
            weights_dict[k][answer[0]]=answer[1]

      
    #return candidates,weights_dict,unanswered_clues
    ''' evaluate merger results "candidates" '''
    rank_of_candidates = {}
    cnt = 0
    rank_sum = 0
    for k in candidates.keys():
	if candidates[k][0] != '-':
	    correct_answer = puz.entries[k].answer
            rank = 0
            find = False 

	    for candidate in candidates[k]:
                rank = rank + 1
                if candidate == correct_answer.upper():
                    rank_of_candidates[k] = rank
                    find = True
                    cnt = cnt + 1
                    rank_sum = rank_sum + rank
                    break

	    if find == False:
                rank_of_candidates[k] = -1
        else:
	    rank_of_candidates[k] = -1
    if cnt == 0:
        cnt = 1
    
    cnt_2 = 0
    temp_S = {}
    rank_answers = {}
    for k in puz.entries.keys():
        temp_S[k] = '-'*puz.entries[k].length
        rank_answers[k] = -1
    
    for k in answers_given.keys():
	rank = 0
        correct_answer = puz.entries[k].answer
        for candidate_tuple in sorted(answers_given[k],key=lambda x:x[1],reverse=True):
	    rank += 1
            if correct_answer.upper() == candidate_tuple[0]:
                temp_S[k] = correct_answer
		rank_answers[k] = rank
	        cnt_2 = cnt_2 + 1
                break

    ''' print how many candidates answers are generated for each clue'''
    tup_list = []
    for k in sorted(puz.entries.keys()):
        if k in answers_given.keys():
            if len(candidates[k])>1:
                first_score = weights_dict[k][candidates[k][0]]
                second_score = weights_dict[k][candidates[k][1]]
            else:
                first_score = weights_dict[k][candidates[k][0]]
		second_score = 0
	    tup_list.append((k,rank_answers[k],len(answers_given[k]),first_score,first_score-second_score))

        else:
	    tup_list.append((k,rank_answers[k],0,0,0))
    for tup in sorted(tup_list,key=lambda x:x[3],reverse=True):
        #print tup[0]+'\t'+str(tup[1])+' \ '+ str(tup[2])+'\t\t'+str(tup[3])+'\t'+str(tup[4])
        print tup[0]+'\t'+str(tup[1])+' \ '+ str(tup[2])

    print "max"+"\t"+str(max([rank_answers[k] for k in rank_answers.keys()]))+'/'+str(max([len(answers_given[k]) for k in answers_given.keys()])) 

    cnt_3 = 0
    for k in temp_S.keys():
        temp_S = puz.update_solution(temp_S,k)
    for k in temp_S.keys():
        if temp_S[k].upper() == puz.entries[k].answer.upper():
            cnt_3 += 1
        
    
    
    print 
    print "number of clues: " , len(puz.entries.keys())
    print "number of clues answered by some component: " , len(answers_given.keys())
    print "number of clues answered correctly by some component: " , cnt_2, "(",cnt_3,")"
    print "number of clues answered correctly in candidates list of CSP: " , cnt 
    print "with average rank: " , float(rank_sum)/cnt  , "/" , limit
    print 

    return candidates,weights_dict,unanswered_clues


class RebusError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def propagate(next_var, next_val, puz, domains, neighbors, S):
    #print 'calling propagate ...........'

    # Check for assigned neighbors of next variable
    for neighbor in neighbors[next_var]:
        # if this neighbor is already assigned
        if neighbor in S.keys():
            if puz.check_intersect(neighbor,S[neighbor],next_var,next_val) == False:
                return False, None, None

    # Give assignment to next variable
    next_S = copy.deepcopy(S)
    next_S[next_var] = next_val
    next_S = puz.update_solution(next_S,next_var)

    # Pop next variable in next_domains
    next_domains = copy.deepcopy(domains)
    next_domains.pop(next_var)
    
    # Check for non-assigned neighbors of next variable
    for neighbor in neighbors[next_var]:
        if neighbor not in S.keys():
            for neighbor_candidate in domains[neighbor]:
                # if conflict, remove it
                if puz.check_intersect(neighbor,neighbor_candidate,next_var,next_val) == False:
                    next_domains[neighbor].remove(neighbor_candidate)

    return True, next_domains, next_S


# A crude search algorithm
def solve_recursive(puz, variables, domains, neighbors, S, B, Pitched, n):
    # print 'calling solve_recursive.....'

    # If all variables assgined, update solution
    if len(variables) == len(S.keys()):
        # might be empy (unanswered_clues)
        scoreS = sum([weight_dict.get(sq, {}).get(S[sq], 0) for sq in S])
        scoreB = sum([weight_dict.get(sq, {}).get(B[sq], 0) for sq in B])
        return S if scoreS > scoreB else B

    unassigned_vars = list( set(variables) - set(S.keys()) )   
    
    localPitched = copy.deepcopy(Pitched)

    next_var = None
    max2_diff = - float('Inf')
    for var in unassigned_vars:
        if var in Pitched and set(domains[var]).issubset( localPitched.get(var, set()) ):
            continue
        values = [weight_dict[var][val] for val in domains[var]]
        if len(values) == 0:
            continue
#         values_diff = max(values) - select(values, 1)
        values_diff = values[0] - (values[1] if len(values) > 1 else 0)
        if values_diff > max2_diff:
            max2_diff = values_diff
            next_var = var
    
    if next_var is None or len(domains[next_var])==0:
        if next_var is None:
            next_var = unassigned_vars[0]
        S[next_var] = '-'*puz.entries[next_var].length
        for k in S.keys():
            S = puz.update_solution(S,k) 
        return solve_recursive(puz,variables,domains,neighbors,S, B, localPitched, n)
    else:
        i = 0
        while domains[next_var][i] in localPitched.get(next_var, []):
            i += 1

        next_val = domains[next_var][i]
        
        success, next_domains, next_S = propagate(next_var,next_val,puz,domains,neighbors,S)
        
        if success:
            B = solve_recursive(puz, variables, next_domains, neighbors, next_S, B, localPitched, n)
        if sum(len(localPitched[key]) for key in localPitched) < n:
            if next_var in localPitched:
                localPitched[next_var].add(next_val)
            else:
                localPitched[next_var] = {next_val}
            B = solve_recursive(puz, variables, domains, neighbors, S, B, localPitched, n)
        return B


## Second round: fill in the blanks
def fill_blanks(S, puz,domains,neighbors):
    for sq in S:
        if domains is None:
            break
        num_cand = len(domains[sq])
        if  num_cand == 0:
            continue
        fill_word = domains[sq][random.randint(0, num_cand-1)]
        success, domains, next_S = propagate(sq, fill_word, puz, domains, neighbors, S)
        if success:
            S = next_S
    return S


## Pre-process answers_cwg_otsys.txt
# hash length to an array of words
def preprocess_db(filename):
    # dictionary of all crossword solutions
    all_dict = {}
    for word in open(filename):
        word = word.strip()
        l = len(word)
        if l in all_dict:
            all_dict[l].append(word)
        else:
            all_dict[l] = [word]
    return all_dict

## generate 'domain' of fill-blank
def gen_blank_domain(S, all_dict):
    domain = {}
    for sq in S:
        cur = S[sq] # current solution with dashes
        domain[sq] = []
        if not '-' in cur: # cur is fully filled
            continue
        candidates = all_dict[len(cur)]
        for cand in candidates:
            match = True
            for i in range(len(cand)):
                if cur[i] != '-' and cur[i] != cand[i]:
                    match = False
                    break
            if match:
                domain[sq].append(cand)
    return domain


## Find a solution to the puzzle
def solve_puzzle(puz,component_output,mode,limit,score_adjust, n=1, second_round=True):
    if puz.is_rebus:
        raise RebusError("Solver cannot handle rebus style puzzles")

    global weight_dict
    puz.update_all_intersections()
    domains,weight_dict,unanswered_clues = generate_all_candidates(puz,limit,score_adjust,component_output)
    
    # construct CSP problem
    problem = csp.CSP(puz.entries.keys(),
                      domains,
                      {k:puz.entries[k].intersections.keys() for k in puz.entries.keys()},
                      puz.check_intersect)
    variables = puz.entries.keys()
    neighbors = {k:puz.entries[k].intersections.keys() for k in puz.entries.keys()}
    S = {}

    # assign variables which cannot be answered
    for k in unanswered_clues:
       	S[k] = domains[k][0] # this will be "-"*
        domains.pop(k)

    print "\nSolving CSP probelm ....."
    start = time.time()
    solution = solve_recursive(puz,variables,domains,neighbors,S, {}, {}, n)
    end = time.time()
    print("\nCSP solver runtime: " + str(end-start))

    # evaluate solution
    print "\nEvaluating solution ...."
    evaluation = puz.evaluate_solution(problem,solution,'_before_fill')
    evaluation['runtime_before_fill'] = end-start

    # PART 2 GOES HERE - FILL IN BLANK SQUARES
    if second_round:
        all_dict = preprocess_db('../answers_cwg_otsys.txt')
        domains = gen_blank_domain(solution, all_dict)
        orig = copy.deepcopy(solution)
        solution = fill_blanks(solution, puz, domains, neighbors)
        for sq in orig:
            if orig[sq] != solution[sq]:
                print orig[sq], 'vs', solution[sq]
        print "\nEvaluating filled solution ...."
        evaluation = puz.evaluate_solution(problem,solution,'_after_fill')

    end2 = time.time()
    print("\nBlank square filling runtime: " + str(end2-start))
    evaluation['runtime']=end2-start

    return evaluation,solution

## Handle command line arguments
def arg_parse():
    parser = argparse.ArgumentParser(description="Import a .puz file as a python puzzle obect and output a solution.")
    parser.add_argument('puz_file', metavar='puz_file', type=str,
                        help='path to the .puz file to load')
    parser.add_argument('candidates_file', metavar='candidates_file', type=str,
                        help='path to component output to use when generating candidate answers')
    return parser.parse_args()

#--- quickselect algorithm from Rosetta Code ----
def partition(vector, left, right, pivotIndex):
    pivotValue = vector[pivotIndex]
    vector[pivotIndex], vector[right] = vector[right], vector[pivotIndex]  # Move pivot to end
    storeIndex = left
    for i in range(left, right):
        if vector[i] > pivotValue:
            vector[storeIndex], vector[i] = vector[i], vector[storeIndex]
            storeIndex += 1
    vector[right], vector[storeIndex] = vector[storeIndex], vector[right]  # Move pivot to its final place
    return storeIndex
 
def _select(vector, left, right, k):
    while True:
        pivotIndex = random.randint(left, right)     # select pivotIndex between left and right
        pivotNewIndex = partition(vector, left, right, pivotIndex)
        pivotDist = pivotNewIndex - left
        if pivotDist == k:
            return vector[pivotNewIndex]
        elif k < pivotDist:
            right = pivotNewIndex - 1
        else:
            k -= pivotDist + 1
            left = pivotNewIndex + 1
 
def select(vector, k, left=None, right=None):
    """\
    Returns the k-th largest, (k >= 0), element of vector within vector[left:right+1].
    left, right default to (0, len(vector) - 1) if omitted
    """
    if k >= len(vector):
        return 0
    if left is None:
        left = 0
    lv1 = len(vector) - 1
    if right is None:
        right = lv1
    return _select(vector, left, right, k)
#----- End of quickselect -----

if __name__ == "__main__":
    args = arg_parse()
    p = puzzle.Puzzle(args.puz_file)
    evaluation = solve_puzzle(p,open(args.candidates_file).read())
    print p.get_side_by_side_comparison()
    for k,v in sorted(evaluation.items()):
        print k+':'+'\t'+str(v)
