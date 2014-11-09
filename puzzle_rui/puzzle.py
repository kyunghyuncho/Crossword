
# @package puzzle
# load a .puz file into a puzzle object
#
# puz file format documentation found at:
# https://code.google.com/p/puz/wiki/FileFormat
#
# Steve Wilson
# Mar 2014
#
# Puzzle.get_gridnumbers() and 
# .to_json() by Cody Hansen

import argparse
import json
import sys
import random
import re
import string

import csp.csp as csp


## entry is used to represent a sequence of squares that must be filled in with an answer
class Entry:

    ## Constructor
    #
    # @param answer the answer to the clue of the entry
    # @clue the clue for this entry
    # @row which row the entry starts in
    # @col which column the entry starts in
    # @acr True if the entry is an "across" entry, False if "down"
    def __init__(self,answer=None,clue=None,row=None,col=None,acr=False):
        self.clue = clue
        self.answer = answer
        self.row = row
        self.col = col
        self.length = None
        self.across = acr
        ## a list coordinates where the entry exists in the puzzle
        self.coords = []
        ## a dictionary of intersections this entry has with other entries
        self.intersections = {}

        
    ## look in puzzle grid to find out how many blanks are provided for the answer
    # could just use len(answer), but done as a precaution to make sure grid is what we expect
    def update_length(self,rows):
        current = rows[self.row][self.col]
        x,y = self.col,self.row
        l = 0
        while current != '.' and x < len(rows[0]) and y < len(rows):
            self.coords.append((x,y))
            if self.across:
                x+=1
            else:
                y+=1
            if x < len(rows[0]) and y < len(rows):
                current = rows[y][x]
            l+=1
        self.length = l
        # this should fail if we come across a puzzle that allows multiple letters per square
        assert(self.length==len(self.answer))

    ## just a getter function for the length so len() can be used pythonically
    def __len__(self):
        return self.length


## Represents a .puz file

class Puzzle:

    def __init__(self,path):
        self.checksums = {}
        with open(path,'rb') as puz:
            self.path = path

            # header
            # ------
            self.checksums['overall'] = puz.read(2)
            ## should be string "ACROSS&DOWN"
            self.magic = puz.read(12)
            self.checksums['cib'] = puz.read(2)
            self.checksums['masked_low'] = puz.read(4)
            self.checksums['masked_high'] = puz.read(4)
            self.version = puz.read(4)
            junk = puz.read(2)
            ## checksum of solution if scrambled puzzle
            self.checksums['scrambled'] = puz.read(2)
            junk = puz.read(12)
            ## puzzle width
            self.width = int(ord(puz.read(1)))
            ## puzzle height
            self.height = int(ord(puz.read(1)))
            self.num_clues = int(ord(puz.read(2)[0]))
            self.bitmask = puz.read(2)
            ## 0 for unscrambled, often 4 for scrambled
            self.tag = puz.read(2)
            
            # puzzle body
            # ------ ----
            ## rows of the puzzle containing the correct answers
            self.rows = [puz.read(self.width) for i in range(self.height)]
            ## rows of the puzzle containing the current state
            # Initially blank
            self.state = [puz.read(self.width) for i in range(self.height)]

            self.entries = self.find_all_entries()
            for k,v in self.entries.items():
                v.update_length(self.rows)
            
            rest = puz.read()
            self.title,self.author,self.source = rest.split("\0")[:3]

            # clues
            # -----
            raw_clues = rest.split("\0")[3:]
            self.clues = []
            i = 0
            for k in sorted(sorted(self.entries.keys(),key=lambda x:x[-1]),key=lambda x:int(x[:-1])):
                self.entries[k].clue = raw_clues[i]
                i += 1

            # additional info
            # ---------------
            self.is_rebus = False
            if i<len(raw_clues):
                other = '\0'.join(raw_clues[i:])
                if re.search("RTBL",other) and re.search("GRBS",other):
                    self.is_rebus = True

            if self.is_rebus:
                sys.stderr.write("WARNING: Puzzle is a 'rebus' puzzle\nSolver will not attempt to solve\n\n")

            self.all_candidates = {}

    ## Used for printing
    def __str__(self):

        # printing puzzle itself
        s = "\n".join([row for row in self.rows])
        s += '\n\n'
        # printing the clues and answers
        for k in sorted(sorted(self.entries.keys(),key=lambda x:x[-1]),key=lambda x:int(x[:-1])):
            s += '\t'.join([k,self.entries[k].clue,self.entries[k].answer]) + '\n'
        return s

    def get_grid(self):
        s = "\n".join([row for row in self.rows])
        s += '\n\n'
        return s

    def get_initial_state(self):
        s = "\n".join([row for row in self.state])
        s += '\n\n'
        return s

    ## output the gridnumbers for each cell in a crossword puzzle
    #
    # Function by Cody Hansen
    # Apr 2014
    def get_gridnumbers(self):
        gridcounter = 1
        gridnums = []
        for row in range(0, self.height):
            for col in range(0, self.width):
                if self.begins_acr_entry(row,col) or self.begins_dwn_entry(row,col):
                    gridnums.append(gridcounter)
                    gridcounter += 1
                else:
                    gridnums.append(0)
        return gridnums


    ## Gets all clues in component API format
    #
    #  printing the resulting string gives the correct input to a component
    def get_all_clues(self):
        s = ""
        for k in sorted(sorted(self.entries.keys(),key=lambda x:x[-1]),key=lambda x:int(x[:-1])):
            s += '\t'.join([k,self.entries[k].clue,str(len(self.entries[k].answer))]) + '\n'
        return s

    ## Search through the grid to find all of the entries and their respective information
    def find_all_entries(self):
        count = 0
        entries = {}
        for i in range(self.height):
            for j in range(self.width):
                if self.rows[i][j] != '.':
                    added_one = False
                    if self.begins_acr_entry(i,j):
                        count += 1
                        added_one = True
                        across = self.find_across(i,j)
                        if len(across) > 2:
                            # entries[str(count)+'A'] = across
                            entries[str(count)+'A'] = Entry(col=j,row=i,answer=across,acr=True)
                    if self.begins_dwn_entry(i,j):
                        if not added_one:
                            count += 1
                        down = self.find_down(i,j)
                        if len(down) > 2:
                            # entries[str(count)+'D'] = down
                            entries[str(count)+'D'] = Entry(col=j,row=i,answer=down,acr=False)
        return entries

    ## Seach through the grid and identify which entries intersect
    def update_all_intersections(self):
        for clue_id,entry in self.entries.items():
            for coord in entry.coords:
                for other,oentry in self.entries.items():
                    if coord in oentry.coords and clue_id != other:
                        entry.intersections[other] = coord

    ## Given the current solution, update any '-' to real values
    # based on intersections with entry with key k
    def update_solution(self,sol,k):
        for inter,coord in self.entries[k].intersections.items():
	    if inter not in sol.keys():
		continue
            current_ans = sol[inter]
            if '-' not in current_ans:
                continue
            word_index = abs(coord[0]-self.entries[k].col)+abs(coord[1]-self.entries[k].row)
            new_letter = sol[k][word_index]
            if new_letter == '-':
                continue
            inter_index = abs(coord[0]-self.entries[inter].col)+abs(coord[1]-self.entries[inter].row)
            sol[inter] = current_ans[:inter_index] + new_letter + current_ans[1+inter_index:]
#print current_ans,"->",sol[inter],new_letter,inter_index
        return sol

    ## Return true if there is no conflict with the assignment, False otherwise
    #
    # Used for CSP solver
    def check_intersect(self,clue1,val1,clue2,val2):
        if clue2 in self.entries[clue1].intersections:
            intersect_coord = self.entries[clue1].intersections[clue2]
            index1,index2 = None,None
            if self.entries[clue1].across:
                index1 = intersect_coord[0]-self.entries[clue1].col
            else:
                index1 = intersect_coord[1]-self.entries[clue1].row
            if self.entries[clue2].across:
                index2 = intersect_coord[0]-self.entries[clue2].col
            else:
                index2 = intersect_coord[1]-self.entries[clue2].row
            try:
                if val1[index1] == val2[index2]:
                    return True
            except Exception as e:
                print val1+"'s #"+str(index1)+" letter should = "+val2+"'s #"+str(index2)+" letter"
                raise e
            if val1[index1] == "-" or val2[index2] == "-":
                return True
            return False
#            return val1[index1] == val2[index2]
        # no intersection (shouldn't happen because csp knows intersections)
        else:
            return True

    ## Check a solution again the correct grid
    def evaluate_solution(self,prob,sol,postfix=""):
        ms,ts,grid = self.num_matching_squares(sol)
        correct_in_candidate_list = (sum([1 if self.entries[var].answer in vals else 0 
             for var,vals in prob.domains.items()]))
        self.state = grid
        return ({"matching_words"+postfix:self.num_matching_words(sol),
                 "total_words":len(self.entries),
                 "matching_squares"+postfix:ms,
                 "total_squares":ts,
                 "correct_answer_was_candidate":correct_in_candidate_list})
            
    ## Count the number of words that match from a solution when compared again the actual answers
    def num_matching_words(self,sol):
        count = 0
        total = 0
        for k,v in {k:self.entries[k].answer for k in self.entries.keys()}.items():
            total += 1
            if sol[k]==v:
                count +=1
        assert total == len(self.entries)
        return count

    ## Count the number of squares that match from a solution when compared again the actual answers
    # generates solution grid as a side product
    def num_matching_squares(self,sol):
        sol_grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append('.')
            sol_grid.append(row)
        for k,v in sol.items():
            for i in range(len(v)):
                x,y = self.entries[k].coords[i]
                # the first case means an intersecting word has already filled the square
                if sol_grid[y][x]!='.' and sol_grid[y][x]!='-':
                    if v[i]!='-':
#                        for row in sol_grid:
#                            print row
#                        print v,sol_grid[y][x],i,x,y
                        assert sol_grid[y][x]==v[i]
                else:
                    sol_grid[y][x]=v[i]
        count = 0
        total = 0
        for x in range(self.width):
            for y in range(self.height):
                if self.rows[y][x] == '.':
                    assert sol_grid[y][x] == '.'
                elif self.rows[y][x] == sol_grid[y][x]:
                    count += 1
                    total += 1
                else:
                    total += 1
                    assert sol_grid[y][x] != '.'
        return count,total,sol_grid

    ## conflict resolution- iteratively remove conflicted words
    #
    #  start with the lowest scoring words (according to component scoring)
    def resolve_conflicts(self,solution,conflicts,problem):
        while conflicts:
            conf_list = []
            for conf in conflicts:
                conf_list.append((conf, problem.domains[conf].index(solution[conf])))
            conf_idx = sorted(conf_list,key=lambda x:x[1],reverse=True)[0]
            conf,idx = conf_idx
            length = len(solution[conf])
            solution[conf] = '-'*length
            conflicts = problem.conflicted_vars(solution)
#        for conf in conflicts:
#            length = len(solution[conf])
#            solution[conf] = '-'*length
        return solution

    ## True if coordinates designate the beginning of an "across" entry
    def begins_acr_entry(self,i,j):
        if self.rows[i][j]== ".":
            return False
        if  j==0:
            return True
        if self.rows[i][j-1] == '.':
            return True

    ## True if coordinates designate the beginning of an "down" entry
    def begins_dwn_entry(self,i,j):
        if self.rows[i][j]== ".":
            return False
        if i==0:
            return True
        if self.rows[i-1][j] == '.':
            return True

    ## Find all places in grid where "across" entries reside
    def find_across(self,i,j):
        idx = self.rows[i].find('.',j)
        if idx != -1:
            return self.rows[i][j:idx]
        else:
            return self.rows[i][j:]

    ## Find all places in grid where "down" entries reside
    def find_down(self,i,j):
        s = ""
        c = 0
        nxt = self.rows[i+c][j]
        while nxt != '.':
            s+=nxt
            c+=1
            if len(self.rows)==i+c:
                break
            nxt = self.rows[i+c][j]
        return s

    def get_side_by_side_comparison(self):
        outstr =  "Solution Generated\tActual Solution\n"
        for i in range(len(self.state)):
            outstr+= "".join(self.state[i])+'\t'+"".join(self.rows[i])+'\n'
        outstr += '\n'
        return outstr
