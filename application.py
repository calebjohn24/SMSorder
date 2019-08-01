import datetime
import json
import time
import easyimap
import nexmo
import nltk
from firebase import firebase
from flask import Flask, request
from fuzzywuzzy import fuzz
from words2num import w2n
import random

database = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
with open('menu.json') as data_file:
    data = json.load(data_file)

foodItems = (data['items'])
items = []
login = "payments@cedarrobots.com"
password = "CedarPayments1!"

client = nexmo.Client(key='8558cb90', secret='PeRbp1ciHeqS8sDI')

NexmoNumber = '13166009096'
databse = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
estName = "TestRaunt"
link = "LINK"

app = Flask(__name__)


def verifyPayment(UUIDcode,indxFB):
    DBdata = database.get("/restaurants/" + estName, "orders")
    code = DBdata[indxFB]["paid"]
    UUIDflag = 0
    while(UUIDflag == 0 and code != 1):
        DBdata = database.get("/restaurants/" + estName, "orders")
        code = DBdata[indxFB]["cash"]
        nameArr = []
        addressArr = []
        emailArr = []
        dateTimeArr = []
        imapper = easyimap.connect('imappro.zoho.com', login, password)
        for mail_id in imapper.listids(limit=100):
            mail = imapper.mail(mail_id)
            nameSTR = (mail.from_addr).lower()
            nameEnd = nameSTR.find("via") - 1
            name = nameSTR[0:nameEnd]
            nameArr.append(name)
            emailSTR = mail.title
            emailEnd = emailSTR.find("from") + 5
            email = emailSTR[emailEnd::]
            emailArr.append(email)
            dateTimeSTR = mail.date
            dateTimeZoneEnd = dateTimeSTR.find("-")
            timeZone = dateTimeSTR[dateTimeZoneEnd::]
            dateTimeDayEnd = dateTimeSTR.find(",")
            day = dateTimeSTR[0:dateTimeDayEnd]
            timeEnd = dateTimeSTR.find(":")
            time = dateTimeSTR[(timeEnd - 2):(timeEnd + 6)]
            year = dateTimeSTR[(timeEnd - 7):(timeEnd - 3)]
            month = dateTimeSTR[(timeEnd - 11):(timeEnd - 8)]
            date = dateTimeSTR[(timeEnd - 14):(timeEnd - 12)]
            dateTimeArr.append(
                [["timezone", timeZone], ["day", day], ["time", time], ["year", year], ["month", month], ["date", date]])
            bodyText = (mail.body)
            bodyText = bodyText.lower()
            ship = (bodyText.find("shipping information"))
            shipEnd = (bodyText.find("end -->"))
            shippingInfo = (bodyText[ship:shipEnd])
            UUID = (bodyText[(bodyText.find("uuid") + 5): ((bodyText.find("uuid")) + 9)])
            shippingInfo = shippingInfo.replace("<", "")
            shippingInfo = shippingInfo.replace("/", "")
            shippingInfo = shippingInfo.replace(">", "")
            shippingInfo = shippingInfo.replace('style="display:inline;"', "")
            shippingInfo = shippingInfo.replace("br", "")
            shippingInfo = shippingInfo.replace("span", "")
            shippingInfo = shippingInfo.replace('style="display: inline;"', "")
            shippingInfo = shippingInfo.replace("-- addressdisplaywrapper : start --  ", "")
            shippingInfo = shippingInfo.replace("!", "")
            shippingInfo = shippingInfo.replace("-", "")
            shippingInfo = shippingInfo.replace("addressdisplaywrapper", "")
            addrBegin = shippingInfo.find(name) + (len(name)) + 3
            shippingInfo = (shippingInfo[addrBegin::])
            commaSplicer = shippingInfo.find(",")
            state = shippingInfo[(commaSplicer + 5): (commaSplicer + 7)]
            zipCode = shippingInfo[(commaSplicer + 11):(commaSplicer + 16)]
            addrEnd = shippingInfo.find("  ")
            streetAdr = (shippingInfo[0:addrEnd])
            city = shippingInfo[(addrEnd + 3):(commaSplicer - 3)]
            addressArr.append([["state", state], ["zipCode", zipCode], ["city", city], ["streetAdr", streetAdr]])
            # for payments in range(len(addressArr))
            if(UUID == UUIDcode):
                print("order found")
                database.put("/restaurants/" + estName + "/orders/" + str(indxFB) + "/", "/paid/", 1)
                UUIDflag = 1
                break
    return "found"



def translateOrder(msg,indxFB):
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

    subtotal += 0.20
    fee = 0.2
    order += ('subtotal ${0}'.format(format(subtotal, ',.2f'))) + "\n"
    tax = subtotal * 0.1
    order += ('tax ${0}'.format(format(tax, ',.2f'))) + "\n"
    total = subtotal + tax
    order += ('proces. fee ${0}'.format(format(fee, ',.2f'))) + "\n"
    order += ('total ${0}'.format(format(total, ',.2f'))) + "\n"
    print(order)
    order += 'if everything looks good enter "ok" otherwise enter "help" \n'
    total = 0.01 #delete line
    database.put("/restaurants/" + estName + "/orders/" + str(indxFB) + "/", "total/", total)
    return order


def logOrder(tix, number):
    logDate = (datetime.datetime.now().strftime("%Y-%m"))
    currentVal = databse.get("/log/" + estName + "/" + str(logDate) + "/", "orders")
    currentacct = databse.get("/log/" + estName + "/" + str(logDate) + "/", "acct")
    databse.put("/log/"+ estName + "/" + str(logDate), "/orders/", (currentVal + 1))
    databse.put("/log/" +estName+"/"+ str(logDate), "/acct/", (currentacct + 0.20))
    database.put("/restaurants/" + estName + "/orders/" + str(tix) + "/", "/number/", str(number)+".")


def genPayment(total, name, UUIDcode):
    print(UUIDcode)
    paymentLink = 'https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=alan.john@cedarrobots.com&currency_code=USD&amount=' \
                  '' + str(total) + '&return=http://cedarrobots.com&item_name=' + str(name) + "-UUID-"+str(UUIDcode)
    return paymentLink


def getReply(msg, number):
    msg = msg.lower()
    indx = 0
    usrIndx = 0
    DBdata = database.get("/restaurants/" + estName, "orders")
    UserData = database.get("/", "users")
    if (msg == "order" or msg == "ordew" or msg == "ord" or msg == "ordet" or msg == "oderr"):
        UUID = random.randint(999, 10000)
        reply = "Hi welcome to " + estName + " please enter your name to continue"
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/UUID/", str(UUID))
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/name/", "")
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/number/", str(number))
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/unprocessedOrder/", "")
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/stage/", 1)
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/paid/", 0)
        database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/cash/", 0)

        client.send_message({
            'from': NexmoNumber,
            'to': number,
            'text': reply
        })
        return reply
    for db in range(len(DBdata)):
        phoneNumDB = DBdata[db]['number']
        if (phoneNumDB == number):
            indx = db
            break
    if(DBdata[indx]['stage'] == 1):
        database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/name/", str(msg))
        database.put("/users/", "/" + str(len(UserData)-1) + "/name/", str(msg))
        database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 2)
        reply = "Hi, " + str(msg).capitalize() + " is this order for-here or to-go?"
        client.send_message({
            'from': NexmoNumber,
            'to': number,
            'text': reply
        })
    elif(DBdata[indx]['stage'] == 2):
        if(msg == "for here" or msg == "fo here" or msg == "for her" or msg == "for herw" or msg == "for herr" or msg == "here"):
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 3)
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/togo/", 0)
            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': "Sounds good! your order will be " + "for-here\n" + " Do you have a loyalty card?"
            })
        else:
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/togo/", 1)
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 3)
            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': "Sounds good! your order will be "+ "to-go\n"+"Do you have a loyalty card?"
            })
    elif (DBdata[indx]['stage'] == 3):
        if(msg == "yes" or msg == "yep" or msg == "yup" or msg == "y" or msg == "ye" or msg == "i do"):
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/loyaltyCard/", 1)
        else:
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/loyaltyCard/", 0)
        database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 4)
        reply = "Got it!, you can " \
                                                 "view the menu here " + link + " please " \
                                                 "enter you order now \n" + "text us items " \
                                                 "one by one in different texts like this"

        client.send_message({
            'from': NexmoNumber,
            'to': number,
            'text': reply
        })
        print("m0")
        time.sleep(0.25)
        print("m1")
        client.send_message({
            'from': NexmoNumber,
            'to': number,
            'text': "Burger with bacon and cheese, no avacado"
        })
        time.sleep(0.75)
        print("m2")
        client.send_message({
            'from': NexmoNumber,
            'to': number,
            'text': "3 large Coffees with cream, no sugar \n" + "enter " +'"done"'+" once you're finished"
        })
        print("m3")
        time.sleep(0.5)
        return reply

    elif (DBdata[indx]['stage'] == 4):
        if(msg == "done"):
            database.get("/restaurants/" + estName + "/orders/" + str(indx) + "/",
                         "unprocessedOrder")
            reply = translateOrder(DBdata[indx]['unprocessedOrder'],indx)
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
            if(msg[-1] != "."):
                msgData += str(msg)
                msgData += "."
            else:
                msgData += str(msg)
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/unprocessedOrder/", msgData)
            return
    elif (DBdata[indx]['stage'] == 5):
        if(msg == "ok"):
            total = DBdata[indx]['total']
            UUID =  DBdata[indx]['UUID']
            name = DBdata[indx]['name']
            reply = 'thanks, please click the link below to pay if you want to pay cash enter "cash"\n ' \
                    ""+ genPayment(total,name,UUID)
            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': reply
            })
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 6)
            verifyPayment(UUID,indx)
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/paid/", 1)
            loyaltyCard = DBdata[indx]["loyaltyCard"]
            cash = DBdata[indx]["cash"]
            if(cash != 1):
                if(loyaltyCard == 0):
                    client.send_message({
                        'from': NexmoNumber,
                        'to': number,
                        'text': "your order has been processed and will be ready shortly, thank you!\n would you like to be registered you for a loyalty card?"
                    })
                else:
                    client.send_message({
                        'from': NexmoNumber,
                        'to': number,
                        'text': "your order has been processed and will be ready shortly!"
                    })
                    logOrder(indx,number)
            return reply

        elif(msg == "help"):
            reply = "Sorry about that, please try re-entering your items, please text me items in this format\n "+ "" \
                    ' "Quantity, Item Name, toppings to add, "no" toppings to remove"'
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/unprocessedOrder/", "")
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 4)
            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': reply
            })
            return reply
    elif(DBdata[indx]['stage'] == 6):
        if(msg == "cash"):
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/cash/", 1)
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/paid/", 1)
            reply = "No problem! enjoy your order, the staff will take your cash payment when you pick up your order"
            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': reply
            })
        elif(msg == "ok" or msg == "yes" or msg == "ye" or msg == "yep" or msg =="yup"or msg =="i do"or msg == "y"or msg == "i do want one"):
            database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/loyaltyCard/", 2)
            reply = "Thanks! we'll sign you up, enjoy your order"
            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': reply
            })
        else:
            reply = "No problem! enjoy your order, the staff will take your cash payment when you pick up your order"
            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': reply
            })
        logOrder(indx,number)
        return reply


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