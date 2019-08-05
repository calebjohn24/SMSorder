import json
import math
import itertools

def nCr(n,r):
    f = math.factorial
    return f(n) / f(r) / f(n-r)


file = open("menu.json","r")
data = json.load(file)

items = data['items']
removelex = ["WITHOUT", "NO", "REMOVE", "TAKE OUT", "W/O", "TAKE OFF"]
addlex = [["WITH", 1], ["ADD", 1], ["MORE", 1.25], ["W/",1], ["INCLUDE", 1], ["EXTRA", 1], ["LIGHT", 0.75]]
for itx in range(len(data['items'])):
    item = []
    extras = []
    name = data['items'][itx]['name']
    if(data['items'][itx]['sizes'][0][1] != -1):
        for ex in range(len(data['items'][itx]['extras'])):
            extras.append(data['items'][itx]['extras'][ex][0])
            for remLex in range(len(removelex)):
                extras.append(str(removelex[remLex])+ " " +data['items'][itx]['extras'][ex][0])
            for adlx in range(len(addlex)):
                extras.append(str(addlex[adlx][0])+ " " +data['items'][itx]['extras'][ex][0])
        numEx = int((len(extras))/4)
        print(extras)
        '''
        for sz in range(len(data['items'][itx]['sizes'])):
            price = data['items'][itx]['sizes'][sz][1]
            writeStr = str(data['items'][itx]['sizes'][sz][0]) + " "
            for nv in range((math.factorial(len(extras)))):
                for exn in range(numEx):
        '''







