import numpy as np

data = []
with open('sublog.txt', 'rt') as fp:
    for line in fp:
        data.append(line.split(' - ')[1])

#print(data)

table = {}
for item in data:
    vals = item.split(' = ')
    key = vals[0]
    val = float(vals[1])

    if not key in table:
        table[key] = []

    table[key].append(val)

with open('sublog.csv', 'wt') as outF:
    outF.write(','.join(table.keys()) + '\r\n')
    list_res = table.values()

    for i in xrange(len(list_res[0])):
        outp = []
        for j in xrange(len(list_res)):
            outp.append(list_res[j][i])
        outF.write(','.join([str(_) for _ in outp]) + '\r\n')

print(table)