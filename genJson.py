import json
import math
import itertools

def nCr(n,r):
    f = math.factorial
    return f(n) / f(r) / f(n-r)

data = {}
data['items'] = []
while True:
    sizes = []
    extras = []
    name = input("enter name enter DONE if finished>")
    name = name.upper()
    if(name == "DONE"):
        print(data)
        with open('menu.json', 'w') as outfile:
            json.dump(data, outfile)
        break
    noSizes = int(input("enter number of sizes >"))
    writeData = []
    for sz in range(noSizes):
       nameSize = input("enter size name if only one size enter N >")
       nameSize = nameSize.upper()
       if(nameSize == "N"):
           nameSize = ""
       priceSize = float(input("enter size price>"))
       sizes.append([nameSize,priceSize])

    noExtras = int(input("enter number of customizations if none enter N  >"))
    for ex in range(noExtras):
        nameExtra = input("enter customization name, enter 2 word pairaing with a hyphen ex. 'hot-sauce' >")
        nameExtra = nameExtra.upper()
        if (nameExtra == "N"):
            nameExtra = ""
        priceExtra = float(input("enter customization price >"))
        extras.append([nameExtra,priceExtra])

    itx = 0
    for szx in range(len(sizes)):
        while itx <= (len(extras)):
            combos = list(itertools.combinations(extras, itx))
            arr = []
            for inx in range(len(combos)):
                arr.append(list(combos[inx]))
            for zx in range(len(arr)):
                writestr = sizes[szx][0] + " " + name + " "
                writeNum = sizes[szx][1]
                for zxx in range(itx):
                    writestr += arr[zx][zxx][0]
                    writestr += " "
                    writeNum += arr[zx][zxx][1]
                    writestr.rstrip()
                    writestr.lstrip()
                data['items'].append({
                    'name': str(writestr),
                    'price':float(writeNum)
                })
            itx += 1
        itx = 0



