import nltk
from fuzzywuzzy import fuzz
from words2num import w2n
from spellchecker import SpellChecker
import num2words


from firebase import firebase
import json
database = firebase.FirebaseApplication("https://cedarfb2.firebaseio.com/")
uid = "JYzVI5fR5KW399swMP9zgEMNTxu2"
data = (database.get("restaurants/" + uid,"/menu/items/"))

userOrder = "8oz iced coffee with cream"

foodItems = (data)

couponflag = 0
spell = SpellChecker()
userOrder = userOrder.lower()
userOrder = userOrder.replace('oz.', 'oz')
userOrder = userOrder.replace('pc.', 'pc')
userOrder = userOrder.replace('pce.', 'pce')
userOrder = userOrder.replace('pcs.', 'pcs')
userOrder = userOrder.replace('lb.', 'lb')
userOrder = userOrder.replace('lbs.', 'lbs')
userOrder = userOrder.replace('g.', 'g')
userOrder = userOrder.replace('mg.', 'mg')
userOrder = userOrder.replace('kg.', 'kg')
userOrder = userOrder.replace("'", "")
userOrder = userOrder.replace(" or", "")
userOrder = userOrder.replace(" and", "")
userOrder = userOrder.replace(",", "")
userOrder = userOrder.replace(".", "")
userOrder = userOrder.replace(" of", "")
userOrder = userOrder.replace("-", "")

measurements = ["oz",'pc','pce','pcs','lbs','lb','ounce','ozs','ounces','pound','pounds'
                ,'grams','g','gram','gs',"milligram",'mg','milligrams','mgs','kilogram','kg'
                ,'kilograms','kgs', 'piece','pice','piecie']

removelex = ["without", "no", "remove", "take out", "w/o", "take off","out"]
addlex = ["with", "add", "more", "w/", "include"]
fractions = [['half',0.5],['fourth',0.25],['third',0.333333],['fifth',0.2],['quarter',0.25],['eighth',0.125],['sixteenth',0.00625]]
for frac in range(2,65):
    fractions.append([("1/"+str(frac)),(1/frac)])

itemIndxs = []
itemSPCK = []
writeStr = ""
if (userOrder[-1] == ";"):
    userOrder = userOrder[:-1]

items = [x.strip() for x in userOrder.split(';')]
if (len(items) < 1):
    items.append(userOrder)

subtotal = 0
itemsOrdered = []
for item in range(len(items)):
    price = 0
    sizeArr = []
    ordStr = nltk.tokenize.word_tokenize(items[item])
    tokens = []
    tokenizedToken = []
    numIndxs = []
    addwordIndxs = []
    remwordIndxs = []
    extras = []
    notes = ""
    newStr = ""
    couponFlag = 0
    for tk in range(len(ordStr)):
        token = (ordStr[tk])
        tokens.append(ordStr[tk])

    frrIndx = -1
    tokenFrIndx = -1
    for frr in range(len(tokens)):
        for frc in range(len(fractions)):
            if (fractions[frc][0] == tokens[frr]):
                frrIndx = frr
                tokenFrIndx = frc
    if (frrIndx != -1):
        tokens.insert(frrIndx, str(fractions[tokenFrIndx][1]))
        tokens.pop((frrIndx+1))

    for bb in range(len(tokens)):
        try:
            print(tokens[bb])
            print(w2n(tokens[bb]))
            tokens.insert(bb,str(w2n(tokens[bb])))
            tokens.pop(bb+1)
        except:
            pass

    for mm in range(len(tokens)):
        for ltrs in range(len(tokens[mm])):
            tokenizedToken.append([str(tokens[mm][ltrs]), mm])


    for ttk in range(len(tokenizedToken)):
        try:
            int(tokenizedToken[ttk][0])
            numIndxs.append(ttk)
            tokenizedToken.insert((ttk+1),[" ", 1000])
        except ValueError:
            pass

    currentNum = 0
    for tk0 in range(len(tokenizedToken)):
        if(currentNum == tokenizedToken[tk0][1]):
            newStr += str(tokenizedToken[tk0][0])
            currentNum = tokenizedToken[tk0][1]
        elif (tokenizedToken[tk0][1] == 1000):
            if(tokenizedToken[tk0 + 1][1] == currentNum):
                try:
                    int(tokenizedToken[tk0 + 1][0])
                    pass
                except ValueError:
                    if (tokenizedToken[tk0 + 1][0] == "."):
                        pass
                    else:
                        newStr += " "

        else:
            newStr += " "
            newStr += str(tokenizedToken[tk0][0])
            currentNum = tokenizedToken[tk0][1]
    newTokens = nltk.tokenize.word_tokenize(newStr)
    cpnIndx = -1
    couponFlag = 0
    if(len(newTokens)==1):
        for cpn in range(len(data)):
            if (data[cpn] != None):
                #print(data[cpn]['sizes'][0][1])
                if(data[cpn]['sizes'][0][1] == -1):
                    if(newTokens[0] == data[cpn]['name'].lower()):
                        print("coupon found")
                        couponFlag = 100
                        discAmt = data[cpn]["extras"][0][1]
                        numUsed = 1
                        for hh in range(len(itemsOrdered)):
                            scoreDisc = (fuzz.token_sort_ratio(itemsOrdered[hh][0],data[cpn]['extras'][0][0].lower()))
                            if(scoreDisc > 95):
                                limit = data[cpn]['extras'][1][1]
                                if (type(discAmt) == str):
                                    discAmt = discAmt[:-1]
                                    discAmt = float(discAmt)
                                    discAmt = itemsOrdered[hh][1] * discAmt
                                    subtotal -= discAmt
                                elif (type(discAmt) == float or type(discAmt) == int):
                                    discTotal = (discAmt)
                                    subtotal -= discAmt
                                if(itemsOrdered[hh][2] > limit):
                                    while(limit > numUsed):
                                        if (type(discAmt) == str):
                                            discAmt = discAmt[:-1]
                                            discAmt = float(discAmt)
                                            discAmt = itemsOrdered[hh][1] * discAmt
                                            subtotal -= discAmt
                                        elif (type(discAmt) == float or type(discAmt) == int):
                                            discTotal = (discAmt)
                                            subtotal -= discAmt
                                        numUsed += 1

                    writeStr += items[item] + (' -${0}'.format(format(discAmt*numUsed, ',.2f')))
                    writeStr += " x " + str(numUsed)
                    writeStr += "\n"

    if(couponFlag == 0):
        for tk1 in range(len(newTokens)):
            for measure in range(len(measurements)):
                tknz = str(newTokens[tk1]) == (measurements[measure])
                if(str(newTokens[tk1]) == (measurements[measure])):
                    sizeArr.append(newTokens[tk1-1])
                    sizeArr.append(newTokens[tk1])

        sizeFlag = 0
        if(len(sizeArr) > 0):
            for szza in range(len(sizeArr)):
                newTokens.remove(sizeArr[szza])
            sizeFlag = 1
        tokenPos = nltk.pos_tag(newTokens)
        #print(tokenPos)
        quantIndx = -1
        quant = 1
        for posInt in range(len(tokenPos)):
            if(tokenPos[posInt][1] == "CD"):
                try:
                    int(newTokens[posInt])
                    quant = int(newTokens[posInt])
                    quantIndx = posInt
                except ValueError:
                    int(w2n(newTokens[posInt]))
                    quant = int(w2n(newTokens[posInt]))
                    quantIndx = posInt

        if(-1 != quantIndx):
            newTokens.pop(quantIndx)

        spellChkTokens = []
        for spll in range(len(newTokens)):
            spellChkTokens.append(spell.correction(newTokens[spll]))
        testString = ""
        if(len(sizeArr) == 0):
            for szz in range(len(spellChkTokens)):
                testString = spellChkTokens[szz]
                testString += " "
            testString = spellChkTokens[0:2]
            testScore = 0
            nameIndx = 0
            sizeIndx = 0
            for dataNM in range(len(data)):
                if (data[dataNM] != None):
                    if(data[dataNM]['sizes'][0][0] != "u"):
                        for dataSZ in range(len(data[dataNM]['sizes'])):
                            compStr = data[dataNM]['name'] + " " + data[dataNM]['sizes'][dataSZ][0]
                            compStr = str(compStr).lower()
                            newScore = fuzz.token_sort_ratio(compStr,testString)
                            if(newScore > testScore):
                                testScore = newScore
                                nameIndx = dataNM
                                sizeIndx = dataSZ
                            elif(newScore == testScore):
                                newScore = fuzz.ratio(compStr, testString)
                                if (newScore > testScore):
                                    testScore = newScore
                                    nameIndx = dataNM
                                    sizeIndx = sizeIndx
                else:
                    if (data[dataNM] != None):
                        if (data[dataNM]['sizes'][0][0] != "u"):
                            compStr = data[dataNM]['name']
                            compStr = str(compStr).lower()
                            newScore = fuzz.token_sort_ratio(compStr, testString)
                            if (newScore > testScore):
                                testScore = newScore
                                nameIndx = dataNM
                                sizeIndx = 0
                            elif (newScore == testScore):
                                newScore = fuzz.ratio(compStr, testString)
                                if (newScore > testScore):
                                    testScore = newScore
                                    nameIndx = dataNM
                                    sizeIndx = sizeIndx

            name = str(data[nameIndx]['name']).lower()
            size = str(data[nameIndx]['sizes'][sizeIndx][0]).lower()
        else:
            for szz in range(len(sizeArr)):
                testString += sizeArr[szz]
                testString += " "
            for nmm in range(len(spellChkTokens)):
                testString += spellChkTokens[nmm]
                testString += " "
            testScore = 0
            nameIndx = 0
            sizeIndx = 0
            for dataNM in range(len(data)):
                if (data[dataNM] != None):
                    if(data[dataNM]['sizes'][0][0] != "u"):
                        for dataSZ in range(len(data[dataNM]['sizes'])):
                            compStr = data[dataNM]['name'] + " " + data[dataNM]['sizes'][dataSZ][0]
                            compStr = str(compStr).lower()
                            newScore = fuzz.token_sort_ratio(compStr,testString)
                            #print(newScore, testScore, compStr, testString)
                            if(newScore > testScore):
                                testScore = newScore
                                nameIndx = dataNM
                                sizeIndx = dataSZ
                            elif(newScore == testScore):
                                newScore = fuzz.ratio(compStr, testString)
                                if (newScore > testScore):
                                    testScore = newScore
                                    nameIndx = dataNM
                                    sizeIndx = dataSZ
                else:
                    if (data[dataNM] != None):
                        compStr = data[dataNM]['name']
                        compStr = str(compStr).lower()
                        newScore = fuzz.token_sort_ratio(compStr, testString)
                        #print(newScore, testScore, compStr, testString)
                        if (newScore > testScore):
                            testScore = newScore
                            nameIndx = dataNM
                            sizeIndx = 0
                        elif (newScore == testScore):
                            newScore = fuzz.ratio(compStr, testString)
                            if (newScore > testScore):
                                testScore = newScore
                                nameIndx = dataNM
                                sizeIndx = 0
        price += data[nameIndx]['sizes'][sizeIndx][1]
        name = str(data[nameIndx]['name']).lower()
        size = str(data[nameIndx]['sizes'][sizeIndx][0]).lower()
        print(newScore)
        testScore = 0
        remNameIndxs = []
        if(sizeFlag == 0):
            lenName = len(name.split()) + len(size.split())
        else:
            lenName = len(name.split())

        spellChkTokens = spellChkTokens[lenName:]
        if(len(spellChkTokens) > 0):
            for spp in range(len(spellChkTokens)):
                for aLex in range(len(addlex)):
                    newScore = fuzz.ratio(addlex[aLex], spellChkTokens[spp])
                    if (newScore > 85):
                        addScore = newScore
                        spIndx = spp
                        aLexIndx = aLex
                        addwordIndxs.append(spp)

            for sppR in range(len(spellChkTokens)):
                for rLex in range(len(removelex)):
                    newScore = fuzz.ratio(removelex[rLex], spellChkTokens[sppR])
                    #print(removelex[rLex], spellChkTokens[sppR], newScore)
                    if (newScore > 85):
                        addScore = newScore
                        spIndx = sppR
                        aLexIndx = rLex
                        remNameIndxs.append(sppR)

            if(len(spellChkTokens) > 0):
                if(len(remNameIndxs) != 0 and len(addwordIndxs) != 0):
                    state = 0
                    currentWord = 0
                    for remEx in range(len(spellChkTokens)):
                        for hh in range(len(remNameIndxs)):
                            if(remNameIndxs[hh] == remEx):
                                state = 1
                                currentWord = 1
                                break
                            else:
                                currentWord = 0
                        for yy in range(len(addwordIndxs)):
                            if(addwordIndxs[yy] == remEx):
                                state = 0
                                currentWord = 1
                                break
                            else:
                                currentWord = 0
                        if(currentWord == 0):
                            if(state == 0):
                                extras.append(spellChkTokens[remEx])
                            elif(state == 1):
                                notes += " "
                                notes += spellChkTokens[remEx]
                elif(len(remNameIndxs) != 0 and len(addwordIndxs) == 0):
                    state = 0
                    currentWord = 0
                    for remEx in range(len(spellChkTokens)):
                        for yy in range(len(remNameIndxs)):
                            if (remNameIndxs[yy] == remEx):
                                state = 1
                                currentWord = 1
                                break
                            else:
                                currentWord = 0
                        if (currentWord == 0):
                            if (state == 0):
                                extras.append(spellChkTokens[remEx])
                            elif (state == 1):
                                notes += "no "
                                notes += spellChkTokens[remEx]
                elif (len(remNameIndxs) == 0 and len(addwordIndxs) != 0):
                    state = 0
                    currentWord = 0
                    for remEx in range(len(spellChkTokens)):
                        # print(spellChkTokens[remEx])
                        for yy in range(len(addwordIndxs)):
                            if (addwordIndxs[yy] == remEx):
                                currentWord = 1
                                break
                            else:
                                currentWord = 0
                        if (currentWord == 0):
                            extras.append(spellChkTokens[remEx])
                elif(len(remNameIndxs) == 0 and len(addwordIndxs) == 0):
                    for remEx in range(len(spellChkTokens)):
                        extras.append(spellChkTokens[remEx])
                        # print(spellChkTokens[remEx])

        if(notes != ""):
            if (size != 'u'):
                writeStr += size
                writeStr += " "
            writeStr += name
            writeStr += ' '
            writeStr += notes
            writeStr += " "
        else:
            if(size != 'u'):
                writeStr += size
                writeStr += " "
            writeStr += name
        appStr = ""
        if (size != 'u'):
            appStr += size
            appStr += " "
        appStr += name
        itemsOrdered.append([appStr,price,quant])
        if(len(extras) > 0):
            writeStr += ""
            extraIndxs = []
            for e in range(len(extras)):
                exScore = 0
                exIndx = 0
                for ee in range(len(data[nameIndx]['extras'])):
                    compStr = data[nameIndx]['extras'][ee][0]
                    compStr = str(compStr.lower())
                    newScore = fuzz.token_sort_ratio(compStr, extras[e])
                    if (newScore > exScore):
                        exScore = newScore
                        extraIndx = ee
                    elif (newScore == exScore):
                        newScore = fuzz.ratio(compStr, testString)
                        if (newScore > exScore):
                            exScore = newScore
                            extraIndx = ee
                extraIndxs.append([e,extraIndx])
            newExStr = ''
            remIndxs = []
            for rr in range(len(extraIndxs)):
                exLen = len(str(data[nameIndx]['extras'][extraIndxs[rr][1]][0]).split())
                print(str(data[nameIndx]['extras'][extraIndxs[rr][1]][0]),exLen)
                if(exLen > 1):
                    newExStr += extras[extraIndxs[rr][0]]
                    remIndxs.append(extras[extraIndxs[rr][0]])

            if(len(remIndxs) > 1):
                for rr in range(len(remIndxs)):
                    extras.remove(remIndxs[rr])
                extras.append(newExStr)
                extraIndxs = []
                for e in range(len(extras)):
                    exScore = 0
                    exIndx = 0
                    for ee in range(len(data[nameIndx]['extras'])):
                        compStr = data[nameIndx]['extras'][ee][0]
                        compStr = str(compStr.lower())
                        newScore = fuzz.token_sort_ratio(compStr, extras[e])
                        if (newScore > exScore):
                            exScore = newScore
                            extraIndx = ee
                        elif (newScore == exScore):
                            newScore = fuzz.ratio(compStr, testString)
                            if (newScore > exScore):
                                exScore = newScore
                                extraIndx = ee
                    extraIndxs.append([e,extraIndx])
            #print(extraIndxs)
            for rrn in range(len(extraIndxs)):
                exV = (extraIndxs[rrn][1])
                writeStr += " add "
                writeStr += data[nameIndx]['extras'][exV][0].lower()
                price += data[nameIndx]['extras'][exV][1]
                print("inc3")


        writeStr += " x "
        writeStr += str(quant)
        price = price*quant
        subtotal += price
        writeStr += " " + '${:0,.2f}'.format(price)
        writeStr += "\n"
        extras = []
        notes  = ''

writeStr += "process fee $0.20 \n"
subtotal += 0.2
writeStr += "subtotal " + '${:0,.2f}'.format(subtotal)
writeStr += "\n"
tax = subtotal*0.1
writeStr += "tax " + '${:0,.2f}'.format(tax)
writeStr += "\n"
total = subtotal*1.1
writeStr += "total " + '${:0,.2f}'.format(total)
writeStr += "\n"
writeStr += 'if everything looks good enter "ok" otherwise enter "help"'
order = writeStr
print(order)