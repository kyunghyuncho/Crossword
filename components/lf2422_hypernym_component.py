#! /usr/bin/python
"""
Linxi Fan
lf2422

Uses nltk's WordNet integration to find the hypernym of a word for clues that look like 
XX and XX, XX or XX, 'for example'
Collects output and formats according to the component API
"""

import sys
import re
from nltk.corpus import wordnet as wn


## Get answers from nltk's WordNet component
#
# @param clue the text of the clue to search for
# @param answer_length length of the expected answer in the puzzle
# 'for example' questions
def get_for_example(clue,answer_length):
    answers = []
    max_disambig = 3  # maximum meaning disambiguation
    for synset in wn.synsets(clue):
        if max_disambig == 0:
            break
        max_disambig -= 1
        # maximum hypernym level
        hyper_level = 4
        for entry in synset.closure(lambda x : x.hypernyms()):
            if hyper_level == 0:
                break
            hyper_level -= 1
            answer = str(entry)[len('Synset(\'') : -2]
            answer = answer.split('.')[0]
            answerlis = answer.split('_')
            if len(answerlis) > 1:
                answerlis = answerlis[1:] + [answer.replace('_', '')]
            for answer in answerlis:
                if len(answer) == answer_length:
                    answers.append(answer.upper())
#         for lemma in synset.lemmas():
#             hypers = lemma.hypernyms()
#             for hyper in hypers:
#                 match = p.search(str(hyper))
#                 if match:
#                     answer = match.group(1)
#                     if len(answer) == int(answer_length):
#                         answers.add((answer.upper(),1))
#                         if len(answers) > limit:
#                             break
#             if len(answers) > limit:
#                 break
    if len(answers) == 0:
        return None

    answer_dict = {}
    unitscore = 3.0 / len(answers)
    i = 1
    for ans in reversed(answers):
        answer_dict[ans] = unitscore * i
        i += 1
        
    return answer_dict


## and/or clue: Cronus and Hyperion
def get_and_or(clue1, clue2, answer_length):
    print "and_or:", clue1, clue2

## Process one line of either stdin or reading from a file
#
# @param line the line itself
def process_line(line):
    if line != "":
        clueid,clue,length = '','',''
        try:
            clueid,clue,length = line.split('\t')
        except Exception as e:
            print line
        
        clue = clue.lower()
        
        # "for example" clue
        matcher1 = re.compile(r"([\w\s]*\w)\s*,\s*for\s+example")
        m1 = matcher1.search(clue)
        
        # and/or clue
        matcher2 = re.compile(r"([\w\s]*\w)\s+(and|or)\s+([\w\s]*\w)")
        m2 = matcher2.search(clue)

        length = int(length)
        answers = None
        if m1 is not None:
            answers = get_for_example(m1.group(1), length)
        elif m2 is not None:
            answers = get_and_or(m2.group(1), m2.group(3), length)
            
        if answers is not None:
            for word in answers:
                print "\t".join([clueid,word,str(answers[word])])


if __name__ == "__main__":
    if len(sys.argv) == 2:
        for line in open(sys.argv[1]).readlines():
            process_line(line)
    elif len(sys.argv) == 1:
        for line in sys.stdin:
            process_line(line)
