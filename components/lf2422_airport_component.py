#!/usr/local/bin/python
"""
Linxi Fan
lf2422

Airport ID, like "JFK", "PVG"
"""

import sys
import re

## Preprocess the airport database
#
airportDb = {}

def process_airport_db(dbfile):
    global airportDb
    matcher = re.compile(r"(.+) \((.+)\)")

    for entry in open(dbfile):
        m = matcher.search(entry.strip())
        if m is None:
            continue
        airid = m.group(2)
        places = m.group(1).split(',')
        for place in places:
            place = place.strip().lower()
            if place in airportDb:
                airportDb[place].append(airid)
            else:
                airportDb[place] = [airid]

# @param clue the text of the clue to search for
# @param answer_length length of the expected answer in the puzzle
# 'airport id' questions
def get_airport_id(clue,answer_length):
    # airport ID can only be 3 letters
    if answer_length != 3 or clue not in airportDb:
        return None
    
    answer_dict = {}
    for answer in airportDb[clue]:
        answer_dict[answer] = 3
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
        
        # "XXX(city) airport ID" clue
        matcher = re.compile(r"([\w\s]*\w)\s+airport id")
        m = matcher.search(clue)
        
        length = int(length)
        answers = None
        if m is not None:
            answers = get_airport_id(m.group(1), length)
            
        if answers is not None:
            for word in answers:
                print "\t".join([clueid,word,str(answers[word])])


if __name__ == "__main__":
    # Process the airport ID database first
    process_airport_db('airports.txt')
    
    if len(sys.argv) == 2:
        for line in open(sys.argv[1]).readlines():
            process_line(line)
    elif len(sys.argv) == 1:
        for line in sys.stdin:
            process_line(line)
