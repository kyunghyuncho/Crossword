#!/usr/local/bin/python

# @package fill_in_the_blank_component
#  attempts to solve fill in the blank crossword clues
#  e.g., "Sierra ____" or "Billy ____ Williams"
#
# Steve Wilson
# Apr 2014

import sys
import re
import nltk
import subprocess
from component_thread import myThread

SEARCH_CLUES_PATH = "../derek/search_wiki.bash"

def generate_exact_phrase_pattern(text,ans_len):
    phrase = text.split('"')[1]
    regex = phrase.replace('.','\.?')
    # only allow 5 spaces in answer
    regex = re.sub("_+","([\w\s]{"+ans_len.strip()+","+str(int(ans_len)+5)+"})",regex)
    regex = regex.replace(' ',r'\s+')
    pattern = re.compile(regex,re.I)
    return pattern

# max_n must be > 1
def generate_ngram_patterns(text,ans_len,max_n=3):
    words = text.split()
    index = None
    # find the blank
    for i,word in enumerate(words):
        if re.search("_+",word):
            index = i
            break
    # change blank to wildcard expression
    words[index] = re.sub("_+","([\w\s]{"+str(ans_len).strip()+","+str(int(ans_len)+5)+'})',words[index])
    windows = set([])
    for x in range(index+1):
        for l in range(2,max_n+1):
            if index-x<=l-1 and x+l-1 < len(words) and x>=0:
                windows.add( (x,x+l-1) )
    for x in range(index,len(words)):
        for l in range(2,max_n+1):
            if x-index<=l-1 and x< len(words) and x-l+1>=0:
                windows.add( (x-l+1,x) )
#    sys.stderr.write(str(windows)+'\n')
#    sys.stderr.write(str(words)+'\n')
    patterns = [re.compile("[^a-z]"+"\s".join(words[window[0]:window[1]+1])+"[^a-z]",re.I) for window in list(windows)]
    return patterns

class ScoreDict:

    def __init__(self):
        self.d = {}

    def add(self,item):
        if item in self.d:
            self.d[item]+=1
        else:
            self.d[item]=1
#        sys.stderr.write("CAND: "+item+" current:"+str(self.d[item]) +'\n')

    def to_list(self):
        l = []
        for k,v, in self.d.items():
            l.append( (k,v) )
        return l

## Find ngram candidate
#
# @param clue the text of the clue, used to make regex
# @param wikiresult a lucene result for a wikipedia article related to clue
def find_ngram_candidates(clue,wikiresult,ans_len,cands):
    patterns = []
    if re.search('".*_+.*"',clue):
        patterns.append(generate_exact_phrase_pattern(clue,ans_len))
    else:
        patterns = generate_ngram_patterns(clue,ans_len)
    try:
        with open(wikiresult['local-path']) as article:
            for line in article:
                for sentence in nltk.sent_tokenize(line):
                    for pattern in patterns:
                        match = pattern.findall(sentence)
                        if match:
#                           sys.stderr.write(pattern.pattern+"\nfound a match in sentence: "+sentence+"\n")
                            for candidate in match:
                                # remove spaces
                                candidate = candidate.replace(" ","").strip().upper()
                                if len(candidate)==int(ans_len):
                                    cands.add(candidate)
                                else:
                                    # if matched extra characters, only take first ans_len chars
                                    candidate1 = candidate [:int(ans_len)]
                                    candidate2 = candidate [len(candidate)-int(ans_len):]
                                    if len(candidate1)==int(ans_len):
                                        cands.add(candidate1)
                                    if len(candidate2)==int(ans_len)and candidate2!=candidate1:
                                        cands.add(candidate2)
    except:
        pass
    return cands

## Get answers
#
# @param clue the text of the clue to search for
# @param answer_length length of the expected answer in the puzzle
def get_answers(clue,answer_length,limit=200):
    answers = ScoreDict()
    if re.search("_+",clue):
        if clue.count('"')%2==1:
            clue=clue.replace('"',' ')
        clue = clue.replace("'",r"\'")
        clue = clue.replace("(",r"\(")
        clue = clue.replace(")",r"\)")
        clue = clue.replace("&",r"\&")
        clue = clue.replace("!",r"\!")
        json_obj = subprocess.check_output(SEARCH_CLUES_PATH +' ' + str(limit) + ' ' + clue, shell=True)
        results_dict = eval(json_obj)
        if 'results' in results_dict['wikipedia-search']:
#            sys.stderr.write(clue+'\n')
            for wikiresult in results_dict['wikipedia-search']['results']:
                answers = find_ngram_candidates(clue,wikiresult,answer_length,answers)
    return answers.to_list()

## Process one line of either stdin or reading from a file
#
# @param line the line itself
def process_line(line):
    if line.strip() != "":
        clueid,clue,length = line.split('\t')
        answers = get_answers(clue,length)
        return answers
#        if answers:
#            sys.stderr.write(str(answers)+'\n')
	'''
        for answer in answers:
            word,score = answer
#            sys.stderr.write("\t".join([clueid,word,str(score)])+'\n')
            print "\t".join([clueid,word,str(score)])
	'''

if __name__ == "__main__":
    if len(sys.argv) == 2:
        for line in open(sys.argv[1]).readlines():
            process_line(line)
    elif len(sys.argv) == 1:
        threads = {}
        clue_answers = []
	clues = []        
        for line in sys.stdin:
            clues.append(line)
            threads[line] = myThread(target=process_line,args=(line,))
            threads[line].start()

        for line in clues:
	    clue_answers = threads[line].join()
            clueid,clue,length = line.split('\t')
            if clue_answers != None:
                for answer in clue_answers:
		    word,score = answer
                    print "\t".join([clueid,word,str(score)])




