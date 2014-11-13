#! /usr/bin/python

# @package wordnet_antomym_component
# Uses nltk's WordNet integration to find the antonym of a word for clues that look like 
# Something's opposite or Something's antonym.
# Collects output and formats according to the component API
#
# Derek Van Assche
# Apr 2014

import sys
import re
from nltk.corpus import wordnet as wn


## Get answers from nltk's WordNet component
#
# @param clue the text of the clue to search for
# @param answer_length length of the expected answer in the puzzle
# @param limit number of responses to generate for each data source
def get_answers(clue,answer_length,limit=100):
    p = re.compile(r'Lemma\(\'([A-Za-z]+)[.]')
    answers = set()
    for synset in wn.synsets(clue):
        for lemma in synset.lemmas():
            antonyms = lemma.antonyms()
            for antonym in antonyms:
                match = p.search(str(antonym))
                if match:
                    answer = match.group(1)
                    if len(answer) == int(answer_length):
                        answers.add((answer.upper(),1))
                        if len(answers) > limit:
                            break
            if len(answers) > limit:
                break
        if len(answers) > limit:
            break
    return answers

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
        p = re.compile(r'^([A-Za-z]+)(([\'][s]){0,1}|([s][\']){0,1})\s(opposite|antonym)')
        match = p.search(clue)
        if match:
            answers = get_answers(match.group(1),length)
            if answers is not None:
                for answer in answers:
                    word,score = answer
                    print "\t".join([clueid,word,str(score)])
        else:
            p = re.compile(r'^([Oo]pposite|[Aa]ntonym)\s(of|for)\s(\'|\"){0,1}([\w]+)(\'|\"){0,1}$')
            match = p.search(clue)
            if match:
                answers = get_answers(match.group(4),length)
                if answers is not None:
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
