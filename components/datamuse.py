#!/usr/local/bin/python
"""
Use DataMuse API
"""

import sys
import re

import urllib2
import urllib



## Get answers from nltk's WordNet component
#
# @param clue the text of the clue to search for
# @param answer_length length of the expected answer in the puzzle
# 'for example' questions
def get_answers(clue,answer_length):
    query = urllib.urlencode([("rd", clue.lower().strip())])
    ret = urllib2.urlopen("http://api.datamuse.com/words?"+query).read()
    wordlist = eval(ret)

    if len(wordlist) < 1:
        return None

    answer_dict = {}
    i = 1
    for ii, s in enumerate(wordlist):
       if len(s['word']) == answer_length:
           answer_dict[s['word']] = s['score']
           i += 1
        
    return answer_dict


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
        length = int(length)
        answers = get_answers(clue, length)
        
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
