#! /usr/bin/python

# @package lucene_component
# Run's derek's lucene script (../derek/search_clues.bash)
# Collects output and formats according to the component API
#
# Steve Wilson
# Apr 2014

import subprocess
import sys

SEARCH_CLUES_PATH = "~/Project3/source_code/derek/search_clues.bash"

def preprocess_clue(clue):
    if clue[0] == '*':
        clue = clue[1:]
 
    if clue.count('"')%2==1:
        clue=clue.replace('"',' ')
    clue = clue.replace("'",r"\'")
    clue = clue.replace("(",r"\(")
    clue = clue.replace(")",r"\)")
    clue = clue.replace("&",r"\&")
    clue = clue.replace("!",r"\!")
    return clue

## Get answers from the search_clues.bash script
#
# @param clue the text of the clue to search for
# @param answer_length length of the expected answer in the puzzle
# @param limit number of responses to generate for each data source
def get_answers(clue,answer_length,limit=10):
#    sys.stderr.write("attempting to search for "+clue+'\n')
    json_obj = subprocess.check_output(SEARCH_CLUES_PATH +' ' + str(limit) + ' ' + preprocess_clue(clue), shell=True)
    results_dict = eval(json_obj)
    answers = []
    # here we hard code the strings we are looking for since they
    # are different for wikipedia and the other data sources
    if 'results' in results_dict['clue-search']:
        for result in results_dict['clue-search']['results']:
            if len(result['word']) == int(answer_length):
                answers.append((result['word'],float(result['score'])))
    if 'results' in results_dict['otsys-search']:
        for result in results_dict['otsys-search']['results']:
            if len(result['word']) == int(answer_length):
                answers.append((result['word'],float(result['score'])))
    if 'results' in results_dict['wikipedia-search']:
        for wikiresult in results_dict['wikipedia-search']['results']:
            if len(wikiresult['compressed-word']) == int(answer_length):
                answers.append((wikiresult['compressed-word'],float(wikiresult['score'])))
#    sys.stderr.write(str(answers)+'\n')
    return answers

## Process one line of either stdin or reading from a file
#
# @param line the line itself
def process_line(line):
    if line.strip() != "":
        clueid,clue,length = line.split('\t')
        answers = get_answers(clue,length)
        for answer in answers:
            word,score = answer
            print "\t".join([clueid,word,str(score)])

if __name__ == "__main__":
    if len(sys.argv) == 2:
        for line in open(sys.argv[1]).readlines():
            process_line(line)
    elif len(sys.argv) == 1:
        for line in sys.stdin:
            process_line(line)
