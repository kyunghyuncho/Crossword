
import re

def generate_alternatives(word_dict,dictionary = "/data0/projects/cross/dictionary.com/all_words.txt"):
    results = {}
    regexes = {}
    for wid,word in word_dict.items():
        regexes[wid] = re.compile("^"+word.replace("-","[A-Z]")+"$",re.I)
    for line in open(dictionary).readlines():
        for wid,regex in regexes.items():
            if re.match(regex,line):
                if wid not in results:
                    results[wid] = []
                results[wid].append(line.upper().strip())
    return results

d = {'1A':"HELLO",'2A':"-ORLD",'2D':"D-G",'3A':"F--D",'4A':"ELEMEN-AR-"}
print generate_alternatives(d)
