#! /usr/bin/python

# give capital of US state
# e.g. 
# capital of Nebraska --> LINCOLN
# capital of New York --> ALBANY

# 
# Rui Zhang
# May 2015

import re
import sys

def build_state_capital_dict():
    capital_of = dict()
    capital_of["Alabama"] = "Montgomery"   
    capital_of["Alaska"] = "Juneau"   
    capital_of["Arizona"] = "Phoenix"
    capital_of["Arkansas"] = "Little Rock"
    capital_of["California"] = "Sacramento"
    capital_of["Colorado"] = "Denver"
    capital_of["Connecticut"] = "Hartford"
    capital_of["Delaware"] = "Dover"
    capital_of["Florida"] = "Tallahassee"
    capital_of["Georgia"] = "Atlanta"
    capital_of["Hawaii"] = "Honolulu"
    capital_of["Idaho"] = "Boise"
    capital_of["Illinois"] = "Springfield"
    capital_of["Indiana"] = "Indianapolis"
    capital_of["Iowa"] = "Des Moines"
    capital_of["Kansas"] = "Topeka"
    capital_of["Kentucky"] = "Frankfort"
    capital_of["Louisiana"] = "Baton Rouge"
    capital_of["Maine"] = "Augusta"
    capital_of["Maryland"] = "Annapolis"
    capital_of["Massachusetts"] = "Boston"
    capital_of["Michigan"] = "Lansing"
    capital_of["Minnesota"] = "Saint Paul"
    capital_of["Mississippi"] = "Jackson"
    capital_of["Missouri"] = "Jefferson City"
    capital_of["Montana"] = "Helena"
    capital_of["Nebraska"] = "Lincoln"
    capital_of["Nevada"] = "Carson City"
    capital_of["New Hampshire"] = "Concord"
    capital_of["New Jersey"] = "Trenton"
    capital_of["New Mexico"] = "Santa Fe"
    capital_of["New York"] = "Albany"
    capital_of["North Carolina"] = "Raleigh"
    capital_of["North Dakota"] = "Bismarck"
    capital_of["Ohio"] = "Columbus"
    capital_of["Oklahoma"] = "Oklahoma City"
    capital_of["Oregon"] = "Salem"
    capital_of["Pennsylvania"] = "Harrisburg"
    capital_of["Rhode Island"] = "Providence"
    capital_of["South Carolina"] = "Columbia"
    capital_of["South Dakota"] = "Pierre"
    capital_of["Tennessee"] = "Nashville"
    capital_of["Texas"] = "Austin"
    capital_of["Utah"] = "Salt Lake City"
    capital_of["Vermont"] = "Montpelier"
    capital_of["Virginia"] = "Richmond"
    capital_of["Washington"] = "Olympia"
    capital_of["West Virginia"] = "Charleston"
    capital_of["Wisconsin"] = "Madison"
    capital_of["Wyoming"] = "Cheyenne"
  
    return capital_of 

def get_answers(state, length, capital_of):
    if capital_of.has_key(state):
	return capital_of[state]
    else:
	return ""


def process_line(line,capital_of):
    if line != "":
        clueid,clue,length = '','',''
	try:
	    clueid,clue,length = line.split('\t')
	except Exception as e:
	    print line
	
	output = []

	clue_words = re.split(r"\W+",clue)
	
	
	# if match, then return the result
	if (clue_words[0].lower() == "capital" and clue_words[1].lower() == "of"):
            state = ' '.join(clue_words[2:])
	    answer = get_answers(state,length,capital_of)
	    if answer != "":
	        output.append(answer)
	    
        #print output
	for word in output:
	    print "\t".join([clueid,word,str(1)])




if __name__ == "__main__":
    capital_of = build_state_capital_dict()
    if len(sys.argv) == 2:
        for line in open(sys.argv[1]).readlines():
            process_line(line,capital_of)
    elif len(sys.argv) == 1:
	for line in sys.stdin:
	    process_line(line,capital_of)
