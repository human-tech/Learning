from sys import argv, exit
import csv

if len(argv) != 3:
    print("python dna.py data.csv sequence.txt")
    exit(1)

database = open(argv[1], "r")
reader = csv.reader(database, delimiter=',')
line = 0
data = {}
for row in reader:
    if line == 0:
        col = len(row) - 1
        STRtype = ()
        for i in range(col):
            STRtype = STRtype + (row[i + 1],)
        line += 1
    else:
        temp = ()
        for j in range(col):
            temp = temp + (int(row[j + 1]),)
        data[temp] = row[0]
        line += 1
database.close()

seq = open(argv[2], "r")
sample = seq.read()
samplelen = len(sample)
seq.close()

index = []
for i in range(col):
    STRlen = len(STRtype[i])
    j = 0
    count = 0
    index.append(0)
    while j < samplelen - STRlen:
        if sample[j:j + STRlen] == STRtype[i]:
            j += STRlen
            count += 1
        else:
            if index[i] < count:
                index[i] = count
            count = 0
            j += 1

index = tuple(index)
if index in data:
    print(data[index])
else:
    print("No Match")