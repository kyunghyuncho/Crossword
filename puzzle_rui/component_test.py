#! /usr/bin/python

"""
component_test.py

run a single component over a directory of puz files to get overall results
as well as some feedback along the way
"""

import re
import os
import sys
import subprocess
import puzzle

def run_test(puz_file, component_path, save_result_path = None):
    puz = puzzle.Puzzle(puz_file)
    
    sys.stderr.write("solving: " + puz_file + '.....\n')
    #print component_path
 
    proc = subprocess.Popen([component_path],stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
  
    total_clues = puz.get_all_clues()
    total_number_clues = len(total_clues.split('\n'))
    #print "number_clues: =======================", total_number_clues
    #print total_clues
    output = proc.communicate(total_clues)
    #print "=============================2================================="
    clues_with_answer_in_list = 0
    clues_attempted = 0
    if save_result_path:
        with open(save_result_path, 'a') as outfile:
            outfile.write(output)
    answers_given = {}
    for line in output[0].split('\n'):
        if line == '':
            continue
        clue_id = None
        answer = None
        score = None
        try:
            clue_id, answer_and_score = line.split('\t', 1)
            if '\t' in answer_and_score:
                answer, score = answer_and_score.split('\t')
            else:
                answer = answer_and_score
                score = 1
            assert clue_id.strip() != ''
        except:
            raise IOError('output format not recognized for line: ' + line)

        if clue_id not in answers_given:
            answers_given[clue_id] = []
        answers_given[clue_id].append((answer, float(score)))

    total_inv_rank = 0
    for clue_id, answers_scores in answers_given.items():
        print "c,a", clue_id, answers_scores
        sorted_answers = [ a[0].upper().strip() for a in sorted(answers_scores, key=lambda x: x[1], reverse=True) ]
        print "sorted_answers ",
        for sa in sorted_answers:
            print sa,
        print
        correct_answer = puz.entries[clue_id].answer
        inv_rank = 0
        clues_attempted = clues_attempted + 1.0
        if correct_answer.upper().strip() in sorted_answers:
            index = sorted_answers.index(correct_answer)
            total_inv_rank += 1.0 / (index + 1)
            clues_with_answer_in_list = clues_with_answer_in_list + 1.0
            print 'clue', clue_id, ' : ' + puz.entries[clue_id].clue + ' answer was', correct_answer, '\tcomponent produced answer with rank:', index
        else:
            print 'clue', clue_id, ' : ' + puz.entries[clue_id].clue + ' answer was', correct_answer, '\tcomponent did not produce correct answer. Top answer was', sorted_answers[0]

    if answers_given:
        MRAR = total_inv_rank / len(answers_given)
        Precision = clues_with_answer_in_list / clues_attempted
        Attempt_ratio = clues_attempted / total_number_clues
        return ({'MRAR': MRAR,
          'Precision': Precision,
          'Attempt_ratio': Attempt_ratio}, output)
    else:
        return (None, output)


def run_all(puz_dir, component_path):
    all_results = {}
    for puz_file in os.listdir(puz_dir):
        if re.match('[^.].*\\.puz', puz_file):
            #print "Solving puzzle " + puz_file, "....................................."
            result, output = run_test(puz_dir.rstrip(os.sep) + os.sep + puz_file, component_path)
            if result:
                print puz_file, result
                all_results = merge_results(all_results, result)
            else:
                print 'No attempts to solve clues in', puz_file, 'were made...'

    print 'Overall average:', all_results
    return all_results


def merge_results(dest, in_dir):
    if dest == {}:
        dest = in_dir
        dest['N'] = 1
    else:
        for k, v in in_dir.items():
            current = dest[k]
            total = current * dest['N']
            total += v
            dest['N'] += 1
            dest[k] = float(total) / dest['N']

    return dest


if __name__ == '__main__':
    if len(sys.argv) == 3:
        run_all(sys.argv[1], sys.argv[2])
    else:
        print 'usage: ./component_test.py <puz_directory> <path_to_component>'
