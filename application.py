import datetime
import json
import random
import urllib.request

import nexmo
import nltk
import paypalrestsdk
from firebase import firebase
from flask import Flask, request
from fuzzywuzzy import fuzz
from werkzeug.datastructures import ImmutableOrderedMultiDict
from words2num import w2n

database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/")
with open('menu.json') as data_file:
    data = json.load(data_file)

paypalClient = "AbnvQxz3b9dhXBe_sQyCER6mrviKkOGoPltfEwQB28_f_gbptqAYSocORdwPJJ42lxDtVfZVIDv38dWl"
paypalSecret = "EIiJshTzYsufiKZmB8sYjpEiJLirn5O9D7K-2Y5B3aeJjSkjClg_ruhGsnua9o7UM3RttsofUFGG3xnh"
VERIFY_URL_PROD = 'https://ipnpb.paypal.com/cgi-bin/webscr'
VERIFY_URL_TEST = 'https://ipnpb.sandbox.paypal.com/cgi-bin/webscr'
foodItems = (data['items'])
items = []
login = "payments@cedarrobots.com"
password = "CedarPayments1!"

promoPass = "asnifnr10002"
paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox or live
    "client_id": paypalClient,
    "client_secret": paypalSecret})

client = nexmo.Client(key='8558cb90', secret='PeRbp1ciHeqS8sDI')

NexmoNumber = '13166009096'
databse = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
estName = "TestRaunt"
link = "LINK"

app = Flask(__name__)


def genUsr(name, number):
    UserData = database.get("/", "users")
    timeStamp = datetime.datetime.today()
    database.put("/users/", "/" + str(len(UserData)) + "/name", name)
    database.put("/users/", "/" + str(len(UserData)) + "/number", number)
    database.put("/users/", "/" + str(len(UserData)) + "/restaurants/" + estName + "/" + str(0) + "/StartTime",
                 str(timeStamp))
    database.put("/users/", "/" + str(len(UserData)) + "/restaurants/" + estName + "/" + str(0) + "/loyaltyCard", 0)


def verifyPayment(indxFB):
    DBdata = database.get("/restaurants/" + estName, "orders")
    code = DBdata[indxFB]["paid"]
    cash = DBdata[indxFB]["cash"]
    while code == 0 and cash == 0:
        DBdata = database.get("/restaurants/" + estName, "orders")
        code = DBdata[indxFB]["paid"]
        cash = DBdata[indxFB]["cash"]
        if (code == 1):
            break
    return "found"



def translateOrder(msg, indxFB):
    DBdata = database.get("/restaurants/" + estName, "orders")
    userOrder = msg
    print(msg)
    removelex = ["without", "no", "remove", "take out", "w/o", "take off"]
    addlex = ["with", "add", "more", "w/", "include"]
    userOrder = userOrder.lower()
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
        if (score < 80):
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
            itemStr = (str(quantity) + "x " + str(nameMatch) + " ")
        if (float(data['items'][indx]['sizes'][sizeIndx][1]) > 0):
            if (sizeMatch != "u"):
                itemIndxs.append([(str(sizeMatch) + " " + str(nameMatch)), indx, sizeIndx])
            else:
                itemIndxs.append([(str(nameMatch)), indx, sizeIndx])
            price += float(data['items'][indx]['sizes'][sizeIndx][1])
        elif (float(data['items'][indx]['sizes'][sizeIndx][1]) < 0):
            itemStr = items[item]
            discountFlag = 1
        if (discountFlag == 0 or invalidFlag == 0):
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
                if (pos[cv][1] != "CC" and pos[cv][1] != "IN" and pos[cv][0] != ","):
                    extraStr = ""
                    extraStr += pos[cv][0]
                    exScore = 0
                    exIndx = 0
                    for xm in range(len(data['items'][indx]['extras'])):
                        # print(pos[cv][0], pos[cv][1])
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
                    if (extraFind.find("-") != -1):
                        cv += 1
                    itemStr += "add "
                    itemStr += str((data['items'][indx]["extras"][exIndx][0])).lower()
                    itemStr += " "
                    price += float(data['items'][indx]["extras"][exIndx][1])
                cv += 1

        if (invalidFlag == 0 and discountFlag == 0):
            itemStr = itemStr[:-1]
            subtotal += (quantity * price)
            order += str(itemStr + " $" + str(price) + " x " + str(quantity) + "\n")
        elif (discountFlag == 1):
            discScore = 0
            disIndx = 0
            for it in range(len(itemIndxs)):
                newScore = (fuzz.token_sort_ratio(itemIndxs[it][0], (data['items'][indx]["extras"][0][0])))
                if (newScore > discScore):
                    discScore = newScore
                    disIndx = it
                if (newScore == discScore):
                    newScore = (fuzz.ratio(itemIndxs[it][0], (data['items'][indx]["extras"][0][0])))
                    if (newScore > discScore):
                        discScore = newScore
                        disIndx = it
            if (discScore > 90):
                discAmt = data['items'][indx]["extras"][0][1]
                if (type(discAmt) == str):
                    discAmt = discAmt[:-1]
                    discAmt = float(discAmt)
                    discTotal = (
                                data['items'][itemIndxs[disIndx][1]]["sizes"][itemIndxs[disIndx][2]][1] * (1 - discAmt))
                    subtotal -= discTotal
                elif (type(discAmt) == float):
                    # print(data['items'][itemIndxs[disIndx][1]]["sizes"][itemIndxs[disIndx][2]][1])
                    discTotal = (discAmt)
                    subtotal -= discAmt
                order += items[item] + (' -${0}'.format(format(discTotal, ',.2f')))
                order += "\n"
            else:
                order += "invalid coupon \n"
        else:
            order += "invalid item \n"

    subtotal += 0.20
    fee = 0.2
    order += ('processing. fee ${0}'.format(format(fee, ',.2f'))) + "\n"
    order += ('subtotal ${0}'.format(format(subtotal, ',.2f'))) + "\n"
    tax = subtotal * 0.1
    order += ('tax ${0}'.format(format(tax, ',.2f'))) + "\n"
    total = subtotal + tax
    order += ('total ${0}'.format(format(total, ',.2f')))
    print(order)
    database.put("/restaurants/" + estName + "/orders/" + str(indxFB) + "/", "total/", total)
    usrIndx = DBdata[indxFB]["userIndx"]
    numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
    database.put("/users/",
                 "/" + str(usrIndx) + "/restaurants/" + estName + "/" + str((len(numOrders) - 1)) + "/total",
                 str(total))

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
    DBdata = database.get("/restaurants/" + estName, "orders")
    UserData = database.get("/", "users")
    if (msg == "order" or msg == "ordew" or msg == "ord" or msg == "ordet" or msg == "oderr" or msg == "ordee"):
        UUID = random.randint(9999, 100000)
        reply = "Hi welcome to " + estName + " please enter your name to continue"
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/UUID/", str(UUID))
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/name/", "")
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/number/", str(number))
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/unprocessedOrder/", "")
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/stage/", 1)
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/paid/", 0)
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/cash/", 0)
        UserData = database.get("/", "users")
        for usr in range(len(UserData)):
            if (number == UserData[usr]["number"]):
                print("found user")
                timeStamp = datetime.datetime.today()
                reply = "Hi " + str(UserData[usr]["name"]) + "! welcome to " + estName + " is this order for here to go"
                database.put("/restaurants/" + estName + "/orders/" + str((len(DBdata))) + "/", "/name/",
                             str(UserData[usr]["name"]))
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/stage/", 2)
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/userIndx/", usr)
                numOrders = database.get("/users/" + str(usr) + "/restaurants/", estName)
                loyaltyCard = numOrders[0]["loyaltyCard"]
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/loyaltyCard/",
                             "Loyalty Card")
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/orderIndx/",
                             (len(numOrders)))
                database.put("/users/",
                             "/" + str(usr) + "/restaurants/" + estName + "/" + str((len(numOrders))) + "/Starttime",
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
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/togo/", "for here")
                usrIndx = DBdata[indx]["userIndx"]
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
                print((len(numOrders)))
                database.put("/users/",
                             "/" + str(usrIndx) + "/restaurants/" + estName + "/" + str(
                                 (len(numOrders) - 1)) + "/to-go",
                             str("here"))

                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': "Sounds good! your order will be " + "for-here\n" + "if you want"
                                                                                " your order now enter" + ' "asap" otherwise enter the time your preferred time.(EX 11:15am)'
                })
            else:
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/togo/", "to-go")
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 3)
                usrIndx = DBdata[indx]["userIndx"]
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
                database.put("/users/",
                             "/" + str(usrIndx) + "/restaurants/" + estName + "/" + str(
                                 (len(numOrders) - 1)) + "/to-go",
                             str("to-go"))
                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': "Sounds good! your order will be " + "to-go\n" + "if you want"
                                                                             " your order now enter " + '"asap" otherwise enter the time your preferred time.(EX 11:15am)'
                })
        elif (DBdata[indx]['stage'] == 3):
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/orderTime/", msg)
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 4)
            usrIndx = DBdata[indx]["userIndx"]
            numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
            database.put("/users/",
                         "/" + str(usrIndx) + "/restaurants/" + estName + "/" + str(
                             (len(numOrders) - 1)) + "/pickup-time",
                         str(msg))
            reply = "Got it!, you can " \
                    "view the menu here " + link + " first enter your items and then promo-codes," \
                                                   " one by one in DIFFERENT TEXTS " \
                                                   "Enter " + '"DONE" when finished'

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
                    msgData += "."
                else:
                    msgData += str(msg)
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/unprocessedOrder/", msgData)
                return
        elif (DBdata[indx]['stage'] == 5):
            if (msg == "ok"):
                timeStamp = datetime.datetime.today()
                usrIndx = DBdata[indx]["userIndx"]
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
                database.put("/users/",
                             "/" + str(usrIndx) + "/restaurants/" + estName + "/" + str(
                                 (len(numOrders) - 1)) + "/EndTime",
                             timeStamp)
                total = DBdata[indx]['total']
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
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
                loyaltyCard = numOrders[0]["loyaltyCard"]
                cash = DBdata[indx]["cash"]
                if (cash != 1):
                    if (loyaltyCard == 0):
                        client.send_message({
                            'from': NexmoNumber,
                            'to': number,
                            'text': "your order has been processed and will be ready shortly, thank you!\n would you like to be registered you for a loyalty card?"
                        })
                    else:
                        database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/loyaltyCard/", "Yes")
                        client.send_message({
                            'from': NexmoNumber,
                            'to': number,
                            'text': "your order has been processed and will be ready shortly! we've added points to your loyalty card"
                        })
                    usrIndx = DBdata[indx]["userIndx"]
                    numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
                    logOrder(indx, number)
                    database.put("/users/",
                                 "/" + str(usrIndx) + "/restaurants/" + estName + "/" + str(
                                     (len(numOrders) - 1)) + "/paymentMethod",
                                 "card")

                return reply

            elif (msg == "help"):
                reply = "Sorry about that, please try re-entering your items, please text me items in this format\n " + "" \
                                                                                                                        ' "Quantity, Item Name, toppings to add, "no" toppings to remove"'
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
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/cash/", 1)
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/paid/", 0)
                usrIndx = DBdata[indx]["userIndx"]
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
                database.put("/users/",
                             "/" + str(usrIndx) + "/restaurants/" + estName + "/" + str(
                                 (len(numOrders) - 1)) + "/paymentMethod",
                             "cash")
                reply = "No problem! enjoy your order, the staff will take your cash payment when you pick up your order"
                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': reply
                })
                logOrder(indx,number)
            elif ((msg == "ok" or msg == "yes" or msg == "sure" or msg == "ye" or msg == "yep" or msg == "yup"
                   or msg == "i do" or msg == "y" or msg == "i do want one" or msg == "yeah" or msg == "yea" or msg == "alright") and
                  DBdata[indx]['paid'] == 1):
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/loyaltyCard/", "sign-up")
                usrIndx = DBdata[indx]["userIndx"]
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
                database.put("/users/",
                             "/" + str(usrIndx) + "/restaurants/" + estName + "/" + str(
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
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/loyaltyCard/", "none")
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
        if(DBdata[dbItems]["UUID"] == rsp["item_name"]):
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/paid/", 1)
            usrIndx = DBdata[dbItems]["userIndx"]
            numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
            database.put("/users/","/" + str(usrIndx) + "/restaurants/" + estName + "/" + str((len(numOrders) - 1)) + "/totalPaid",rsp["mc_gross"])
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
                database.put("/log/" + estName + "/" + str(logDate), "/paypalFees/", (float(rsp["mc_fee"]) + currentacct))
            else:
                database.put("/log/" + estName + "/" + str(logDate), "/paypalFees/", float(rsp["mc_fee"]))
    return (" ", 200)


# when you run the code through terminal, this will allow Flask to work
if __name__ == '__main__':
    app.run(port=5000)
