from flask import Flask, request
from twilio.twiml.messaging_response import Message, MessagingResponse
import twilio
from firebase import firebase
import time
import nltk
import json
import datetime
from fuzzywuzzy import fuzz
from words2num import w2n

SendNum = "+14253828604"

databse = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
estName = "NAME"
link = "LINK"
with open('menu.json') as data_file:
    data = json.load(data_file)
foodItems = (data['items'])
# set up Flask to connect this code to the local host, which will
# later be connected to the internet through Ngrok
app = Flask(__name__)

def transalteOrder(msg, FBtoken):

    userOrder = msg
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
        for cv in range(len(pos) - 1):
            if (pos[cv][1] != "CC" and pos[cv][1] != "IN"):
                extraStr = ""
                extraStr += pos[cv][0]
                exScore = 0
                exIndx = 0
                for xm in range(len(data['items'][indx]['extras'])):
                    newScore = (fuzz.token_sort_ratio(data['items'][indx]["extras"][xm], extraStr))
                    if (newScore > exScore):
                        exScore = newScore
                        exIndx = xm
                    if (newScore == exScore):
                        newScore = (fuzz.ratio(data['items'][indx]["extras"][xm], extraStr))
                        if (newScore > exScore):
                            score = newScore
                            exIndx = xm
                itemStr += "add "
                itemStr += str((data['items'][indx]["extras"][exIndx][0])).lower()
                itemStr += " "
                price += float(data['items'][indx]["extras"][exIndx][1])

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
    order += ('total ${0}'.format(format(total, ',.2f')))
    print(order)
    return order

def logOrder(tix,number):
    logDate = (datetime.datetime.now().strftime("%Y-%m"))
    currentVal = databse.get("/log/" + str(logDate) + "/", "orders")
    currentacct = databse.get("/log/" + str(logDate) + "/", "acct")
    databse.put("/log/" + str(logDate), "/orders/", (currentVal + 1))
    databse.put("/log/" + str(logDate), "/acct/", (currentacct + 0.20))
    databse.put("/tickets/" + str(tix), "/number/", str(number) + ".")


def assignRobot(tableNum):
    print(tableNum)
def genPayment(total):
    print(total)
    return ("dummy link")
# Main method. When a POST request is sent to our local host through Ngrok
# (which creates a tunnel to the web), this code will run. The Twilio service # sends the POST request - we will set this up on the Twilio website. So when # a message is sent over SMS to our Twilio number, this code will run
def getReply(msg,number):
    if(msg == "ORDER" or msg == "ORDR" or msg == "ODER"):
        response = "Welcome to " + estName + " you can view the menu here " + link + \
                   " | to order please seperate Items with a period. like this '" \
                   "3 12 oz Iced Coffees with Cream and sugar. Burger with Bacon.' " \
                   "Don't forget to mention sizes!"
        tickNum = databse.get("/", "tickets")
        databse.put("/tickets/" + str(len(tickNum)), "/stage/", 1)
        databse.put("/tickets/" + str(len(tickNum)), "/time/", (int(time.time())))
        databse.put("/tickets/" + str(len(tickNum)), "/number/", number)
        return response
    else:
        tickNum = databse.get("/", "tickets")
        for tix in range(len(tickNum)):
            if(tickNum[tix]["number"] == number):
                stage = tickNum[tix]["stage"]
                if(stage == 1):
                    transalteOrder(msg, tix)
                    respStr = "Got it! Is this order for here or to-go"
                    databse.put("/tickets/" + str(tix), "/stage/", 2)
                    return respStr
                elif(stage == 2):
                    total = tickNum[tix]["total"]
                    if(msg == "FOR HERE" or msg == "FO HERE" or msg == "HERE" or msg == "FOR ERE"):
                        respStr = "Thank you for your order, what's the number of the table you are sitting at?"
                        databse.put("/tickets/" + str(tix), "/togo/", 0)
                        databse.put("/tickets/" + str(tix), "/stage/", 3)
                    elif(msg == "TO GO" or msg == "TOGO" or msg == "TO-GO" or msg == ""):
                        respStr = "Thank you for your order enter 'R' to review your order and pay"
                        databse.put("/tickets/" + str(tix), "/togo/", 1)
                        databse.put("/tickets/" + str(tix), "/stage/", 4)
                    else:
                        rpStr = str(tickNum[tix]["processedOrder"])
                        respStr = "Thank you for your order" \
                        "enter 'r' to review your order and pay"
                        databse.put("/tickets/" + str(tix), "/togo/", 1)
                        databse.put("/tickets/" + str(tix), "/stage/", 4)
                    return respStr
                elif(stage == 3):
                    try:
                        rpStr = str(tickNum[tix]["processedOrder"])
                        int(msg)
                        tableNum = int(msg)
                        respStr = "thank you you food will arrive soon enter 'r' to review your order and pay"
                        databse.put("/tickets/" + str(tix), "/stage/", 4)
                        databse.put("/tickets/" + str(tix), "/tableNum/", tableNum)
                        assignRobot(tableNum)
                    except ValueError:
                        respStr = "please enter a number ex. '18'"
                    return respStr
                elif(stage == 4):
                    rpStr = str(tickNum[tix]["processedOrder"])
                    #rpStr = "test"
                    logOrder(tix, number)
                    databse.put("/tickets/" + str(tix), "/pay/", 0)
                    return rpStr

@app.route('/', methods=['POST'])
def sms():
    # Get the text in the message sent
    number = request.form['From']
    message_body = request.form['Body']
    message_body = str(message_body).upper()
    resp = MessagingResponse()
    # Text back our response!
    reply = getReply(message_body,number)
    resp.message(reply)
    print(reply)
    return str(resp)

# when you run the code through terminal, this will allow Flask to work
if __name__ == '__main__':
    app.run(debug=True)