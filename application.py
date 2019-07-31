from flask import Flask, request
import nexmo
from firebase import firebase
import datetime
import json
import nltk
from fuzzywuzzy import fuzz
from words2num import w2n
import easyimap

with open('menu.json') as data_file:
    data = json.load(data_file)

foodItems = (data['items'])
items = []
login = "payments@cedarrobots.com"
password = "CedarPayments1!"

client = nexmo.Client(key='8558cb90', secret='PeRbp1ciHeqS8sDI')

NexmoNumber = '13166009096'
databse = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
estName = "NAME"
link = "LINK"

app = Flask(__name__)

def verifyPayment(name,time,date,month,year):
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
        for payments in range(len(addressArr))

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
                    cv += 2
                itemStr += "add "
                itemStr += str((data['items'][indx]["extras"][exIndx][0])).lower()
                # print(len(data['items'][indx]["extras"][exIndx][0]))
                # print(itemStr)
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
    order += ('total ${0}'.format(format(total, ',.2f')))
    print(order)
    databse.put("/tickets/" + str(FBtoken), "/processedOrder/", orderFin)
    databse.put("/tickets/" + str(FBtoken), "/subTotal/", subtotal)
    databse.put("/tickets/" + str(FBtoken), "/total/", total)
    return order

def logOrder(tix,number):
    logDate = (datetime.datetime.now().strftime("%Y-%m"))
    currentVal = databse.get("/log/" + str(logDate) + "/", "orders")
    currentacct = databse.get("/log/" + str(logDate) + "/", "acct")
    databse.put("/log/" + str(logDate), "/orders/", (currentVal + 1))
    databse.put("/log/" + str(logDate), "/acct/", (currentacct + 0.20))
    databse.put("/tickets/" + str(tix), "/number/", str(number) + ".")


def genPayment(total,name):
    paymentLink = 'https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=alan.john@cedarrobots.com&currency_code=USD&amount=' \
                  '' + str(total) + '&return=http://cedarrobots.com&item_name=' + str(name)
    return paymentLink
# Main method. When a POST request is sent to our local host through Ngrok
# (which creates a tunnel to the web), this code will run. The Twilio service # sends the POST request - we will set this up on the Twilio website. So when # a message is sent over SMS to our Twilio number, this code will run
def getReply(msg,number):
    if()
    return reply

@app.route('/sms', methods=['GET', 'POST'])
def inbound_sms():
    data = dict(request.form) or dict(request.args)
    print(data["text"])
    number = str(data['msisdn'][0])
    msg = str(data["text"][0])
    print(number,msg)
    response = getReply(msg,number)

    client.send_message({
        'from': NexmoNumber,
        'to': number,
        'text': response
    })


    return ('', 200)

# when you run the code through terminal, this will allow Flask to work
if __name__ == '__main__':
    app.run(port=3000,debug=True)