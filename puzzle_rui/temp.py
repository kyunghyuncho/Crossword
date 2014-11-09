f = open('temp.sh', 'w')
name = "./print_puzzle.py ../test_month/May{:02d}14.puz >> clues.txt"
for i in range(2, 32):
    if i == 10:
        continue
    print >> f, name.format(i)
