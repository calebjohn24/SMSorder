import itertools
array5 = [["item1", 2], ["item2", 4.5], ["item3" , 3], ["item4", 2.5]]
itx = 2
combos = list(itertools.combinations(array5,itx))
arr = []
strX = []
prX = []
final = []
for inx in range(len(combos)-1):
    arr.append(list(combos[inx]))

for zx in range(len(arr)):
    writestr = ""
    writeNum = 0
    for zxx in range(itx):
        writestr += arr[zx][zxx][0]
        writestr += " "
        writeNum += arr[zx][zxx][1]
    final.append([writestr,writeNum])

print(final)