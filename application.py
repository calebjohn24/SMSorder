import datetime
import json
import random
import urllib.request
import nexmo
import nltk
import paypalrestsdk
from firebase import firebase
from flask import Flask, request, redirect, url_for
from fuzzywuzzy import fuzz
from werkzeug.datastructures import ImmutableOrderedMultiDict
from words2num import w2n
from spellchecker import SpellChecker
from flask import render_template

database = firebase.FirebaseApplication("https://cedarfb2.firebaseio.com/")
uid = "MmvTki8FjtM07zdTHA3QMfxp6712"
data = (database.get("restaurants/" + uid, "/menu/items/"))

paypalClient = "AbnvQxz3b9dhXBe_sQyCER6mrviKkOGoPltfEwQB28_f_gbptqAYSocORdwPJJ42lxDtVfZVIDv38dWl"
paypalSecret = "EIiJshTzYsufiKZmB8sYjpEiJLirn5O9D7K-2Y5B3aeJjSkjClg_ruhGsnua9o7UM3RttsofUFGG3xnh"
VERIFY_URL_PROD = 'https://ipnpb.paypal.com/cgi-bin/webscr'
VERIFY_URL_TEST = 'https://ipnpb.sandbox.paypal.com/cgi-bin/webscr'
items = []
login = "payments@cedarrobots.com"
password = "CedarPayments1!"


paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox or live
    "client_id": paypalClient,
    "client_secret": paypalSecret})

client = nexmo.Client(key='8558cb90', secret='PeRbp1ciHeqS8sDI')

NexmoNumber = '13166009096'
databse = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
estNameStr = "TestRaunt"
promoPass = "promo-" + str(estNameStr)
addPass = "add-" + str(estNameStr)
remPass = "remove-" + str(estNameStr)
estName = "MmvTki8FjtM07zdTHA3QMfxp6712"
link = "LINK"

app = Flask(__name__)


def genUsr(name, number):
    UserData = database.get("/", "users")
    timeStamp = datetime.datetime.today()
    database.put("/users/", "/" + str(len(UserData)) + "/name", name)
    database.put("/users/", "/" + str(len(UserData)) + "/number", number)
    database.put("/users/", "/" + str(len(UserData)) + "/restaurants/" + estNameStr + "/" + str(0) + "/StartTime",
                 str(timeStamp))
    database.put("/users/", "/" + str(len(UserData)) + "/restaurants/" + estNameStr + "/" + str(0) + "/loyaltyCard",
                 "NOCARD")


def verifyPayment(indxFB):
    DBdata = database.get("/restaurants/" + estName, "orders")
    code = DBdata[indxFB]["paid"]
    cash = DBdata[indxFB]["cash"]
    while code == 0 and cash != "CASH":
        DBdata = database.get("/restaurants/" + estName, "orders")
        code = DBdata[indxFB]["paid"]
        cash = DBdata[indxFB]["cash"]
        if (code == 1 or cash == "CASH"):
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata) - 1) + "/", "/filled/", "1")
            break
    return "found"


def translateOrder(msg, indxFB):
    DBdata = database.get("/restaurants/" + estName, "orders")
    couponflag = 0
    userOrder = msg
    spell = SpellChecker()
    userOrder = userOrder.lower()
    userOrder = userOrder.replace('oz.', 'oz')
    userOrder = userOrder.replace('\n', ';')
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

    measurements = ["oz", 'pc', 'pce', 'pcs', 'lbs', 'lb', 'ounce', 'ozs', 'ounces', 'pound', 'pounds'
        , 'grams', 'g', 'gram', 'gs', "milligram", 'mg', 'milligrams', 'mgs', 'kilogram', 'kg'
        , 'kilograms', 'kgs', 'piece', 'pice', 'piecie']

    removelex = ["without", "no", "remove", "take out", "w/o", "take off", "out"]
    addlex = ["with", "add", "more", "w/", "include"]
    fractions = [['half', 0.5], ['fourth', 0.25], ['third', 0.333333], ['fifth', 0.2], ['quarter', 0.25],
                 ['eighth', 0.125], ['sixteenth', 0.00625]]
    for frac in range(2, 65):
        fractions.append([("1/" + str(frac)), (1 / frac)])
    writeStr = ""
    if (userOrder[-1] == ";"):
        userOrder = userOrder[:-1]

    items = [x.strip() for x in userOrder.split(';')]
    if (len(items) < 1):
        items.append(userOrder)

    subtotal = 0
    itemsOrdered = []
    for item in range(len(items)):
        price = 0.0
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
            tokens.pop((frrIndx + 1))

        for bb in range(len(tokens)):
            try:
                print(tokens[bb])
                print(w2n(tokens[bb]))
                tokens.insert(bb, str(w2n(tokens[bb])))
                tokens.pop(bb + 1)
            except:
                pass

        for mm in range(len(tokens)):
            for ltrs in range(len(tokens[mm])):
                tokenizedToken.append([str(tokens[mm][ltrs]), mm])

        for ttk in range(len(tokenizedToken)):
            try:
                int(tokenizedToken[ttk][0])
                numIndxs.append(ttk)
                tokenizedToken.insert((ttk + 1), [" ", 1000])
            except ValueError:
                pass

        currentNum = 0
        for tk0 in range(len(tokenizedToken)):
            if (currentNum == tokenizedToken[tk0][1]):
                newStr += str(tokenizedToken[tk0][0])
                currentNum = tokenizedToken[tk0][1]
            elif (tokenizedToken[tk0][1] == 1000):
                if (tokenizedToken[tk0 + 1][1] == currentNum):
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
        if (len(newTokens) == 1):
            for cpn in range(len(data)):
                if (data[cpn] != None):
                    # print(data[cpn]['sizes'][0][1])
                    if (data[cpn]['sizes'][0][1] == -1):
                        if (newTokens[0] == data[cpn]['name'].lower()):
                            print("coupon found")
                            couponFlag = 100
                            discAmt = data[cpn]["extras"][0][1]
                            numUsed = 1
                            for hh in range(len(itemsOrdered)):
                                scoreDisc = (
                                    fuzz.token_sort_ratio(itemsOrdered[hh][0], data[cpn]['extras'][0][0].lower()))
                                if (scoreDisc > 95):
                                    limit = data[cpn]['extras'][1][1]
                                    if (type(discAmt) == str):
                                        discAmt = discAmt[:-1]
                                        discAmt = float(discAmt)
                                        discAmt = itemsOrdered[hh][1] * discAmt
                                        subtotal -= discAmt
                                    elif (type(discAmt) == float or type(discAmt) == int):
                                        discTotal = (discAmt)
                                        subtotal -= discAmt
                                    if (itemsOrdered[hh][2] > limit):
                                        while (limit > numUsed):
                                            if (type(discAmt) == str):
                                                discAmt = discAmt[:-1]
                                                discAmt = float(discAmt)
                                                discAmt = itemsOrdered[hh][1] * discAmt
                                                subtotal -= discAmt
                                            elif (type(discAmt) == float or type(discAmt) == int):
                                                discTotal = (discAmt)
                                                subtotal -= discAmt
                                            numUsed += 1

                        writeStr += items[item] + (' -${0}'.format(format(discAmt * numUsed, ',.2f')))
                        writeStr += " x " + str(numUsed)
                        writeStr += "\n"

        if (couponFlag == 0):
            for tk1 in range(len(newTokens)):
                for measure in range(len(measurements)):
                    tknz = str(newTokens[tk1]) == (measurements[measure])
                    if (str(newTokens[tk1]) == (measurements[measure])):
                        sizeArr.append(newTokens[tk1 - 1])
                        sizeArr.append(newTokens[tk1])

            sizeFlag = 0
            if (len(sizeArr) > 0):
                for szza in range(len(sizeArr)):
                    newTokens.remove(sizeArr[szza])
                sizeFlag = 1
            tokenPos = nltk.pos_tag(newTokens)
            # print(tokenPos)
            quantIndx = -1
            quant = 1
            for posInt in range(len(tokenPos)):
                if (tokenPos[posInt][1] == "CD"):
                    try:
                        int(newTokens[posInt])
                        quant = int(newTokens[posInt])
                        quantIndx = posInt
                    except ValueError:
                        int(w2n(newTokens[posInt]))
                        quant = int(w2n(newTokens[posInt]))
                        quantIndx = posInt

            if (-1 != quantIndx):
                newTokens.pop(quantIndx)

            spellChkTokens = []
            for spll in range(len(newTokens)):
                spellChkTokens.append(spell.correction(newTokens[spll]))
            testString = ""
            if (len(sizeArr) == 0):
                for szz in range(len(spellChkTokens)):
                    testString = spellChkTokens[szz]
                    testString += " "
                testString = spellChkTokens[0:2]
                testScore = 0
                nameIndx = 0
                sizeIndx = 0
                for dataNM in range(len(data)):
                    if (data[dataNM] != None):
                        if (data[dataNM]['sizes'][0][0] != "u"):
                            for dataSZ in range(len(data[dataNM]['sizes'])):
                                compStr = data[dataNM]['name'] + " " + data[dataNM]['sizes'][dataSZ][0]
                                compStr = str(compStr).lower()
                                newScore = fuzz.token_sort_ratio(compStr, testString)
                                if (newScore > testScore):
                                    testScore = newScore
                                    nameIndx = dataNM
                                    sizeIndx = dataSZ
                                elif (newScore == testScore):
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
                        if (data[dataNM]['sizes'][0][0] != "u"):
                            for dataSZ in range(len(data[dataNM]['sizes'])):
                                compStr = data[dataNM]['name'] + " " + data[dataNM]['sizes'][dataSZ][0]
                                compStr = str(compStr).lower()
                                newScore = fuzz.token_sort_ratio(compStr, testString)
                                # print(newScore, testScore, compStr, testString)
                                if (newScore > testScore):
                                    testScore = newScore
                                    nameIndx = dataNM
                                    sizeIndx = dataSZ
                                elif (newScore == testScore):
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
                            # print(newScore, testScore, compStr, testString)
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
            price += float(data[nameIndx]['sizes'][sizeIndx][1])
            name = str(data[nameIndx]['name']).lower()
            size = str(data[nameIndx]['sizes'][sizeIndx][0]).lower()
            print(newScore)
            testScore = 0
            remNameIndxs = []
            if (sizeFlag == 0):
                lenName = len(name.split()) + len(size.split())
            else:
                lenName = len(name.split())

            spellChkTokens = spellChkTokens[lenName:]
            if (len(spellChkTokens) > 0):
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
                        # print(removelex[rLex], spellChkTokens[sppR], newScore)
                        if (newScore > 85):
                            addScore = newScore
                            spIndx = sppR
                            aLexIndx = rLex
                            remNameIndxs.append(sppR)

                if (len(spellChkTokens) > 0):
                    if (len(remNameIndxs) != 0 and len(addwordIndxs) != 0):
                        state = 0
                        currentWord = 0
                        for remEx in range(len(spellChkTokens)):
                            for hh in range(len(remNameIndxs)):
                                if (remNameIndxs[hh] == remEx):
                                    state = 1
                                    currentWord = 1
                                    break
                                else:
                                    currentWord = 0
                            for yy in range(len(addwordIndxs)):
                                if (addwordIndxs[yy] == remEx):
                                    state = 0
                                    currentWord = 1
                                    break
                                else:
                                    currentWord = 0
                            if (currentWord == 0):
                                if (state == 0):
                                    extras.append(spellChkTokens[remEx])
                                elif (state == 1):
                                    notes += " "
                                    notes += spellChkTokens[remEx]
                    elif (len(remNameIndxs) != 0 and len(addwordIndxs) == 0):
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
                    elif (len(remNameIndxs) == 0 and len(addwordIndxs) == 0):
                        for remEx in range(len(spellChkTokens)):
                            extras.append(spellChkTokens[remEx])
                            # print(spellChkTokens[remEx])

            if (notes != ""):
                if (size != 'u'):
                    writeStr += size
                    writeStr += " "
                writeStr += name
                writeStr += ' '
                writeStr += notes
                writeStr += " "
            else:
                if (size != 'u'):
                    writeStr += size
                    writeStr += " "
                writeStr += name
            appStr = ""
            if (size != 'u'):
                appStr += size
                appStr += " "
            appStr += name
            itemsOrdered.append([appStr, price, quant])
            if (len(extras) > 0):
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
                    extraIndxs.append([e, extraIndx])
                newExStr = ''
                remIndxs = []
                for rr in range(len(extraIndxs)):
                    exLen = len(str(data[nameIndx]['extras'][extraIndxs[rr][1]][0]).split())
                    print(str(data[nameIndx]['extras'][extraIndxs[rr][1]][0]), exLen)
                    if (exLen > 1):
                        newExStr += extras[extraIndxs[rr][0]]
                        remIndxs.append(extras[extraIndxs[rr][0]])

                if (len(remIndxs) > 1):
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
                        extraIndxs.append([e, extraIndx])
                # print(extraIndxs)
                for rrn in range(len(extraIndxs)):
                    exV = (extraIndxs[rrn][1])
                    writeStr += " add "
                    writeStr += data[nameIndx]['extras'][exV][0].lower()
                    price += float(data[nameIndx]['extras'][exV][1])
                    print("inc3")

            writeStr += " x "
            writeStr += str(quant)
            price = float(price) * quant
            subtotal += price
            writeStr += " " + '${:0,.2f}'.format(price)
            writeStr += "\n"
            extras = []
            notes = ''

    usrIndx = DBdata[indxFB]["userIndx"]
    numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
    database.put("/restaurants/" + estName + "/orders/" + str(indxFB) + "/", "finalOrder/", writeStr)
    database.put("/users/",
                 "/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str((len(numOrders) - 1)) + "/order/",
                 str(writeStr))
    writeStr += "process fee $0.20 \n"
    subtotal += 0.2
    writeStr += "subtotal " + '${:0,.2f}'.format(subtotal)
    writeStr += "\n"
    tax = subtotal * 0.1
    writeStr += "tax " + '${:0,.2f}'.format(tax)
    writeStr += "\n"
    total = subtotal * 1.1
    linkTotal = float(total)
    writeStr += "total " + '${:0,.2f}'.format(total)
    totalStr = "" + '${:0,.2f}'.format(total)
    writeStr += "\n"
    writeStr += 'if everything looks good enter "ok" otherwise enter "help"'
    order = writeStr
    print(order)
    database.put("/restaurants/" + estName + "/orders/" + str(indxFB) + "/", "total/", str(totalStr))
    database.put("/restaurants/" + estName + "/orders/" + str(indxFB) + "/", "linkTotal/", str(linkTotal))
    usrIndx = DBdata[indxFB]["userIndx"]
    numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
    database.put("/users/",
                 "/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str((len(numOrders) - 1)) + "/total/",
                 str(totalStr))

    return order


def logOrder(tix, number):
    logDate = (datetime.datetime.now().strftime("%Y-%m"))
    database.put("/log/" + estName + "/" + str(logDate), "/exp/", 0)
    currentVal = (database.get("/log/" + str(estName) + "/" + str(logDate) + "/", "orders"))
    currentacct = (database.get("/log/" + str(estName) + "/" + str(logDate) + "/", "acct"))
    if (currentacct == None):
        database.put("/log/" + estName + "/" + str(logDate), "/orders/", (1))
        database.put("/log/" + estName + "/" + str(logDate), "/acct/", (0.2))
    else:
        database.put("/log/" + estName + "/" + str(logDate), "/orders/", (currentVal + 1))
        database.put("/log/" + estName + "/" + str(logDate), "/acct/", (currentacct + 0.20))
    database.put("/restaurants/" + estName + "/orders/" + str(tix) + "/", "/number/", str(number) + ".")


def genPayment(total, name, UUIDcode):
    print(UUIDcode)
    print(name)
    apiurl = "http://tinyurl.com/api-create.php?url="
    paymentLink = 'https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_xclick&business=sb-ninhv43009@business.example.com&currency_code=USD&amount=' \
                  '' + str(total) + '&item_name=' + str(UUIDcode)
    tinyurl = urllib.request.urlopen(apiurl + paymentLink).read()
    shortLink = tinyurl.decode("utf-8")
    return shortLink


def getReply(msg, number):
    msg = msg.lower()
    indx = 0
    DBdata = database.get("/restaurants/" + estName, "/orders")
    UserData = database.get("/", "users")
    if (msg == "order" or msg == "ordew" or msg == "ord" or msg == "ordet" or msg == "oderr" or msg == "ordee"):
        UUID = random.randint(9999, 100000)
        reply = "Hi welcome to " + estNameStr + " please enter your name to continue"
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/UUID/", str(UUID))
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/name/", "")
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/number/", str(number))
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/unprocessedOrder/", "")
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/stage/", 1)
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/paid/", 0)
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/cash/", "")
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/togo/", "")
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/filled/", "0")
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "finalOrder/", "")
        UserData = database.get("/", "users")
        for usr in range(len(UserData)):
            if (number == UserData[usr]["number"]):
                print("found user")
                timeStamp = datetime.datetime.today()
                reply = "Hi " + str(
                    UserData[usr]["name"]) + "! welcome to " + estNameStr + " is this order for here to go"
                database.put("/restaurants/" + estName + "/orders/" + str((len(DBdata))) + "/", "/name/",
                             str(UserData[usr]["name"]))
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/filled/", "0")

                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/stage/", 2)
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/userIndx/", usr)
                numOrders = database.get("/users/" + str(usr) + "/restaurants/", estNameStr)
                loyaltyCard = numOrders[0]["loyaltyCard"]
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/loyaltyCard/",
                             "LoyaltyCard")
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/orderIndx/",
                             (len(numOrders)))
                database.put("/users/",
                             "/" + str(usr) + "/restaurants/" + estNameStr + "/" + str((len(numOrders))) + "/Starttime",
                             str(timeStamp))

                break
            if ((len(UserData) - usr) == 1):
                genUsr("", number)
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/userIndx/",
                             (len(UserData)))
        client.send_message({
            'from': NexmoNumber,
            'to': number,
            'text': reply
        })
        return reply
    elif (msg == promoPass):
        print("gen new code")
        reply = "enter the Name of this coupon Ex: 50% off medium coffee"
        client.send_message({
            'from': NexmoNumber,
            'to': number,
            'text': reply
        })
        return reply
    else:
        for db in range(len(DBdata)):
            phoneNumDB = DBdata[db]['number']
            if (phoneNumDB == number):
                indx = db
                break
            elif ((len(DBdata) - db) == 1):
                print("no msg")
                return 200
        if (DBdata[indx]['stage'] == 1):
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/name/", str(msg).capitalize())
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 2)
            reply = "Hi, " + str(msg).capitalize() + " is this order for-here or to-go?"
            usrIndx = DBdata[indx]["userIndx"]
            database.put("/users", "/" + str(usrIndx) + "/name", str(msg.capitalize()))
            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': reply
            })
        elif (DBdata[indx]['stage'] == 2):
            if (
                    msg == "for here" or msg == "fo here" or msg == "for her" or msg == "for herw" or msg == "for herr" or msg == "here"):
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 3)
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/togo/", "HERE")
                usrIndx = DBdata[indx]["userIndx"]
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
                print((len(numOrders)))
                database.put("/users/",
                             "/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                                 (len(numOrders) - 1)) + "/to-go",
                             str("here"))

                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': "Sounds good! your order will be " + "for-here\n" + "if you want"
                                                                                " your order now enter" + ' "asap" otherwise enter your preferred time.(EX 11:15am)'
                })
            else:
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/togo/", "TO_GO")
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 3)
                usrIndx = DBdata[indx]["userIndx"]
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
                database.put("/users/",
                             "/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                                 (len(numOrders) - 1)) + "/to-go",
                             str("to-go"))
                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': "Sounds good! your order will be " + "to-go\n" + "if you want"
                                                                             " your order now enter " + '"asap" otherwise enter the time your preferred time.(EX 11:15am)'
                })
        elif (DBdata[indx]['stage'] == 3):
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/time/", msg.upper())
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 4)
            usrIndx = DBdata[indx]["userIndx"]
            numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
            database.put("/users/",
                         "/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                             (len(numOrders) - 1)) + "/pickup-time",
                         str(msg))
            reply = "-Got it!, you can " \
                    "view the menu here " + link + "\n-first enter your items then any promo-codes," \
                                                   " one by one in DIFFERENT TEXTS\n" \
                                                   "-Enter " + '"DONE" when finished'

            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': reply
            })
            print("m0")
            return reply

        elif (DBdata[indx]['stage'] == 4):
            if (msg == "done"):
                database.get("/restaurants/" + estName + "/orders/" + str(indx) + "/",
                             "unprocessedOrder")
                reply = translateOrder(DBdata[indx]['unprocessedOrder'], indx)
                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': reply
                })
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 5)
                return reply
            else:
                msgData = str(
                    database.get("/restaurants/" + estName + "/orders/" + str(indx) + "/",
                                 "unprocessedOrder"))
                print(msgData)
                if (msg[-1] != "."):
                    msgData += str(msg)
                    msgData += ";"
                else:
                    msgData += str(msg)
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/unprocessedOrder/", msgData)
                return
        elif (DBdata[indx]['stage'] == 5):
            if (msg == "ok"):
                timeStamp = datetime.datetime.today()
                usrIndx = DBdata[indx]["userIndx"]
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
                database.put("/users/",
                             "/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                                 (len(numOrders) - 1)) + "/EndTime",
                             timeStamp)
                total = DBdata[indx]['linkTotal']
                UUID = DBdata[indx]['UUID']
                name = DBdata[indx]['name']
                reply = 'thanks, please click the link below to pay if you want to pay cash enter "CASH"\n ' \
                        "" + genPayment(total, name, UUID)
                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': reply
                })
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 6)
                DBdata = database.get("/restaurants/" + estName, "orders")
                usrIndx = DBdata[indx]["userIndx"]
                verifyPayment(indx)
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
                loyaltyCard = numOrders[0]["loyaltyCard"]
                cash = DBdata[indx]["cash"]
                if (cash != 1):
                    if (loyaltyCard != "LoyaltyCard"):
                        client.send_message({
                            'from': NexmoNumber,
                            'to': number,
                            'text': "-your order has been processed and will be ready shortly, thank you!\n-would you like to be registered you for a loyalty card?"
                        })
                    else:
                        database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/loyaltyCard/",
                                     "LoyaltyCard")
                        client.send_message({
                            'from': NexmoNumber,
                            'to': number,
                            'text': "your order has been processed and will be ready shortly! we've added points to your loyalty card"
                        })
                    usrIndx = DBdata[indx]["userIndx"]
                    numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
                    logOrder(indx, number)
                    database.put("/users/",
                                 "/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                                     (len(numOrders) - 1)) + "/paymentMethod",
                                 "card")
                return reply

            elif (msg == "help"):
                reply = "-Sorry about that, please try re-entering your items, please text me items " \
                        "in this format\n" + '-"Quantity, Item Name, toppings to add, "no" toppings to remove"'
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/unprocessedOrder/", "")
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 4)
                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': reply
                })
                return reply

        elif (DBdata[indx]['stage'] == 6):
            if (msg == "cash"):
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/cash/", "CASH")
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/paid/", 0)
                usrIndx = DBdata[indx]["userIndx"]
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
                database.put("/users/",
                             "/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                                 (len(numOrders) - 1)) + "/paymentMethod",
                             "cash")
                reply = "No problem! enjoy your order, the staff will take your cash payment when you pick up your order"
                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': reply
                })
                logOrder(indx, number)
            elif ((msg == "ok" or msg == "yes" or msg == "sure" or msg == "ye" or msg == "yep" or msg == "yup"
                   or msg == "i do" or msg == "y" or msg == "i do want one" or msg == "yeah" or msg == "yea" or msg == "alright") and
                  DBdata[indx]['paid'] == 1):
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/loyaltyCard/", "SIGN-UP")
                usrIndx = DBdata[indx]["userIndx"]
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", )
                database.put("/users/",
                             "/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                                 (len(numOrders) - 1)) + "/loyaltyCard",
                             1)
                reply = "Thanks! we'll sign you up, enjoy your order"
                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': reply
                })
                logOrder(indx, number)
                return reply
            elif (msg == "no" or msg == "don't" or msg == "nope" or msg == "nah" or msg == "n" or
                  msg == "no thanks" or msg == "nop" or msg == "i don't want one" or msg == "i don't" or msg == "i dont" or msg == "i dont want one"):
                reply = "No problem! enjoy your order!"
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/loyaltyCard/", "NOCARD")
                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': reply
                })
                logOrder(indx, number)
                return reply
            else:
                return 200
        else:
            return 200


@app.route('/sms', methods=['GET', 'POST'])
def inbound_sms():
    data = dict(request.form) or dict(request.args)
    print(data["text"])
    number = str(data['msisdn'][0])
    msg = str(data["text"][0])
    print(number, msg)

    getReply(msg, number)

    return ('', 200)


@app.route('/ipn', methods=['POST'])
def ipn():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    DBdata = database.get("/restaurants/" + estName, "orders")
    for dbItems in range(len(DBdata)):
        if (DBdata[dbItems]["UUID"] == rsp["item_name"]):
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/paid/", 1)
            usrIndx = DBdata[dbItems]["userIndx"]
            numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
            database.put("/users/", "/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                (len(numOrders) - 1)) + "/totalPaid", rsp["mc_gross"])
            database.put("/users/", "/" + str(usrIndx) + "/email", rsp["payer_email"])
            database.put("/users/", "/" + str(usrIndx) + "/country", rsp["address_country_code"])
            database.put("/users/", "/" + str(usrIndx) + "/state", rsp["address_state"])
            database.put("/users/", "/" + str(usrIndx) + "/zipCode", rsp["address_zip"])
            database.put("/users/", "/" + str(usrIndx) + "/city", rsp["address_city"])
            database.put("/users/", "/" + str(usrIndx) + "/streetAdr", rsp["address_street"])
            logDate = (datetime.datetime.now().strftime("%Y-%m"))
            database.put("/log/" + estName + "/" + str(logDate), "/exp/", 0)
            currentacct = (database.get("/log/" + str(estName) + "/" + str(logDate) + "/", "paypalFees"))
            if (currentacct != None):
                database.put("/log/" + estName + "/" + str(logDate), "/paypalFees/",
                             (float(rsp["mc_fee"]) + currentacct))
            else:
                database.put("/log/" + estName + "/" + str(logDate), "/paypalFees/", float(rsp["mc_fee"]))
    return (" ", 200)


@app.route('/' + estNameStr, methods=['GET'])
def view():
    orders = database.get("/restaurants/" + estName, "orders")
    webDataDisp = []
    keys = []
    print(orders)
    for ords in range(len(orders)):
        filled = orders[ords]["filled"]
        if (filled == "1"):
            UUID = orders[ords]["UUID"]
            writeStr = str(orders[ords]["name"]) + " " + str(orders[ords]["finalOrder"]) \
                       + " " + str(orders[ords]["togo"]) + " " + str(orders[ords]["time"]) + " " \
                 "" + str(orders[ords]["total"]) + " " + str(orders[ords]["loyaltyCard"]) + " " + str(orders[ords]["cash"])
            keys.append(UUID)
            webDataDisp.append(writeStr)
    return render_template("index.html", len=len(webDataDisp), webDataDisp=webDataDisp, keys=keys, btn=estNameStr)


@app.route('/' + estNameStr, methods=['POST'])
def button():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    item = (rsp['item'])
    print(item)
    orders = database.get("/restaurants/" + estName, "orders")
    webDataDisp = []
    keys = []
    print(orders)
    for ords in range(len(orders)):
        UUID = orders[ords]["UUID"]
        if (item == UUID):
            database.put("/restaurants/" + estName + "/orders/" + str(ords) + "/", "/filled/", "2")
        else:
            filled = orders[ords]["filled"]
            if (filled == "1"):
                writeStr = str(orders[ords]["name"]) + " " + str(orders[ords]["finalOrder"]) \
                           + " " + str(orders[ords]["togo"]) + " " + str(orders[ords]["time"]) + " " \
                                                                                                 "" + str(
                    orders[ords]["total"]) + " " + str(orders[ords]["loyaltyCard"]) + " " + str(orders[ords]["cash"])
                keys.append(UUID)
                webDataDisp.append(writeStr)
    return render_template("index.html", len=len(webDataDisp), webDataDisp=webDataDisp, keys=keys, btn=estNameStr)

@app.route('/'+remPass, methods=['GET'])
def removeItemsDisp():
    menuItems = database.get("/restaurants/" + estName +"/menu/", "items")
    print(menuItems)
    names = []
    keys = []
    for men in range(len(menuItems)):
        if(menuItems[men] != None):
            names.append(menuItems[men]["name"])
            keys.append(men)
    return render_template("remItems.html", len=len(names), names=names, keys=keys, btn=remPass)

@app.route('/'+remPass, methods=['POST'])
def removeItems():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    item = int(rsp['item'])
    names = []
    keys = []
    database.delete("/restaurants/" + estName + "/menu/items/", item)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    for men in range(len(menuItems)):
        if(menuItems[men] != None):
            names.append(menuItems[men]["name"])
            keys.append(men)
    return render_template("remItems.html", len=len(names), names=names, keys=keys, btn=remPass)

@app.route('/'+addPass, methods=['GET'])
def addItmDisp():
    return render_template('addform.html', btn=addPass)

@app.route('/'+addPass, methods=['POST'])
def addItmForm():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    name = (rsp['name'])
    numSizes = int(rsp['numSizes'])
    sku = (rsp['sku'])
    print(name)
    print(numSizes)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    keyVal = 0
    for mmx in range(len(menuItems)):
        if(menuItems[mmx] != None):
            if(keyVal < mmx):
                keyVal = mmx
    keyVal += 1
    database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal) , "/name/", name)
    database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/sku/", sku)
    database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal) , "/inp/", "inp")
    for nn in range(numSizes):
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal) + "/sizes/" + str(nn) , "/0", "")
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal) + "/sizes/" + str(nn) , "/1", 0)
        return render_template('addform2.html', btn=(str(addPass) + "2"), len=numSizes)

''' 
@app.route('/'+addPass+"2", methods=['GET'])
def addItmForm2():
    return render_template('addform2.html', btn=(str(addPass) + "2"),len = 2)
'''

@app.route('/'+addPass+"2", methods=['POST'])
def addItmResp2():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    print(rsp)
    numExtras = rsp["numEx"]
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    for sx in range(len(menuItems)):
        if(menuItems[sx] != None):
            if(menuItems[sx]['inp'] == "inp"):
                for ssz in range(int((len(rsp)-1)/2)):
                    szName = rsp[str(ssz)]
                    szPrice = rsp[str(ssz) + "a"]
                    database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/sizes/" + str(ssz) ,"/0/", szName)
                    database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/sizes/" + str(ssz) , "/1/",float(szPrice))
                for sse in range(int(numExtras)):
                    database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse) , "/0/", "")
                    database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse) , "/1/", 0)
                break
    return render_template('addform3.html', btn=(str(addPass) + "3"), len=int(numExtras))

@app.route('/'+addPass+"3", methods=['GET'])
def addItmForm3():
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    for sx in range(len(menuItems)):
        if (menuItems[sx] != None):
            if (menuItems[sx]['inp'] == "inp"):
                itxL = int(len(menuItems[sx]['extras']))
                return render_template('addform3.html', btn=(str(addPass) + "3"), len=itxL)

@app.route('/'+addPass+"3", methods=['POST'])
def addItmResp3():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    for sx in range(len(menuItems)):
        if (menuItems[sx] != None):
            if (menuItems[sx]['inp'] == "inp"):
                for sse in range(int(len(rsp)/2)):
                    exName = rsp[str(sse)]
                    exPrice = rsp[str(sse) + "a"]
                    database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse) , "/0/", exName)
                    database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse) ,"/1/", float(exPrice))
                database.put("/restaurants/" + estName + "/menu/items/" + str(sx), "/inp/", "")
                break
    return redirect(url_for('addItmDisp'))

@app.route('/'+promoPass, methods=['GET'])
def addCpn():
    return render_template('coupon.html')

@app.route('/'+promoPass, methods=['POST'])
def addCpnResp():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    print(rsp)
    name = rsp['name']
    item = rsp['itm']
    amt = rsp['amt']
    limit = rsp['lim']
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    keyVal = 0
    for mmx in range(len(menuItems)):
        if (menuItems[mmx] != None):
            if (keyVal < mmx):
                keyVal = mmx
    keyVal += 1
    database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/name/", name)
    database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/sizes/0/0/", "u")
    database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/sizes/0/1/", -1)
    database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/extras/0/0/", item)
    try:
        amt = float(amt)
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/extras/0/1/", amt)
    except ValueError:
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/extras/0/1/", amt)
    database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/extras/1/0/", "limit")
    database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/extras/1/1/", limit)
    return render_template('coupon.html')

@app.route("/"+uid,methods=["GET"])
def sendPromo():
    return render_template('sendPromo.html')


@app.route("/"+uid,methods=["GET"])
def checkPromo():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    print(rsp)
    return render_template('sendPromo.html')

# when you run the code through terminal, this will allow Flask to work
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
