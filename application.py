import datetime
import json
import random
import time
from bs4 import BeautifulSoup
import uszipcode
import easyimap
import nexmo
import nltk
from firebase import firebase
from flask import Flask, request
from fuzzywuzzy import fuzz
from words2num import w2n

database = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
with open('menu.json') as data_file:
    data = json.load(data_file)

foodItems = (data['items'])
items = []
login = "payments@cedarrobots.com"
password = "CedarPayments1!"

promoPass = "asnifnr10002"

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
    database.put("/users/", "/" + str(len(UserData)) + "/restaurants/" + estName + "/" + str(0) + "/time",
                 str(timeStamp))
    database.put("/users/","/" + str(len(UserData)) + "/restaurants/" + estName + "/" + str(0) + "/loyaltyCard",0)



def verifyPayment(UUIDcode, indxFB, usrIndx):
    DBdata = database.get("/restaurants/" + estName, "orders")
    code = DBdata[indxFB]["paid"]
    UUIDflag = 0
    while (UUIDflag == 0 and code != 1):
        DBdata = database.get("/restaurants/" + estName, "orders")
        code = DBdata[indxFB]["cash"]
        imapper = easyimap.connect('imappro.zoho.com', login, password)
        for mail_id in imapper.listids(limit=100):
            mail = imapper.mail(mail_id)
            bodyText = (mail.body)
            bodyText = bodyText.lower()
            UUID = (bodyText[(bodyText.find("uuid") + 5): ((bodyText.find("uuid")) + 9)])
            bodyText = (mail.body)
            soup = BeautifulSoup(bodyText, 'lxml')
            bodyText = (soup.get_text())
            strStart = bodyText.find("Hello")
            bodyText = str(bodyText[strStart:])
            bodyText = bodyText.replace("  ", "")
            bodyText = bodyText.replace("\n", "")
            # print(bodyText)
            emailStart = bodyText.find("(")
            emailEnd = bodyText.find(")")
            email = (bodyText[(emailStart + 1):emailEnd])
            ship = (bodyText.find("Shipping"))
            shipEnd = (bodyText.find("United States"))
            adrText = str(bodyText[ship + (len("shipping")):(shipEnd)])
            adrText = adrText.replace("  ", "")
            adrText = adrText.replace("confirmed", "")
            adrText = adrText.replace(" address -", "")
            adrText = adrText.replace(" information:", "")
            adrText = adrText.rstrip()
            adrText = adrText.lstrip()
            adrText = adrText.upper()
            name = ""
            streetAdrIndx = 0
            for ltr in range(len(adrText)):
                try:
                    testStr = int(adrText[ltr])
                    streetAdrIndx = ltr
                    break
                except ValueError:
                    name += adrText[ltr]
            name = name.upper()
            streetAdrFull = adrText[streetAdrIndx:]
            zipCode = (streetAdrFull[-5:])
            streetAdrCity = (streetAdrFull[:-5])
            search = uszipcode.SearchEngine(simple_zipcode=True)
            zipCitySearch = search.by_zipcode(zipCode).common_city_list
            score = 0
            city = ""
            for cities in range(len(zipCitySearch)):
                newScore = fuzz.partial_ratio(streetAdrCity, str(zipCitySearch[cities]).upper())
                if (newScore > score):
                    score = newScore
                    city = str(zipCitySearch[cities]).upper()
            cityIndx = streetAdrCity.find(city)
            streetAdr = streetAdrCity[:cityIndx]
            print(streetAdr, city, zipCode, name, email)
            if (UUID == UUIDcode):
                print("order found")
                database.put("/restaurants/" + estName + "/orders/" + str(indxFB) + "/", "/paid/", 1)
                database.put("/users/", "/" + str(usrIndx) + "/email", email)
                database.put("/users/", "/" + str(usrIndx) + "/city", city)
                database.put("/users/", "/" + str(usrIndx) + "/zipCode", zipCode)
                database.put("/users/", "/" + str(usrIndx) + "/streedAdr", streetAdr)
                database.put("/users/", "/" + str(usrIndx) + "/legalName", name)
                UUIDflag = 1
                break
    return "found"


def translateOrder(msg, indxFB):
    DBdata = database.get("/restaurants/" + estName, "orders")
    userOrder = msg
    print(msg)
    removelex = ["without", "no", "remove", "take out", "w/o", "take off"]
    addlex = ["with", "add", "more", "w/", "include"]
    userOrder = userOrder.lower()
    userOrder = userOrder.replace('...', '.')
    userOrder = userOrder.replace('..', '.')
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
                            score = newScore
                            exIndx = xm
                extraFind = str(data['items'][indx]["extras"][exIndx])
                if (extraFind.find("-") != -1):
                    cv += 1
                itemStr += "add "
                itemStr += str((data['items'][indx]["extras"][exIndx][0])).lower()
                itemStr += " "
                price += float(data['items'][indx]["extras"][exIndx][1])
            cv += 1

        itemStr = itemStr[:-1]
        subtotal += (quantity * price)
        order += str(itemStr + " $" + str(price) + " x " + str(quantity) + "\n")
    usrIndx = DBdata[indxFB]["userIndx"]
    numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
    database.put("/users/",
                 "/" + str(usrIndx) + "/restaurants/" + estName + "/" + str((len(numOrders) - 1)) + "/processedOrder",
                 str(order))
    subtotal += 0.20
    fee = 0.2
    order += ('subtotal ${0}'.format(format(subtotal, ',.2f'))) + "\n"
    tax = subtotal * 0.1
    order += ('tax ${0}'.format(format(tax, ',.2f'))) + "\n"
    total = subtotal + tax
    order += ('proces. fee ${0}'.format(format(fee, ',.2f'))) + "\n"
    order += ('total ${0}'.format(format(total, ',.2f'))) + "\n"
    print(order)
    order += 'if everything looks good enter "ok" otherwise enter "help"\n'
    total = 0.01  # delete line
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
    paymentLink = 'https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=alan.john@cedarrobots.com&currency_code=USD&amount=' \
                  '' + str(total) + '&return=http://cedarrobots.com&item_name=' + str(name) + "-UUID-" + str(UUIDcode)
    return paymentLink


def getReply(msg, number):
    msg = msg.lower()
    indx = 0
    DBdata = database.get("/restaurants/" + estName, "orders")
    UserData = database.get("/", "users")
    if (msg == "order" or msg == "ordew" or msg == "ord" or msg == "ordet" or msg == "oderr"):
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
                reply = "Hi " + str(UserData[usr]["name"]) + "! welcome to" + estName + " is this order for here to go"
                database.put("/restaurants/" + estName + "/orders/" + str((len(DBdata))) + "/", "/name/", str(UserData[usr]["name"]))
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/stage/", 2)
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/userIndx/", usr)
                numOrders = database.get("/users/" + str(usr) + "/restaurants/", estName)
                loyaltyCard = numOrders[0]["loyaltyCard"]
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/loyaltyCard/", "Loyalty Card")
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/orderIndx/",
                             (len(numOrders)))
                database.put("/users/",
                             "/" + str(usr) + "/restaurants/" + estName + "/" + str((len(numOrders))) + "/time",
                             str(timeStamp))

                break
            if ((len(UserData) - usr) == 1):
                genUsr("", number)
                database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/userIndx/", (len(UserData)))
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
                return 200
        if (DBdata[indx]['stage'] == 1):
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/name/", str(msg).capitalize())
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 2)
            reply = "Hi, " + str(msg).capitalize() + " is this order for-here or to-go?"
            usrIndx = DBdata[indx]["userIndx"]
            database.put("/users", "/" + str(usrIndx) + "/name" ,str(msg.capitalize()))
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
                    "view the menu here " + link + " please " \
                                                   "enter you order now " + "text us items " \
                                                                              "one by one in Different Texts like this, " \
                                                                              "you can also enter any promo codes at this time"

            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': reply
            })
            print("m0")
            time.sleep(0.5)
            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': 'Quantity, Item Name, toppings add, "no" toppings to remove'
            })
            time.sleep(0.5)
            print("jk")
            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': 'text "done" once your finished'
            })
            time.sleep(0.5)
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
                total = DBdata[indx]['total']
                UUID = DBdata[indx]['UUID']
                name = DBdata[indx]['name']
                reply = 'thanks, please click the link below to pay if you want to pay cash enter "cash"\n ' \
                        "" + genPayment(total, name, UUID)
                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': reply
                })
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 6)
                DBdata = database.get("/restaurants/" + estName, "orders")
                usrIndx = DBdata[indx]["userIndx"]
                verifyPayment(UUID, indx, usrIndx)
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/paid/", 1)
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
                loyaltyCard = numOrders[0]["loyaltyCard"]
                cash = DBdata[indx]["cash"]
                if (cash != 1):
                    if (loyaltyCard == 1):
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
                        logOrder(indx, number)
                    usrIndx = DBdata[indx]["userIndx"]
                    numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estName)
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
            elif (
                    msg == "ok" or msg == "yes" or msg == "sure" or msg == "ye" or msg == "yep" or msg == "yup"
                    or msg == "i do" or msg == "y" or msg == "i do want one" or msg == "yeah" or msg == "yea"):
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
            return 0



@app.route('/sms', methods=['GET', 'POST'])
def inbound_sms():
    data = dict(request.form) or dict(request.args)
    print(data["text"])
    number = str(data['msisdn'][0])
    msg = str(data["text"][0])
    print(number, msg)

    getReply(msg, number)

    return ('', 200)


# when you run the code through terminal, this will allow Flask to work
if __name__ == '__main__':
    app.run(port=5000)
