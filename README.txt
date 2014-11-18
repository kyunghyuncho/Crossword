Linxi Fan

Commandline:

python solve_a_puzzle.py <XXX.puz> <component_list> <n> <don't_fill_blank>

The 3rd arg is the "n" parameter used in the search. 
If you provide anything for the optional 4th arg, the solver will NOT
fill blanks. 

The performance on Monday puzzles is extremely good, reaching 90+%
per-square accuracy on average and 85+% in the worst case. 
There can be a big gap when n goes from 0 to 1. Otherwise, n = 1 and n = 2
don't seem to make much difference. 

The lowest n such that all Monday puzzles can be solved with greater than
75% accuracy is simply n = 0.

n = 2 is the highest average limit under which the puzzles can be solved
within 20 minutes. Occasionally, n = 3 also works. 

n represents the "discrepancy limit", namely how far the current search path
deviates from the greedy "best" path. The usage of n forms a barrier 
against a full search of the tree, which can be explosively large.
(reference: Dr. Fill paper)


- If some squares are still not determined even after filling blanks, I will
  randomly assign letters to those squares as long as they are consistent
  with the "down" and "across" alignments. The letters are assigned with
  probabilities proportional to their frequencies in "answers_cwg_otsys.txt". 
  Performance improvement depends on luck. ;)

- I used an implementation of the quickselect algorithm to choose the highest
  and second-highest word probabilities not in P. 

- I implemented my own cache system to avoid recomputing the components.


Here's a summary of results for each of the four Monday puzzles before
filling blanks (accuracy is per-square):

--- May0514
n = 0: time = 0.57;  96.8%
n = 1: time = 12.1;  96.8%
n = 2: time = 206.6;  96.8%
n = 3: time = 2241.3;  96.8%

--- May1214
n = 0: time = 0.62;  91.4%
n = 1: time = 12.1;  97.3%
n = 2: time = 179.6;  97.3%
n = 3: time = 2004.1;  97.3%

--- May1914
n = 0: time = 0.41;  78.6%
n = 1: time = 7.0;  87.1%
n = 2: time = 100.32;  93.0%
n = 3: time = 1310.3;  93.0%

--- May2614
n = 0: time = 0.51;  100.0%
n = 1: time = 9.4;  100.0%
n = 2: time = 147.8;  100.0%
n = 3: time = 1977.3;  100.0%



My fill blank algorithm first processes the "answers_cwg_otsys.txt" and
builds a hash dictionary. 
Then it greedily matches the unfilled squares while it ensures that "down"
and "across" alignment contraints are fully satisfied. 

Because the first round almost gets everything correct, the improvement by
filling blanks can be limited. 

For example, May0514 improves from 182/189 to 185/189
May1214 improves from 182/187 to 185/187
May1914 improves from 174/187 to 176/187

The running time is almost not affected. 


===== Component 1 (designated) =====
Hypernym (No. 16)
"components/lf2422_hypernym_component.py"

Clues in the format of "XXX and XXX", "XXX or XXX", "XXX, for example" will
trigger this component. 
The class uses NLTK to compute hypernym closure, and then find common
ancestors between the two clues. 

There are very few clues in test_month that triggers hypernym. 

Examples can be found in components/hypernym_example (including some clues
from the database 'clues.txt')

> python lf2422_hypernym_component.py hypernym_example

===== Component 1 (original) =====
Airport ID
"components/lf2422_airport_component.py"

Clues in the format of "XX(city) airport ID" will trigger this component. 
The class uses a copy-and-pasted database "components/airports.txt" to
generate the components. The file is preprocessed into a dictionary. Airport
IDs must be 3-letter abbreviations.

There are very few clues in test_month that triggers airport ID, but quite a
few examples can be found in the larger 'clues.txt' database. 

Examples can be found in components/airport_example 

> python lf2422_airport_component.py airport_example

Both components above do not yield a big improvement because of their
rarity. In fact, the first component triggers only 4 instances in test_month
and the second doesn't appear at all. The improvement is only around 2% in
matched squares. 
