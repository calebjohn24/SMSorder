import json
import nltk
from fuzzywuzzy import fuzz
from words2num import w2n

with open('menu.json') as data_file:
    data = json.load(data_file)

foodItems = (data['items'])
userOrder = "12 oz. Bees knees with extra honey"
removelex = ["without", "no", "remove", "take out", "w/o", "take off"]
addlex = ["with", "add", "more", "w/", "include"]
itemIndxs = []
userOrder = userOrder.lower()
userOrder = userOrder.replace('oz.', 'oz')
userOrder = userOrder.replace("'", "")
if (userOrder[-1] == "."):
    userOrder = userOrder[:-1]

items = [x.strip() for x in userOrder.split('.')]
if (len(items) < 1):
    items.append(userOrder)

order = ""
subtotal = 0
orderFin = "You ordered "
for item in range(len(items)):
    invalidFlag = 0
    price = 0
    discountFlag = 0
    quantity = 1
    size = "u"
    itemStr = (items[item])
    tokens = nltk.word_tokenize(itemStr)
    pos = nltk.pos_tag(tokens)
    for tknQty in range(len(tokens)):
        part = pos[tknQty][1]
        word = pos[tknQty][0]
        if (part == "CD"):
            try:
                nextword = pos[tknQty+1][0]
                if(nextword == "oz" or nextword == "ounce" or
                    nextword == "ounces" or nextword == "lb" or nextword == "pound"
                    or nextword == "g" or nextword == "gram" or nextword == "mg" or nextword == "milligram"
                or nextword == "kg" or nextword == "killogram"):
                    quantity = int(1)
                    pos.pop(tknQty+1)
                else:
                    quantity = int(word)
                    pos.pop(tknQty)
                break
            except ValueError:
                wordConv = w2n(word)
                quantity = int(wordConv)
                nextword = pos[tknQty + 1][0]
                if (nextword == "oz" or nextword == "ounce" or
                        nextword == "ounces" or nextword == "lb" or nextword == "pound"
                        or nextword == "g" or nextword == "gram" or nextword == "mg" or nextword == "milligram"
                        or nextword == "kg" or nextword == "killogram"):
                    quantity = int(1)
                    pos.pop(tknQty + 1)
                else:
                    quantity = int(word)
                    pos.pop(tknQty)
                break
    sizeFlag = 0
    sizeIndx = 0
    while sizeFlag != 1:
        wordX = pos[sizeIndx][0]
        posX = pos[sizeIndx][1]
        if (quantity > 1):
            if (pos[sizeIndx][1] == "CD" or pos[sizeIndx][1] == "NN" or pos[sizeIndx][1] == "JJ"):
                size = pos[sizeIndx][0]
                pos.pop(sizeIndx)
                sizeFlag = 1
                break
        elif (quantity == 1):
            if (pos[sizeIndx][1] == "CD" or pos[sizeIndx][1] == "JJ"):
                size = pos[sizeIndx][0]
                pos.pop(sizeIndx)
                sizeFlag = 1
                break
        sizeFlag += 1
    name = ""
    nameFlag = 0
    nameIndx = 0
    while (nameFlag == 0):
        itemXtag = pos[nameIndx][1]
        itemX = pos[nameIndx][0]
        # print(itemX)
        if (itemXtag == "NN" or itemXtag == "NNS"):
            if((len(pos))- nameIndx != 1):
                if(pos[nameIndx + 1][1] == "NN" or pos[nameIndx + 1][1] == "NNS"):
                    name += itemX
                    # nameIndx += 1
                    name += " "
                    pos.pop(nameIndx)
                else:
                    name += itemX
                    nameFlag = 1
                    pos.pop(nameIndx)
                    break
            else:
                name += itemX
                nameFlag = 1
                pos.pop(nameIndx)
                break
        elif (itemXtag == "JJ" or itemXtag == "VBD" or itemXtag == "RB" or itemXtag == "RB" or itemXtag == "RBR"):
            name += itemX
            # nameIndx += 1
            name += " "
            pos.pop(nameIndx)
        else:
            nameIndx += 1
    # print(name)
    score = 0
    indx = 0
    for x in range(len(data['items'])):
        newScore = (fuzz.token_sort_ratio(data['items'][x]['name'], name))
        if (newScore > score):
            score = newScore
            indx = x
        if (newScore == score):
            newScore = (fuzz.ratio(data['items'][x]['name'], name))
            if (newScore > score):
                score = newScore
                indx = x
    if(score < 80):
        invalidFlag = 1
    nameMatch = str(data['items'][indx]['name']).lower()
    nosSizes = len(data['items'][indx]['sizes'])
    sizeScore = 0
    sizeIndx = 0
    for sizeX in range(len(data['items'][indx]['sizes'])):
        newScore = (fuzz.token_sort_ratio(str(data['items'][indx]['sizes'][sizeX][0]).lower(), size))
        if (newScore > sizeScore):
            sizeScore = newScore
            sizeIndx = sizeX
        if (newScore == sizeScore):
            newScore = (fuzz.ratio(str(data['items'][indx]['sizes'][sizeX][0]).lower(), size))
            if (newScore > sizeScore):
                sizeScore = newScore
                sizeIndx = sizeX
    sizeMatch = str(data['items'][indx]['sizes'][sizeIndx][0]).lower()
    if (quantity > 1):
        nameMatch = str(nameMatch) + "s"
    if (str(sizeMatch) != "u"):
        itemStr = (str(quantity) + "x " + str(sizeMatch) + " " + str(nameMatch) + " ")
    else:
        itemStr = (str(quantity) + "x " +  str(nameMatch) + " ")
    if(float(data['items'][indx]['sizes'][sizeIndx][1]) > 0):
        if(sizeMatch != "u"):
            itemIndxs.append([(str(sizeMatch) + " "+ str(nameMatch)),indx,sizeIndx])
        else:
            itemIndxs.append([(str(nameMatch)), indx, sizeIndx])
        price += float(data['items'][indx]['sizes'][sizeIndx][1])
    elif(float(data['items'][indx]['sizes'][sizeIndx][1]) < 0):
        itemStr = items[item]
        discountFlag = 1
    if(discountFlag == 0 or invalidFlag == 0):
        remIndx = []
        notes = ""
        for extrasWords in range(len(pos)):
            if (pos[extrasWords][1] != "NN" or pos[extrasWords][1] != "NNS" or pos[extrasWords][1] != "JJ"):
                for remLex in range(len(removelex)):
                    negScore = fuzz.partial_ratio(pos[extrasWords], removelex[remLex])
                    if (negScore > 75):
                        indxEx = 1
                        remIndx.append(pos[extrasWords])
                        while (pos[extrasWords + indxEx][1] == "NN" or pos[extrasWords + indxEx][1] == "NNS" or
                               pos[extrasWords + indxEx][1] == "RB"
                               or pos[extrasWords + indxEx][1] == "JJ" or pos[extrasWords + indxEx][1] == "CC" or
                               pos[extrasWords + indxEx][0] == ","
                               or pos[extrasWords + indxEx][1] == "RBR" or pos[extrasWords + indxEx][1] == "RBS"):
                            if (pos[extrasWords + indxEx][0] != ","):
                                notes += pos[extrasWords + indxEx][0]
                                notes += " "
                            remIndx.append(pos[indxEx + extrasWords])
                            indxEx += 1
                            if ((extrasWords + indxEx) == (len(pos))):
                                break
                        indxEx = 1
                        if (notes != ""):
                            notesStr = "no " + notes
                            itemStr += notesStr
                            notes = ""
        # pos.remove(remIndx[0])
        ignoreindx = []
        for remX in range(len(remIndx)):
            pos.remove(remIndx[remX])
        # print(pos)
        for itx in range(len(pos)):
            for rem in range(len(addlex)):
                addScore = fuzz.partial_ratio(pos[itx][0], addlex[rem])
                if (addScore > 75):
                    ignoreindx.append(pos[itx])
        for adX in range(len(ignoreindx)):
            pos.remove(pos[adX])
        extras = []
        cv = 0
        while cv < len(pos):
            if(pos[cv][1] != "CC" and pos[cv][1] != "IN" and pos[cv][0] != ","):
                extraStr = ""
                extraStr += pos[cv][0]
                exScore = 0
                exIndx = 0
                for xm in range(len(data['items'][indx]['extras'])):
                    #print(pos[cv][0], pos[cv][1])
                    newScore = (fuzz.token_sort_ratio(data['items'][indx]["extras"][xm], extraStr))
                    if (newScore > exScore):
                        exScore = newScore
                        exIndx = xm
                    if (newScore == exScore):
                        newScore = (fuzz.ratio(data['items'][indx]["extras"][xm], extraStr))
                        if (newScore > exScore):
                            exScore = newScore
                            exIndx = xm
                extraFind = str(data['items'][indx]["extras"][exIndx])
                if(extraFind.find("-") != -1):
                    cv +=1
                itemStr += "add "
                itemStr += str((data['items'][indx]["extras"][exIndx][0])).lower()
                itemStr += " "
                price += float(data['items'][indx]["extras"][exIndx][1])
            cv += 1

    if(invalidFlag == 0 and discountFlag == 0):
        itemStr = itemStr[:-1]
        subtotal += (quantity * price)
        order += str(itemStr + " $" +str(price) + " x " +str(quantity)+  "\n")
    elif(discountFlag == 1):
        discScore = 0
        disIndx= 0
        for it in range(len(itemIndxs)):
            newScore = (fuzz.token_sort_ratio(itemIndxs[it][0],(data['items'][indx]["extras"][0][0])))
            if (newScore > discScore):
                discScore = newScore
                disIndx = it
            if (newScore == discScore):
                newScore = (fuzz.ratio(itemIndxs[it][0],(data['items'][indx]["extras"][0][0])))
                if (newScore > discScore):
                    discScore = newScore
                    disIndx = it
        if(discScore > 90):
            discAmt = data['items'][indx]["extras"][0][1]
            if(type(discAmt) == str):
                discAmt = discAmt[:-1]
                discAmt = float(discAmt)
                discTotal = (data['items'][itemIndxs[disIndx][1]]["sizes"][itemIndxs[disIndx][2]][1] * (1- discAmt))
                subtotal -= discTotal
            elif(type(discAmt) == float):
                #print(data['items'][itemIndxs[disIndx][1]]["sizes"][itemIndxs[disIndx][2]][1])
                discTotal = (discAmt)
                subtotal -= discAmt
            order += items[item] +(' -${0}'.format(format(discTotal, ',.2f')))
            order += "\n"
        else:
            order += "invalid coupon \n"
    else:
        order += "invalid item \n"


subtotal += 0.20
fee = 0.2
order += ('proces. fee ${0}'.format(format(fee, ',.2f'))) + "\n"
order += ('subtotal ${0}'.format(format(subtotal, ',.2f'))) + "\n"
tax = subtotal * 0.1
order += ('tax ${0}'.format(format(tax, ',.2f'))) + "\n"
total = subtotal +tax
order += ('total ${0}'.format(format(total, ',.2f')))
print(order)

