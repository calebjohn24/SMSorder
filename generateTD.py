import json
import math
import random
import pandas
import num2words
num2words.num2words(100)
def nCr(n,r):
    f = math.factorial
    return f(n) / f(r) / f(n-r)


file = open("menu.json","r")
data = json.load(file)
extras = []
items = data['items']
removelex = [["WITHOUT",0], ["NO",0], ["REMOVE",0], ["TAKE OUT",0], ["W/O",0], ["TAKE OFF",0]]
addlex = [["WITH", 1], ["ADD", 1], ["MORE", 1], ["W/",1], ["INCLUDE", 1],["",1]]
TrainData = []
batchSize = 1000
maxQty = 15
Datas = ["qty","name","size","add","remove"]
def genData(TrainItem):
    outfile = open((str(TrainItem) + ".txt"),"w")
    for itx in range(len(data['items'])):
        extras = []
        itemADD = []
        itemREM = []
        name = data['items'][itx]['name']
        if(data['items'][itx]['sizes'][0][1] != -1):
            for ex in range(len(data['items'][itx]['extras'])):
                extras.append([data['items'][itx]['extras'][ex][0],1,data['items'][itx]['extras'][ex][0]])
                for remLex in range(len(removelex)):
                    extras.append([str(removelex[remLex][0])+ " " +data['items'][itx]['extras'][ex][0],0,data['items'][itx]['extras'][ex][0]])
                for adlx in range(len(addlex)):
                    extras.append([str(addlex[adlx][0])+ " " +data['items'][itx]['extras'][ex][0],1,data['items'][itx]['extras'][ex][0]])
            numEx = int(len(addlex) + len(removelex))
            szIndx = random.randint(0,(len(data['items'][itx]['sizes'])-1))
            for testData in range(batchSize):
                WNum = random.randint(0,1)
                WNumSize = random.randint(0,1)
                szIndx = random.randint(0,(len(data['items'][itx]['sizes'])-1))
                tesSTR = ""
                qtyTest = random.randint(1,maxQty)
                qty = str(qtyTest)
                if(WNum == 1):
                    (qty) = num2words.num2words(int(qtyTest))
                itemLen = random.randint(0,(len(data['items'][itx]['extras'])))
                if(qtyTest == 1):
                    tesSTR += ""
                else:
                    tesSTR += str(qty)
                    tesSTR += " "
                if(len(data['items'][itx]['sizes']) != 1):
                    try:
                        if(WNumSize == 1):
                            szNums = []
                            for zzx in range(len(data['items'][itx]['sizes'][szIndx][0])):
                                if(data['items'][itx]['sizes'][szIndx][0][zzx] == "."):
                                    szNums.append(".")
                                try:
                                    int(data['items'][itx]['sizes'][szIndx][0][zzx])
                                    szNums.append([int(data['items'][itx]['sizes'][szIndx][0][zzx]),zzx])
                                except ValueError:
                                    pass
                            endIndx = 0
                            intSTR = ""
                            if(len(szNums) > 0):
                                for mz in range(len(szNums)):
                                    intSTR += str(szNums[mz][0])
                                    if(szNums[mz][1] > endIndx):
                                        endIndx = szNums[mz][1]
                                intSTR = num2words.num2words(intSTR)
                                szAppSTR = intSTR
                                tesSTR += szAppSTR
                                tesSTR += " "
                                tesSTR += data['items'][itx]['sizes'][szIndx][0][endIndx+2::]
                                tesSTR += " "
                            else:
                                tesSTR += (num2words.num2words(data['items'][itx]['sizes'][szIndx][0][0]))
                                #tesSTR += " "
                                for szx in range(1,len(data['items'][itx]['sizes'][szIndx][0])):
                                    tesSTR += data['items'][itx]['sizes'][szIndx][0][szx]
                                tesSTR += " "
                        else:
                            tesSTR += data['items'][itx]['sizes'][szIndx][0]
                            tesSTR += " "
                    except Exception:
                        tesSTR += data['items'][itx]['sizes'][szIndx][0]
                        tesSTR += " "
                tesSTR += name
                tesSTR += " "
                tesSTR = tesSTR.upper()
                if(itemLen > 0):
                    prevState = 2
                    indxUsed = []
                    for hh in range(itemLen):
                        newState = random.randint(0,1)
                        pickExIndx = random.randint(0,(len(data['items'][itx]['extras'])-1))
                        if(len(indxUsed) > 0):
                            for jj in range(len(indxUsed)):
                                while(pickExIndx == indxUsed[jj]):
                                    pickExIndx = random.randint(0, (len(data['items'][itx]['extras']) - 1))
                                    if(pickExIndx != indxUsed[jj]):
                                        break
                        indxUsed.append(pickExIndx)
                        if(newState == prevState):
                            tesSTR += data['items'][itx]['extras'][pickExIndx][0]
                            if (newState == 0):
                                itemADD.append(data['items'][itx]['extras'][pickExIndx][0])
                            elif(newState == 1):
                                itemREM.append(data['items'][itx]['extras'][pickExIndx][0])
                        else:
                            if(newState == 0):
                                pickAddlex = random.randint(0,(len(addlex)-1))
                                tesSTR += addlex[pickAddlex][0]
                                tesSTR += " "
                                tesSTR += data['items'][itx]['extras'][pickExIndx][0]
                                itemADD.append(data['items'][itx]['extras'][pickExIndx][0])
                            elif(newState == 1):
                                pickRemlex = random.randint(0, (len(removelex)-1))
                                tesSTR += removelex[pickRemlex][0]
                                tesSTR += " "
                                tesSTR += data['items'][itx]['extras'][pickExIndx][0]
                                itemREM.append(data['items'][itx]['extras'][pickExIndx][0])
                        tesSTR += " "
                        prevState = newState
                rem = "NONE"
                add = "NONE"
                if(len(itemREM) > 0):
                    rem = ""
                    for rxx in range(len(itemREM)):
                        rem += itemREM[rxx]
                        rem += ","
                    rem = rem[:-1]
                if(len(itemADD) > 0):
                    add = ""
                    for axx in range(len(itemADD)):
                        add += itemADD[axx]
                        add += ","
                    add = add[:-1]
                tesSTR = tesSTR[:-1]
                TrainData.append([tesSTR,[qtyTest, name, data['items'][itx]['sizes'][szIndx][0], add, rem]])
                itemADD = []
                itemREM = []
                tesSTR = ""

    for train in range(len(TrainData)):
        #print(TrainData[train])
        wrteSTR = TrainData[train][0]
        wrteSTR += ","
        fvv = Datas.index(TrainItem)
        wrteSTR += str(TrainData[train][1][fvv])
        wrteSTR += "\n"
        outfile.write(wrteSTR)
        if(len(TrainData) - train == 1):
            wrteSTR = TrainData[train][0]
            wrteSTR += ","
            fvv = Datas.index(TrainItem)
            wrteSTR += str(TrainData[train][1][fvv])
            outfile.write(wrteSTR)


genData("remove")
