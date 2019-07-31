import json
import nltk
from fuzzywuzzy import fuzz
from words2num import w2n

with open('menu.json') as data_file:
    data = json.load(data_file)

foodItems = (data['items'])
items = []
userOrder = "2 Burgers with honey mustard no bacon. five 8 oz. Iced Coffee's with chocolate sauce, caramel sauce, no cream. 5 med coffee's with no cream espresso, or sugar. " \
            "Chicken Burger with Hot Sauce and avacado, no bacon"
removelex = ["without", "no", "remove", "take out", "w/o", "take off"]
addlex = ["with", "add", "more", "w/", "include"]
userOrder = userOrder.lower()
userOrder = userOrder.replace('oz.', '')
userOrder = userOrder.replace('ounce', '')
userOrder = userOrder.replace('oz', '')
userOrder = userOrder.replace('ounces', '')

# userOrder = userOrder.replace(',', '')
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
    price = 0
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
                quantity = int(word)
                pos.pop(tknQty)
                break
            except ValueError:
                wordConv = w2n(word)
                quantity = int(wordConv)
                pos.pop(tknQty)
                break
    # print(quantity,pos)
    sizeFlag = 0
    sizeIndx = 0
    while sizeFlag != 1:
        # print(pos[tkns][0], "POS.", pos[tkns][1])
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
            name += itemX
            nameFlag = 1
            pos.pop(nameIndx)
            break
        elif (itemXtag == "JJ"):
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
        itemStr = (str(quantity) + "x " + str(nameMatch) + " ")
    price += float(data['items'][indx]['sizes'][sizeIndx][1])
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
                        score = newScore
                        exIndx = xm
            extraFind = str(data['items'][indx]["extras"][exIndx])
            if(extraFind.find("-") != -1):
                cv +=1
            itemStr += "add "
            itemStr += str((data['items'][indx]["extras"][exIndx][0])).lower()
            #print(len(data['items'][indx]["extras"][exIndx][0]))
            #print(itemStr)
            itemStr += " "
            price += float(data['items'][indx]["extras"][exIndx][1])
        cv += 1


    itemStr = itemStr[:-1]
    subtotal += (quantity * price)
    order += str(itemStr + " $" +str(price) + " x " +str(quantity)+  "\n")


subtotal += 0.20
fee = 0.2
order += ('subtotal ${0}'.format(format(subtotal, ',.2f'))) + "\n"
tax = subtotal * 0.1
order += ('tax ${0}'.format(format(tax, ',.2f'))) + "\n"
total = subtotal +tax
order += ('proces. fee ${0}'.format(format(fee, ',.2f'))) + "\n"
order += ('total ${0}'.format(format(total, ',.2f')))
print(order)

