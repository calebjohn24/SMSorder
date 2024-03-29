import nexmo
import logging
import logging.handlers
from wsgiref.simple_server import make_server
import pygsheets
import pandas as pd
import paypalrestsdk
from firebase import firebase
from flask import Flask, request, redirect, url_for
from werkzeug.datastructures import ImmutableOrderedMultiDict
from flask import render_template
from flask import jsonify, session, sessions
from flask import Flask, escape, request, session
from flask_session import Session
import pyrebase as fbAuth
from fpdf import FPDF
from words2num import w2n
import os
import calendar
import random
import datetime
import json
import time
import urllib.request

sessionTime = 1000
infoFile = open("info.json")
info = json.load(infoFile)
uid = info['uid']
gc = pygsheets.authorize(service_file='static/CedarChatbot-70ec2d781527.json')
email = "cedarchatbot@applicationspot.gserviceaccount.com"
estName = info['uid']
estNameStr = info['name']
shortUID = info['shortUID']
mainLink = ""
authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W', 'cajohn0205@gmail.com',
                                                 extra={'id': 123})
database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
data = (database.get("restaurants/" + uid, "/menu/items/"))
items = []
config = {
    "apiKey": "AIzaSyB2it4zPzPdn_bW9OAglTHUtclidAw307o",
    "authDomain": "cedarchatbot.firebaseapp.com",
    "databaseURL": "https://cedarchatbot.firebaseio.com",
    "storageBucket": "cedarchatbot.appspot.com",
}
firebaseAuth = fbAuth.initialize_app(config)
auth = firebaseAuth.auth()
client = nexmo.Client(key='8558cb90', secret='PeRbp1ciHeqS8sDI')
pointAlg = "x.10"
pointThresh = 1000
NexmoNumber = info['number']
databse = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
promoPass = "promo-" + str(estName)
addPass = "add-" + str(estName)
remPass = "remove-" + str(estName)
fontName = "helvetica"
smsTest = "sms:13166009096?body=order"
sh = gc.open('TestRaunt')
linkOrderLong = "cedarrestaurants.us-east-2.elasticbeanstalk.com" + uid + "check"

webLink = "sms:+" + NexmoNumber + "?body=order"
application = Flask(__name__)


def updateLog():
    logYM = (datetime.datetime.now().strftime("%Y-%m"))
    sh = gc.open('TestRaunt')
    wks = sh.worksheet_by_title(logYM + "-sales")
    logData = database.get("/log/" + uid + "/", logYM)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    numOrders = (len(database.get("/restaurants/" + estName, "/orders/")) - 1)
    totalDF = pd.DataFrame()
    totalArr = []
    cdrFees = logData['CedarFees']
    totalArr.append(cdrFees)
    paypalFees = logData['paypalFees']
    totalArr.append(paypalFees)
    totalFees = cdrFees + paypalFees
    totalArr.append(totalFees)
    totalRev = logData['totalRev']
    totalArr.append(totalRev)
    numOrders = (len(database.get("/restaurants/" + estName, "/orders/")) - 1)
    totalArr.append(numOrders)
    numCard = logData['cardPay']
    totalArr.append(numCard)
    Totals = pd.DataFrame()
    totalDF['Totals'] = totalArr
    wks.set_dataframe(totalDF, (1, 6))
    skuDict = logData['skus']
    skuKeys = list(skuDict.keys())
    SKUkeyArr = []
    SKUrev = []
    SKUnumSold = []
    SKUnames = []
    for sk in range(len(skuKeys)):
        numSold = skuDict[skuKeys[sk]]["numSold"]
        SKUnumSold.append(numSold)
        SKUkeyArr.append(skuKeys[sk])
        for men in range(len(menuItems)):
            if (menuItems[men] != None):
                if ((menuItems[men]["sizes"][0][1] != -1)):
                    for sz in range(len(menuItems[men]["sizes"])):
                        if (skuKeys[sk] == str(menuItems[men]["sizes"][sz][2])):
                            #print("found size")
                            if (str(menuItems[men]["sizes"][sz][0]).lower() != "u"):
                                name = str(menuItems[men]["name"]).lower()
                                name += "-"
                                name += str(menuItems[men]["sizes"][sz][0]).lower()
                                SKUnames.append(name)
                                rev = menuItems[men]["sizes"][sz][1] * numSold
                                SKUrev.append(rev)

                            else:
                                name = str(menuItems[men]["name"]).lower()
                                SKUnames.append(name)
                                rev = menuItems[men]["sizes"][sz][1] * numSold
                                SKUrev.append(rev)
                            break
                        if (len(menuItems[men]["sizes"]) - sz == 1):
                            for ex in range(len(menuItems[men]["extras"])):
                                if (skuKeys[sk] == str(menuItems[men]["extras"][ex][2])):
                                    #print("found ex")
                                    name = str(menuItems[men]["name"]).lower()
                                    name += "||"
                                    name += str(menuItems[men]["extras"][ex][0]).lower()
                                    name += "* TOPPING "
                                    SKUnames.append(name)
                                    rev = float(menuItems[men]["extras"][ex][1]) * float(numSold)
                                    SKUrev.append(rev)
                                    break

    SKUkeysDF = pd.DataFrame()
    SKUnameDF = pd.DataFrame()
    SKUrevDF = pd.DataFrame()
    SKUnumSoldDF = pd.DataFrame()
    SKUkeysDF['SKU'] = SKUkeyArr
    wks.set_dataframe(SKUkeysDF, (1, 1))
    SKUnameDF['Name'] = SKUnames
    wks.set_dataframe(SKUnameDF, (1, 2))
    SKUrevDF["Revenue"] = SKUrev
    wks.set_dataframe(SKUrevDF, (1, 3))
    SKUnumSoldDF["Number Sold"] = SKUnumSold
    wks.set_dataframe(SKUnumSoldDF, (1, 4))


def genUsr(name, number, dbIndx):
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    UserData = database.get("/", "users")
    timeStamp = datetime.datetime.today()
    database.put("/users/", "/" + str(len(UserData)) + "/name", name)
    database.put("/users/", "/" + str(len(UserData)) + "/number", number)
    database.put("/users/", "/" + str(len(UserData)) + "/restaurants/" + estNameStr + "/" + str(0) + "/StartTime",
                 str(timeStamp))
    database.put("/users/", "/" + str(len(UserData)) + "/loyalty/" + str(0) + "/name/", estNameStr)
    database.put("/users/", "/" + str(len(UserData)) + "/loyalty/" + str(0) + "/points/", 0)
    database.put("/restaurants/" + estName + "/orders/" + str(dbIndx) + "/", "/usrIndx/", len(UserData))


def genPayment(total, name, UUIDcode):
    #print(UUIDcode)
    #print(name)
    apiurl = "http://tinyurl.com/api-create.php?url="
    paymentLink = 'https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_xclick&business=sb-ninhv43009@business.example.com&currency_code=USD&amount=' \
                  '' + str(total) + '&item_name=' + str(UUIDcode)
    tinyurl = urllib.request.urlopen(apiurl + paymentLink).read()
    shortLink = tinyurl.decode("utf-8")
    return paymentLink


def getReply(msg, number):
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    currentTime = str((float(datetime.datetime.now().hour)) + ((float(datetime.datetime.now().minute)) / 100.0))
    startHr = float(database.get("restaurants/" + uid, "/OChrs/open/"))
    endHr = float(database.get("restaurants/" + uid, "/OChrs/close/"))
    if (startHr <= float(currentTime) < endHr):
        msg = msg.lower()
        indx = 0
        DBdata = database.get("/restaurants/" + estName, "/orders")
        UserData = database.get("/", "users")
        if (msg == "order" or msg == "ordew" or msg == "ord" or msg == "ordet" or msg == "oderr" or msg == "ordee"):
            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': "Hi! Welcome to " + estNameStr + ", please wait one moment..."
            })
            UUID = random.randint(9999999, 100000000)
            reply = "Hi, welcome to " + estNameStr + " please enter your name to continue"
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/UUID/", str(UUID))
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/name/", "")
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/number/", str(number))
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/stage/", 1)
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/paid/", 0)
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/cash/", "")
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/togo/", "")
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/tickSize/", 0)
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/discUsed/", 0)
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/discTotal/", 0.0)
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/discStr/", "")
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/filled/", "0")
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/linkTotal/", 0.0)
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "finalOrder/", "")
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "startTime/", time.time())
            UserData = database.get("/", "users")
            for usr in range(len(UserData)):
                if (number == UserData[usr]["number"]):
                    #print("found user")
                    timeStamp = datetime.datetime.today()
                    reply = "Hi " + str(
                        UserData[usr]["name"]) + "! welcome to " + estNameStr + " is this order or to go?"
                    database.put("/restaurants/" + estName + "/orders/" + str((len(DBdata))) + "/", "/name/",
                                 str(UserData[usr]["name"]))
                    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/filled/", "0")

                    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/stage/", 2)
                    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/userIndx/", usr)
                    numOrders = database.get("/users/" + str(usr) + "/restaurants/", estNameStr)
                    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/orderIndx/",
                                 (len(numOrders)))
                    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "startTime/",
                                 time.time())
                    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/ret/", 0)
                    database.put("/users/",
                                 "/" + str(usr) + "/restaurants/" + estNameStr + "/" + str(
                                     (len(numOrders))) + "/startTime",
                                 str(timeStamp))
                    break
                if ((len(UserData) - usr) == 1):
                    genUsr("", number, (len(DBdata)))
                    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/userIndx/",
                                 (len(UserData)))
                    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/orderIndx/",
                                 0)
                    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/ret/", 1)
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
                    #print("no msg")
                    return 200
            if (DBdata[indx]['stage'] == 1):
                name = msg
                DBdata = database.get("/restaurants/" + estName, "/orders")
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/name/", str(msg).capitalize())
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 2)
                UserData = database.get("/", "users")
                timeStamp = datetime.datetime.today()
                database.put("/users/", "/" + str(DBdata[indx]["userIndx"]) + "/name", name)
                database.put("/users/", "/" + str(DBdata[indx]["userIndx"]) + "/number", number)
                database.put("/users/",
                             "/" + str(DBdata[indx]["userIndx"]) + "/restaurants/" + estNameStr + "/" + str(
                                 0) + "/StartTime",
                             str(timeStamp))
                database.put("/users/", "/" + str((DBdata[indx]["userIndx"])) + "/loyalty/" + estNameStr + "/points/",
                             0)
                reply = "is this order for-here or to-go?"
                usrIndx = DBdata[indx]["userIndx"]
                database.put("/users", "/" + str(DBdata[indx]["userIndx"]) + "/name", str(msg.capitalize()))
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
                    #print((len(numOrders)))
                    database.put("/users/",
                                 "/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                                     (len(numOrders) - 1)) + "/to-go",
                                 str("here"))

                    client.send_message({
                        'from': NexmoNumber,
                        'to': number,
                        'text': "-Sounds good! your order will be " + "for-here\n" + "-if you want"
                                                                                     " your order now enter" + ' "asap" otherwise enter your preferred time.(EX 11:15am)'
                    })
                else:
                    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                                     'cajohn0205@gmail.com', extra={'id': 123})
                    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/",
                                                            authentication=authentication)
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
                        'text': "-Sounds good! your order will be " + "to-go\n" + "-if you want"
                                                                                  " your order now enter " + '"asap" otherwise enter the time your preferred time.(EX 11:15am)'
                    })
            elif (DBdata[indx]['stage'] == 3):
                currentMenu = ""
                menuIndx = 0
                authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                                 'cajohn0205@gmail.com', extra={'id': 123})
                database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/",
                                                        authentication=authentication)
                data = (database.get("restaurants/" + uid, "/menu/items/"))
                currentTime = str(
                    (float(datetime.datetime.now().hour)) + ((float(datetime.datetime.now().minute)) / 100.0))
                DBdata = database.get("/restaurants/" + estName, "orders")
                MenuHrs = ((database.get("restaurants/" + uid, "/Hours/")))
                menuLink = ""
                menKeys = list(MenuHrs.keys())
                for mnx in range(len(menKeys)):
                    startHrMn = (float(MenuHrs[menKeys[mnx]]["startHr"]))
                    endHrMn = (float(MenuHrs[menKeys[mnx]]["endHr"]))
                    if (startHrMn <= float(currentTime) < endHrMn):
                        #print("current menu")
                        #print(menKeys[mnx])
                        menuIndx = mnx
                        currentMenu = str(menKeys[mnx])
                        menuLink = str(MenuHrs[menKeys[mnx]]["link"])
                        break
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/time/", msg.upper())
                database.put("/restaurants/" + estName + "/orders/" + str(indx) + "/", "/stage/", 4)
                usrIndx = DBdata[indx]["userIndx"]
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
                #print(numOrders)
                database.put("/users/",
                             "/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                                 (len(numOrders) - 1)) + "/pickup-time", str(msg))
                linkOrder = database.get("/restaurants/" + estName, "/orderLink")
                reply = "Got it! click this link below to view the menu and continue ordering " + str(linkOrder)

                client.send_message({
                    'from': NexmoNumber,
                    'to': number,
                    'text': reply
                })
                #print("m0")
                return reply
    else:
        return ("no msg")


@application.route('/sms', methods=['GET', 'POST'])
def inbound_sms():
    data = dict(request.form) or dict(request.args)
    #print(data["text"])
    number = str(data['msisdn'][0])
    msg = str(data["text"][0])
    #print(number, msg)
    getReply(msg, number)
    return ('', 200)


@application.route('/ipn', methods=['POST'])
def ipn():
    logYM = (datetime.datetime.now().strftime("%Y-%m"))
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    DBdata = database.get("/restaurants/" + estName, "orders")
    for dbItems in range(len(DBdata)):
        #print(rsp["item_name"])
        if (DBdata[dbItems]["UUID"] == rsp["item_name"]):
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/paid/", 1)
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/filled/", "1")
            usrIndx = DBdata[dbItems]["userIndx"]
            # ticketSize = int(DBdata[dbItems]["tickSize"])
            # startTime = float(DBdata[dbItems]["startTime"])
            number = str(DBdata[dbItems]["number"])
            duration = time.time() - float(DBdata[dbItems]["startTime"])
            numItms = len(DBdata[dbItems]["item"])
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "tickSize/", numItms)
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/duration/", duration)
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/day/",
                         calendar.day_name[datetime.datetime.now().today().weekday()])
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/hour/",
                         int(datetime.datetime.now().hour))
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/month/",
                         (datetime.datetime.now().strftime("%m")))
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/date/",
                         (datetime.datetime.now().strftime("%d")))
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/year/",
                         (datetime.datetime.now().strftime("%Y")))

            numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
            database.put("/users/", "/" + str(usrIndx) + "/email", rsp["payer_email"])
            database.put("/users/", "/" + str(usrIndx) + "/country", rsp["address_country_code"])
            database.put("/users/", "/" + str(usrIndx) + "/state", rsp["address_state"])
            database.put("/users/", "/" + str(usrIndx) + "/zipCode", rsp["address_zip"])
            database.put("/users/", "/" + str(usrIndx) + "/city", rsp["address_city"])
            database.put("/users/", "/" + str(usrIndx) + "/streetAdr", rsp["address_street"])
            logData = database.get("/log/" + uid + "/", logYM)
            numCard = int(logData['cardPay'])
            numCard += 1
            payPalFees = float(logData['paypalFees'])
            payPalFees += float(rsp["mc_fee"])
            cdrFees = logData['CedarFees']
            cdrFees += 0.1
            database.put("/log/" + uid + "/" + logYM, "/CedarFees/", cdrFees)
            totalRev = float(logData["totalRev"])
            totalRev += float((DBdata[dbItems]["linkTotal"] + 0.1) * 1.1)
            database.put("/log/" + uid + "/" + logYM, "/totalRev/", totalRev)
            database.put("/log/" + uid + "/" + logYM, "/cardPay/", numCard)
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/zipCode/", rsp["address_zip"])
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/city/", rsp["address_city"])
            database.put("/log/" + uid + "/" + logYM, "/paypalFees/", payPalFees)
            numItms = len(DBdata[dbItems]["item"])
            orderIndx = DBdata[dbItems]["orderIndx"]
            usrIndx = DBdata[dbItems]["userIndx"]
            ret = int(logData["retCustomers"])
            newCust = int(logData["newCustomers"])
            if (DBdata[dbItems]["ret"] == 0):
                ret += 1
                database.put("/log/" + uid + "/" + logYM, "/retCustomers/", ret)
            else:
                newCust += 1
                database.put("/log/" + uid + "/" + logYM, "/newCustomers/", newCust)

            database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(orderIndx) + "/", "total",
                         ((DBdata[dbItems]["linkTotal"] + 0.1) * 1.1))
            database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(orderIndx) + "/",
                         "tickSize",
                         numItms)
            database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(orderIndx) + "/", "items",
                         DBdata[dbItems]["item"])
            database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(orderIndx) + "/",
                         "duration",
                         duration)
            #print("sending")
            reply = "-Thank you for your order, you can pick it up when you arrive and skip the line \n-To order again just text " + '"order"'
            updateLog()
            client.send_message({
                'from': NexmoNumber,
                'to': number,
                'text': reply
            })
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "number/", str((number) + "."))
    return (" ", 200)


@application.route('/' + estNameStr, methods=['GET'])
def loginPage():
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/",
                                            authentication=authentication)
    database.put("/restaurants/" + uid + "/", "loginTime", 0)
    return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@application.route('/' + estNameStr, methods=['POST'])
def loginPageCheck():
    rsp = ((request.form))
    email = str(rsp["email"])
    pw = str(rsp["pw"])
    try:
        user = auth.sign_in_with_email_and_password(str(rsp["email"]), pw)
        #print(user['localId'])
        authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                         'cajohn0205@gmail.com', extra={'id': 123})
        fireapp = firebase.FirebaseApplication('https://cedarchatbot.firebaseio.com/', authentication=authentication)
        testDB = (fireapp.get("/restaurants/", user["localId"]))
        if (str(user["localId"]) == str(uid) and testDB != None):
            #print("found")
            database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/",
                                                    authentication=authentication)
            database.put("/restaurants/" + uid + "/", "loginTime", time.time())
            return redirect(url_for('panel'))
        else:
            authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                             'cajohn0205@gmail.com', extra={'id': 123})
            #print("incorrect password")
            database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/",
                                                    authentication=authentication)
            database.put("/restaurants/" + uid + "/", "loginTime", 0)
            return render_template("login2.html", btn=str(estNameStr), restName=estNameStr)
    except Exception:
        authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                         'cajohn0205@gmail.com', extra={'id': 123})
        database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/",
                                                authentication=authentication)
        database.put("/restaurants/" + uid + "/", "loginTime", 0)
        #print("incorrect password")
        return render_template("login2.html", btn=str(estNameStr), restName=estNameStr)


@application.route('/' + uid, methods=['GET'])
def panel():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    if ((currentTime - lastLogin) < sessionTime):
        links = []
        names = []
        hours = (database.get("restaurants/" + uid, "/Hours/"))
        keys = list(hours.keys())
        for menuNames in range(len(keys)):
            names.append(str([keys[menuNames]][0]))
            links.append(str(hours[keys[menuNames]]["link"]))
            #print(links)
        updateLog()
        return render_template("panel.html", len=len(links), menuLinks=links, menuNames=names, restName=estNameStr,
                               viewOrders=(uid + "view"), addItm=(addPass), remItms=remPass, addCpn=promoPass,
                               signOut=estNameStr)
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@application.route('/' + uid + "view", methods=['GET'])
def view():
    orders = database.get("/restaurants/" + estName, "orders")
    webDataDisp = []
    keys = []
    #print(orders)
    for ords in range(len(orders)):
        try:
            filled = orders[ords]["filled"]
            #print(filled)
            if (filled == "1"):
                UUID = orders[ords]["UUID"]
                try:
                    subTotal = (orders[ords]["linkTotal"]) + orders[ords]["discTotal"]
                except KeyError:
                    subTotal = (orders[ords]["linkTotal"])
                Tax = float(subTotal * 0.1)
                Total = float(subTotal + float(Tax) + 0.1)
                subTotalStr = ('$' + format(subTotal, ',.2f'))
                TotalStr = ('$' + format(Total, ',.2f'))
                TaxStr = ('$' + format(Tax, ',.2f'))
                #print(TotalStr)
                writeStr = str(orders[ords]["name"]) + " || " + str(orders[ords]["finalOrder"]) + " " + str(
                    orders[ords]["discStr"]) \
                           + " || " + str(orders[ords]["togo"]) + " || " + str(orders[ords]["time"]) + " || " \
                                                                                                       "" + TotalStr + " || " + str(
                    orders[ords]["cash"])
                keys.append(UUID)
                #print(writeStr)
                webDataDisp.append(writeStr)
        except KeyError:
            #print("exec")
            pass
    return render_template("indexV.html", len=len(webDataDisp), webDataDisp=webDataDisp, keys=keys,
                           btn=str(uid + "view"), restName=estNameStr)


@application.route('/' + uid + "view", methods=['POST'])
def button():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    item = (rsp['item'])
    #print(item)
    orders = database.get("/restaurants/" + estName, "orders")
    webDataDisp = []
    keys = []
    #print(orders)
    for ords in range(len(orders)):
        UUID = orders[ords]["UUID"]
        if (item == UUID):
            database.put("/restaurants/" + estName + "/orders/" + str(ords) + "/", "/filled/", "2")
        else:
            filled = orders[ords]["filled"]
            if (filled == "1"):
                UUID = orders[ords]["UUID"]
                try:
                    subTotal = (orders[ords]["linkTotal"]) + orders[ords]["discTotal"]
                except KeyError:
                    subTotal = (orders[ords]["linkTotal"])
                Tax = float(orders[ords]["linkTotal"] * 0.1)
                Total = float(subTotal + float(Tax) + 0.1)
                subTotalStr = ('$' + format(subTotal, ',.2f'))
                TotalStr = ('$' + format(Total, ',.2f'))
                TaxStr = ('$' + format(Tax, ',.2f'))
                #print(TotalStr)
                writeStr = str(orders[ords]["name"]) + " || " + str(orders[ords]["finalOrder"]) + " " + str(
                    orders[ords]["discStr"]) \
                           + " || " + str(orders[ords]["togo"]) + " || " + str(orders[ords]["time"]) + " || " \
                                                                                                       "" + TotalStr + " || " + str(
                    orders[ords]["cash"])
                keys.append(UUID)
                #print(writeStr)
                webDataDisp.append(writeStr)
    return render_template("indexV.html", len=len(webDataDisp), webDataDisp=webDataDisp, keys=keys,
                           btn=str(uid + "view"))


@application.route('/' + remPass, methods=['GET'])
def removeItemsDisp():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    #print()
    if ((currentTime - lastLogin) < sessionTime):
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        #print(menuItems)
        names = []
        keys = []
        for men in range(len(menuItems)):

            if (menuItems[men]["descrip"] != "REMOVEDITM!"):
                names.append(menuItems[men]["name"])
                keys.append(men)
        return render_template("remItems.html", len=len(names), names=names, keys=keys, btn=remPass)
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@application.route('/' + remPass, methods=['POST'])
def removeItems():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    if ((currentTime - lastLogin) < sessionTime):
        request.parameter_storage_class = ImmutableOrderedMultiDict
        rsp = ((request.form))
        item = int(rsp['item'])
        names = []
        keys = []
        database.put("/restaurants/" + estName + "/menu/items/" +str(item)+"/", "descrip", "REMOVEDITM!")
        database.put("/restaurants/" + estName + "/menu/items/" + str(item) + "/", "sizes/0/1", -1)
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        for men in range(len(menuItems)):
            if (menuItems[men]["descrip"] != "REMOVEDITM!"):
                names.append(menuItems[men]["name"])
                keys.append(men)
        pdf = FPDF()
        pdf.add_page()
        yStart = 20
        authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                         'cajohn0205@gmail.com', extra={'id': 123})
        database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
        menu = (database.get("restaurants/" + uid, "/menu/items/"))
        hours = (database.get("restaurants/" + uid, "/Hours/"))
        #print(hours)
        keys = list(hours.keys())
        for menuNames in range(len(keys)):
            pdf = FPDF()
            pdf.add_page()
            yStart = 20
            pdf.set_font(fontName, size=24, style="BU")
            text = estNameStr + " " + str([keys[menuNames]][0]) + " Menu"
            pdf.multi_cell(200, 10, txt=text, align="C")
            yStart += 10
            for dt in range(len(menu)):
                if (menu[dt] != None):
                    if ((menu[dt]["sizes"][0][1] != -1)):
                        name = menu[dt]["name"].lower()
                        #print(name)
                        #print(menu[dt]["time"], str([keys[menuNames]][0]))
                        #print(menu[dt]["time"] == str([keys[menuNames]][0]))
                        #print(str(menu[dt]["time"]).lower() == "all")
                        #print("\n")
                        if (str(menu[dt]["time"]).lower() == "all" or str(menu[dt]["time"]).lower() == str(
                                [keys[menuNames]][0]).lower()):
                            name = menu[dt]["name"].lower()
                            sizes = []
                            toppings = []
                            for sz in range(len(menu[dt]["sizes"])):
                                sizes.append([str(menu[dt]["sizes"][sz][0]).lower(), menu[dt]["sizes"][sz][1]])
                            if (str(menu[dt]["extras"][0][0]) != ""):
                                for ex in range(len(menu[dt]["extras"])):
                                    toppings.append([str(menu[dt]["extras"][ex][0]).lower(), menu[dt]["extras"][ex][1]])
                            # pdf.line(0, yStart, 500000, yStart)
                            pdf.set_font(fontName, size=18, style="B")
                            text = name
                            pdf.multi_cell(100, 10, txt=text, align="L")
                            yStart += 10
                            text = ""
                            pdf.set_font(fontName, size=14, style="B")
                            if (len(sizes) > 1):
                                text = "-Sizes:"
                                pdf.multi_cell(100, 7, txt=text, align="L")
                                yStart += 7
                                pdf.set_font(fontName, size=12, style="")
                                text = ""
                                for szs in range(len(sizes)):
                                    text += "     -"
                                    text += sizes[szs][0]
                                    text += " ~ $" + str(sizes[szs][1])
                                    pdf.multi_cell(100, 7, txt=text, align="L")
                                    yStart += 7
                                    text = ""
                            else:
                                pdf.set_font(fontName, size=12, style="")
                                text += "     ~$" + str(sizes[0][1])
                                pdf.multi_cell(100, 7, txt=text, align="L")
                                yStart += 7
                                text = ""
                            if (len(toppings) > 1):
                                pdf.set_font(fontName, size=14, style="B")
                                text = "-Toppings/Customizations:"
                                pdf.multi_cell(100, 7, txt=text, align="L")
                                yStart += 7
                                text = ""
                                pdf.set_font(fontName, size=12, style="")
                                for ex in range(len(toppings)):
                                    text += "     -"
                                    text += toppings[ex][0]
                                    text += " ~ $" + str(toppings[ex][1])
                                    pdf.multi_cell(100, 7, txt=text, align="L")
                                    yStart += 7
                                    text = ""
                            yStart += 7
                            text = ""
            fileName = "menus/" + estNameStr + "-" + str([keys[menuNames]][0]) + "-" + "menu.pdf"
            pdf.output(fileName)
            storage = firebaseAuth.storage()
            storage.child(estNameStr + "/" + fileName).put(fileName)
            #print("\n")
        return redirect(url_for('panel'))
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@application.route('/' + addPass, methods=['GET'])
def addItmDisp():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    #print()
    if ((currentTime - lastLogin) < sessionTime):
        return render_template('addform.html', btn=addPass, restName=estNameStr)
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@application.route('/' + addPass, methods=['POST'])
def addItmForm():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    #print()
    if ((currentTime - lastLogin) < sessionTime):
        request.parameter_storage_class = ImmutableOrderedMultiDict
        rsp = ((request.form))
        name = str(rsp['name']).lower()
        numSizes = int(rsp['numSizes'])
        menTime = str(rsp['time']).lower()
        descrip = str(rsp['desc']).lower() + " "
        #print(name)
        #print(numSizes)
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        keyVal = 0
        for mmx in range(len(menuItems)):
            if (menuItems[mmx] != None):
                if (keyVal < mmx):
                    keyVal = mmx
        keyVal += 1
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/name/", name)
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/time/", menTime)
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/descrip/", descrip)
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/inp/", "inp")
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal) + "/extras/" + str(0), "/0/", "")
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal) + "/extras/" + str(0), "/1/", 0)
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal) + "/extras/" + str(0), "/2/", "")
        for nn in range(numSizes):
            database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal) + "/sizes/" + str(nn), "/0", "")
            database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal) + "/sizes/" + str(nn), "/1", 0)
            return render_template('addform2.html', btn=(str(addPass) + "2"), len=numSizes, restName=estNameStr)
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@application.route('/' + addPass + "2", methods=['POST'])
def addItmResp2():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    if ((currentTime - lastLogin) < sessionTime):
        request.parameter_storage_class = ImmutableOrderedMultiDict
        rsp = ((request.form))
        numExtras = rsp["numEx"]
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        for sx in range(len(menuItems)):
            if (menuItems[sx] != None):
                if (menuItems[sx]['inp'] == "inp"):
                    for ssz in range(int((len(rsp) - 1) / 3)):
                        szName = rsp[str(ssz)]
                        szPrice = rsp[str(ssz) + "a"]
                        sku = rsp[str(ssz) + "b"]
                        database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/sizes/" + str(ssz), "/0/",
                                     szName)
                        database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/sizes/" + str(ssz), "/1/",
                                     float(szPrice))
                        database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/sizes/" + str(ssz), "/2/",
                                     str(sku))
                    if (numExtras != ""):
                        for sse in range(int(numExtras)):
                            database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse),
                                         "/0/",
                                         "")
                            database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse),
                                         "/1/", 0)
                    else:
                        database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse),
                                     "/0/",
                                     "")
                        database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse),
                                     "/1/", 0)
                    break
        return render_template('addform3.html', btn=(str(addPass) + "3"), len=int(numExtras), restName=estNameStr)
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@application.route('/' + addPass + "3", methods=['GET'])
def addItmForm3():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    if ((currentTime - lastLogin) < sessionTime):
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        for sx in range(len(menuItems)):
            if (menuItems[sx] != None):
                if (menuItems[sx]['inp'] == "inp"):
                    itxL = int(len(menuItems[sx]['extras']))
                    return render_template('addform3.html', btn=(str(addPass) + "3"), len=itxL, restName=estNameStr)
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@application.route('/' + addPass + "3", methods=['POST'])
def addItmResp3():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    #print()
    if ((currentTime - lastLogin) < sessionTime):
        request.parameter_storage_class = ImmutableOrderedMultiDict
        rsp = ((request.form))
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        for sx in range(len(menuItems)):
            if (menuItems[sx] != None):
                if (menuItems[sx]['inp'] == "inp"):
                    for sse in range(int(len(rsp) / 3)):
                        exName = rsp[str(sse)]
                        exPrice = rsp[str(sse) + "a"]
                        sku = rsp[str(sse) + "b"]
                        database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse),
                                     "/0/",
                                     exName)
                        database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse),
                                     "/1/", float(exPrice))
                        database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse),
                                     "/2/", str(sku))
                    database.put("/restaurants/" + estName + "/menu/items/" + str(sx), "/inp/", "")
                    menu = (database.get("restaurants/" + uid, "/menu/items/"))
                    break
        # select the first sheet
        startHr = 0
        endHr = 0
        authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                         'cajohn0205@gmail.com', extra={'id': 123})
        database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
        menu = (database.get("restaurants/" + uid, "/menu/items/"))
        hours = (database.get("restaurants/" + uid, "/Hours/"))
        keys = list(hours.keys())
        for menuNames in range(len(keys)):
            pdf = FPDF()
            pdf.add_page()
            yStart = 20
            pdf.set_font(fontName, size=24, style="BU")
            text = estNameStr + " " + str([keys[menuNames]][0]) + " Menu"
            pdf.multi_cell(200, 10, txt=text, align="C")
            yStart += 10
            for dt in range(len(menu)):
                if (menu[dt] != None):
                    if ((menu[dt]["sizes"][0][1] != -1)):
                        name = menu[dt]["name"].lower()
                        if (str(menu[dt]["time"]).lower() == "all" or str(menu[dt]["time"]).lower() == str(
                                [keys[menuNames]][0]).lower()):
                            name = menu[dt]["name"].lower()
                            sizes = []
                            toppings = []
                            for sz in range(len(menu[dt]["sizes"])):
                                sizes.append([str(menu[dt]["sizes"][sz][0]).lower(), menu[dt]["sizes"][sz][1]])
                            if (str(menu[dt]["extras"][0][0]) != ""):
                                for ex in range(len(menu[dt]["extras"])):
                                    toppings.append([str(menu[dt]["extras"][ex][0]).lower(), menu[dt]["extras"][ex][1]])
                            # pdf.line(0, yStart, 500000, yStart)
                            pdf.set_font(fontName, size=18, style="B")
                            text = name
                            pdf.multi_cell(100, 10, txt=text, align="L")
                            yStart += 10
                            text = ""
                            pdf.set_font(fontName, size=14, style="B")
                            if (len(sizes) > 1):
                                text = "-Sizes:"
                                pdf.multi_cell(100, 7, txt=text, align="L")
                                yStart += 7
                                pdf.set_font(fontName, size=12, style="")
                                text = ""
                                for szs in range(len(sizes)):
                                    text += "     -"
                                    text += sizes[szs][0]
                                    text += " ~ $" + str(sizes[szs][1])
                                    pdf.multi_cell(100, 7, txt=text, align="L")
                                    yStart += 7
                                    text = ""
                            else:
                                pdf.set_font(fontName, size=12, style="")
                                text += "     ~$" + str(sizes[0][1])
                                pdf.multi_cell(100, 7, txt=text, align="L")
                                yStart += 7
                                text = ""
                            if (len(toppings) > 0):
                                pdf.set_font(fontName, size=14, style="B")
                                text = "-Toppings/Customizations:"
                                pdf.multi_cell(100, 7, txt=text, align="L")
                                yStart += 7
                                text = ""
                                pdf.set_font(fontName, size=12, style="")
                                for ex in range(len(toppings)):
                                    text += "     -"
                                    text += toppings[ex][0]
                                    text += " ~ $" + str(toppings[ex][1])
                                    pdf.multi_cell(100, 7, txt=text, align="L")
                                    yStart += 7
                                    text = ""
                            yStart += 7
                            text = ""
            fileName = "menus/" + estNameStr + "-" + str([keys[menuNames]][0]) + "-" + "menu.pdf"
            #print(fileName)
            pdf.output(fileName)
            storage = firebaseAuth.storage()
            storage.child(estNameStr + "/" + fileName).put(fileName)
            #print("\n")
        return redirect(url_for('panel'))
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@application.route('/' + promoPass, methods=['GET'])
def addCpn():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    #print()
    if ((currentTime - lastLogin) < sessionTime):
        return render_template('coupon.html', restName=estNameStr)
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@application.route('/' + promoPass, methods=['POST'])
def addCpnResp():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    #print()
    if ((currentTime - lastLogin) < sessionTime):
        request.parameter_storage_class = ImmutableOrderedMultiDict
        rsp = ((request.form))
        #print(rsp)
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
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/descrip/", " ")
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/sku/", "cpn-" + name)
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/sizes/0/0/", "u")
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/sizes/0/1/", -1)
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/extras/0/0/", item)
        try:
            amt = float(amt)
            database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/extras/0/1/", amt)
        except ValueError:
            database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/extras/0/1/", amt)
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/extras/1/0/", "limit")
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/extras/1/1/", (limit - 1))
        menu = (database.get("restaurants/" + uid, "/menu/items/"))
        return render_template('coupon.html', restName=estNameStr)
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@application.route("/" + uid + "check", methods=['GET'])
def loginUUID():
    return render_template("verifyCode.html", btn=str(uid + "check"))


@application.route('/' + uid + 'check', methods=['POST'])
def getUUID():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    code = rsp["tickID"]
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    tickets = database.get("restaurants/" + uid, "/orders/")
    for tx in range(len(tickets)):
        if (code == tickets[tx]["number"][-4:]):
            key = tx
            UUID = tickets[tx]["UUID"]
            session['UUID'] = UUID
            session['key'] = key
            return redirect(url_for('order'))
        elif ((len(tickets) - tx) == 1):
            return render_template("verifyCode2.html", btn=str(uid + "check"))


@application.route('/' + uid + 'order', methods=['GET'])
def order():
    UUID = session.get('UUID', None)
    #key = session.get('key', None)
    key = 0
    nameKey = session.get('nameKey', None)
    itmKey = random.randint(9999, 1000000)
    session['itmKey'] = itmKey
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    data = (database.get("restaurants/" + uid, "/menu/items/"))
    currentTime = str((float(datetime.datetime.now().hour)) + ((float(datetime.datetime.now().minute)) / 100.0))
    currentTotal = float(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
    DBdata = database.get("/restaurants/" + estName, "orders")
    try:
        subTotal = (DBdata[key]["linkTotal"]) + DBdata[key]["discTotal"]
    except KeyError:
        subTotal = (DBdata[key]["linkTotal"])
    Tax = float(subTotal * 0.1)
    Total = float(subTotal + float(Tax) + 0.1)
    subTotalStr = ('$' + format(subTotal, ',.2f'))
    TotalStr = ('$' + format(Total, ',.2f'))
    TaxStr = ('$' + format(Tax, ',.2f'))
    dispTotal = subTotalStr
    MenuHrs = ((database.get("restaurants/" + uid, "/Hours/")))
    menKeys = list(MenuHrs.keys())
    currentMenu = ""
    menuIndx = 0
    for mnx in range(len(menKeys)):
        startHrMn = (float(MenuHrs[menKeys[mnx]]["startHr"]))
        endHrMn = (float(MenuHrs[menKeys[mnx]]["endHr"]))
        if (startHrMn <= float(currentTime) < endHrMn):
            menuIndx = mnx
            currentMenu = str(menKeys[mnx])
            break
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    itms = database.get("/restaurants/" + estName + "/orders/" + str(key), "/item/")
    currentItems = []
    currKeys = []
    if (itms != None):
        dispKeys = list(itms.keys())
        for itmX in range(len(dispKeys)):
            try:
                if (itms[dispKeys[itmX]] != None):
                    wrtStr = ""
                    if (str(itms[dispKeys[itmX]]["size"]).lower() != "u"):
                        wrtStr += str(itms[dispKeys[itmX]]["size"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["name"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["notes"])
                        wrtStr += " x "
                        wrtStr += str(itms[dispKeys[itmX]]["qty"])
                        wrtStr += " $"
                        wrtStr += str(itms[dispKeys[itmX]]["price"])
                        currentItems.append(wrtStr)
                        currKeys.append(dispKeys[itmX])
                    else:
                        wrtStr = str(itms[dispKeys[itmX]]["name"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["notes"])
                        wrtStr += " x "
                        wrtStr += str(itms[dispKeys[itmX]]["qty"])
                        wrtStr += " $"
                        wrtStr += str(itms[dispKeys[itmX]]["price"])
                        currentItems.append(wrtStr)
                        currKeys.append(dispKeys[itmX])
            except KeyError:
                pass
    names = []
    keys = []
    descrips = []
    for men in range(len(menuItems)):
        if (menuItems[men] != None and (menuItems[men]["time"] == currentMenu or menuItems[men]["time"] == "all")):
            if (menuItems[men]["sizes"][0][1] != -1):
                names.append(str(menuItems[men]["name"]).upper())
                descrips.append(str(menuItems[men]["descrip"]).lower())
                keys.append(men)
    return render_template("mainOrder.html", len=len(names), names=names, keys=keys, btn=uid + "orderSz",
                           len2=(len(currentItems)),descrips=descrips ,currentItms=currentItems, currKeys=currKeys, btn2=uid + "order",
                           total=dispTotal, btn3=uid + "checkpayment")


@application.route('/' + uid + 'order', methods=['POST'])
def orderX():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    itmKey = random.randint(9999, 1000000)
    session['itmKey'] = itmKey
    #print(UUID, key, itmKey)
    #print(rsp)

    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    currentPrice = float(
        database.get("/restaurants/" + estName + "/orders/" + str(key) + "/item/" + str((rsp["rem"])), "price"))
    currentTotal = float(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
    currentTotal -= currentPrice
    DBdata = database.get("/restaurants/" + estName, "orders")
    subTotal = (DBdata[key]["linkTotal"]) + DBdata[key]["discTotal"]
    Tax = float(subTotal * 0.1)
    Total = float(subTotal + float(Tax) + 0.15)
    subTotalStr = ('$' + format(subTotal, ',.2f'))
    TotalStr = ('$' + format(Total, ',.2f'))
    TaxStr = ('$' + format(Tax, ',.2f'))
    dispTotal = subTotalStr
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/linkTotal/", currentTotal)
    database.delete("/restaurants/" + estName + "/orders/" + str(key) + "/item/", (rsp["rem"]))
    data = (database.get("restaurants/" + uid, "/menu/items/"))
    currentTime = str((float(datetime.datetime.now().hour)) + ((float(datetime.datetime.now().minute)) / 100.0))
    DBdata = database.get("/restaurants/" + estName, "orders")
    MenuHrs = ((database.get("restaurants/" + uid, "/Hours/")))
    menKeys = list(MenuHrs.keys())
    currentMenu = ""
    menuIndx = 0
    for mnx in range(len(menKeys)):
        startHrMn = (float(MenuHrs[menKeys[mnx]]["startHr"]))
        endHrMn = (float(MenuHrs[menKeys[mnx]]["endHr"]))
        if (startHrMn <= float(currentTime) < endHrMn):
            #print("current menu")
            #print(menKeys[mnx])
            menuIndx = mnx
            currentMenu = str(menKeys[mnx])
            break
    session['UUID'] = UUID
    session['key'] = key
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    itms = database.get("/restaurants/" + estName + "/orders/" + str(key), "/item/")
    currentItems = []
    currKeys = []
    finalOrd = ""
    if (itms != None):
        dispKeys = list(itms.keys())
        for itmX in range(len(dispKeys)):
            try:
                if (itms[dispKeys[itmX]] != None):
                    wrtStr = ""
                    if (str(itms[dispKeys[itmX]]["size"]).lower() != "u"):
                        wrtStr += str(itms[dispKeys[itmX]]["size"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["name"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["notes"])
                        wrtStr += " x "
                        wrtStr += str(itms[dispKeys[itmX]]["qty"])
                        wrtStr += " $"
                        wrtStr += str(itms[dispKeys[itmX]]["price"])
                        currentItems.append(wrtStr)
                        currKeys.append(dispKeys[itmX])
                        #print(wrtStr)
                    else:
                        wrtStr = str(itms[dispKeys[itmX]]["name"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["notes"])
                        wrtStr += " x "
                        wrtStr += str(itms[dispKeys[itmX]]["qty"])
                        wrtStr += " $"
                        wrtStr += str(itms[dispKeys[itmX]]["price"])
                        currentItems.append(wrtStr)
                        currKeys.append(dispKeys[itmX])
                        #print(wrtStr)
            except KeyError:
                pass
    else:
        dispTotal = "$0.00"
    names = []
    keys = []
    descrips = []
    #print(type(menuItems))
    for men in range(len(menuItems)):
        if (menuItems[men] != None and (menuItems[men]["time"] == currentMenu or menuItems[men]["time"] == "all")):
            if (menuItems[men]["sizes"][0][1] != -1):
                names.append(str(menuItems[men]["name"]).upper())
                descrips.append(str(menuItems[men]["descrip"]).lower())
                keys.append(men)
    return render_template("mainOrderBtn.html", len=len(names), names=names, keys=keys, btn=uid + "orderSz",
                           len2=(len(currentItems)), descrips=descrips ,currentItms=currentItems, total=dispTotal, currKeys=currKeys,
                           btn2=uid + "order", btn3=uid + "checkpayment")


@application.route('/' + uid + 'orderSz', methods=['POST'])
def orderNm():
    newItmKey = session.get('itmKey', None)
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    #print(UUID, key)
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    names = []
    keys = []
    prices = []
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    numItms = database.get("/restaurants/" + estName + "/orders/" + str(key), "item")
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(newItmKey) + "/name/",
                 str(menuItems[int(rsp['item'])]['name'].lower()))
    sizes = menuItems[int(rsp['item'])]['sizes']
    for sz in range(len(sizes)):
        if ((menuItems[int(rsp['item'])]['sizes'][sz][0].lower()) != "u"):
            putStr = ""
            putStr += str(menuItems[int(rsp['item'])]['sizes'][sz][0]).lower()
            putStr += " $"
            putStr += str(menuItems[int(rsp['item'])]['sizes'][sz][1])
            names.append(putStr)
            keys.append(sz)
            prices.append(menuItems[int(rsp['item'])]['sizes'][sz][1])
        else:
            names.append("Standard")
            keys.append(0)
            prices.append(menuItems[int(rsp['item'])]['sizes'][sz][1])
    session['itmKey'] = newItmKey
    session['nameKey'] = int(rsp['item'])
    return render_template("picksize.html", len=len(prices), names=names, keys=keys, prices=prices,
                           btn=uid + "ordertopping")


@application.route('/' + uid + 'ordertopping', methods=['POST'])
def ordertp():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    itmKey = session.get('itmKey', None)
    nameKey = session.get('nameKey', None)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    #print(menuItems[nameKey], "current item")
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/size/",
                 str(menuItems[nameKey]['sizes'][int(rsp['item'])][0].lower()))
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/price/",
                 float(menuItems[nameKey]['sizes'][int(rsp['item'])][1]))
    skuKey = random.randint(99999, 1000000)
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/",
                 "/item/" + str(itmKey) + "/skus/" + str(skuKey) + "/",
                 str(menuItems[nameKey]['sizes'][int(rsp['item'])][2]))
    names = []
    keys = []
    prices = []
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    toppings = menuItems[nameKey]["extras"]
    names = []
    keys = []
    for ex in range(len(toppings)):
        if (toppings[ex][0] != ""):
            putStr = ""
            putStr += str(toppings[ex][0].lower())
            putStr += " $"
            putStr += str(toppings[ex][1])
            names.append(putStr)
            keys.append(ex)
    #print(rsp)
    return render_template("pickToppings.html", len=len(names), names=names, keys=keys, prices=prices,
                           btn=uid + "ordertoppingConfirm")


@application.route('/' + uid + 'ordertoppingConfirm', methods=['POST'])
def ConfirmItm():
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    itmKey = session.get('itmKey', None)
    nameKey = session.get('nameKey', None)
    #print("nameKEY", nameKey)
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    #print(menuItems[nameKey], "topping")
    #print(rsp, "rsp")
    #print(len(rsp))
    putStr = ""
    addPrice = 0
    extraIndxs = []
    SKUSarr = []
    if (len(rsp) > 2):
        #print(rsp["quantity"])
        #print(rsp["notes"])
        for itx in range(len(menuItems[nameKey]["extras"])):
            ##print(itx)
            try:
                #print(rsp[str(itx)], "found")
                extraIndxs.append(int(itx))
            except Exception:
                #print(str(itx), "not found")
                pass
        #print(extraIndxs)
        for exx in range(len(extraIndxs)):
            putStr += str(menuItems[nameKey]["extras"][extraIndxs[exx]][0])
            #print(menuItems[nameKey]["extras"][extraIndxs[exx]])
            addPrice += float(menuItems[nameKey]["extras"][extraIndxs[exx]][1])
            addPrice = round(addPrice, 2)
            putStr += " "
            SKUSarr.append(str(menuItems[nameKey]["extras"][extraIndxs[exx]][2]))
            skuKey = random.randint(99999, 1000000)
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/",
                         "/item/" + str(itmKey) + "/skus/" + str(skuKey) + "/",
                         str(menuItems[nameKey]["extras"][extraIndxs[exx]][2]))
        currentPrice = float(
            database.get("/restaurants/" + estName + "/orders/" + str(key) + "/item/" + str(itmKey), "price"))
        currentPrice += addPrice
        round(currentPrice, 2)
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/toppings/",
                     putStr)
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/notes/",
                     putStr)
        if (rsp["quantity"] == ""):
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/qty/", 1)
        else:
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/qty/",
                         int(rsp["quantity"]))
            currentPrice = currentPrice * int(rsp["quantity"])
            #print(currentPrice)
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/notes/",
                     rsp["notes"])
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/price/",
                     currentPrice)
        currentTotal = float(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
        currentTotal += currentPrice
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/linkTotal/", currentTotal)
    else:
        currentPrice = float(
            database.get("/restaurants/" + estName + "/orders/" + str(key) + "/item/" + str(itmKey), "price"))
        round(currentPrice, 2)
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/toppings/",
                     putStr)
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/notes/",
                     putStr)
        if (rsp["quantity"] == ""):
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/qty/", 1)
            currentTotal = float(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
            currentTotal += currentPrice
            round(currentPrice, 2)
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/linkTotal/", currentTotal)
        else:
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/qty/",
                         int(rsp["quantity"]))
            currentPrice = currentPrice * int(rsp["quantity"])
            #print(currentPrice)
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/notes/",
                     rsp["notes"])
        currentPrice = float(
            database.get("/restaurants/" + estName + "/orders/" + str(key) + "/item/" + str(itmKey), "price"))
        round(currentPrice, 2)
        currentTotal = float(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
        currentTotal += currentPrice
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/linkTotal/", currentTotal)
    return redirect(url_for('order'))


@application.route('/' + uid + 'checkpayment', methods=['POST'])
def CheckPaymentMethod():
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    itms = database.get("/restaurants/" + estName + "/orders/" + str(key), "/item/")
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    if (itms != None):
        finalOrd = ""
        dispKeys = list(itms.keys())
        for itmX in range(len(dispKeys)):
            if (itms[dispKeys[itmX]] != None):
                #print(itms[dispKeys[itmX]])
                skuKeys = list(itms[dispKeys[itmX]]["skus"].keys())
                wrtStr = ""
                if (str(itms[dispKeys[itmX]]["size"]).lower() != "u"):
                    wrtStr += str(itms[dispKeys[itmX]]["size"])
                    wrtStr += " "
                    #print(wrtStr)
                    #print(str(itms[dispKeys[itmX]]["size"]))
                    wrtStr += str(itms[dispKeys[itmX]]["name"])
                    wrtStr += " "
                    wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                    wrtStr += " "
                    wrtStr += str(itms[dispKeys[itmX]]["notes"])
                    wrtStr += " x "
                    wrtStr += str(itms[dispKeys[itmX]]["qty"])
                    wrtStr += " $"
                    wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                    #print(wrtStr)
                    finalOrd += wrtStr + " :: "
                    skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                    for skk in range(len(skuKeyItm)):
                        currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                        for mmn in range(len(menuItems)):
                            if (menuItems[mmn] != None):
                                if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn]["descrip"] != "REMOVEDITM!"):
                                    if (str(menuItems[mmn]["extras"][0][0]) == str(currentSkuItm)):
                                        #print("ggbrgebrgebr")
                                        discAmt = menuItems[mmn]["extras"][0][1]
                                        limit = int(menuItems[mmn]["extras"][1][1])
                                        cpnUsed = int(
                                            database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                         "/discUsed/"))
                                        discTotal = float(
                                            database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                         "/discTotal/"))
                                        #print(cpnUsed, limit, discTotal)
                                        if (cpnUsed <= limit):
                                            try:
                                                float(discAmt)
                                                discAmtflt = float(discAmt)
                                                #print(cpnUsed, limit, int(itms[dispKeys[itmX]]["qty"]))
                                                while cpnUsed <= limit and cpnUsed <= int(itms[dispKeys[itmX]]["qty"]):
                                                    #print("iid")
                                                    discTotal -= discAmtflt
                                                    cpnUsed += 1
                                            except ValueError:
                                                discAmt = discAmt[:-1]
                                                discAmtflt = float(discAmt)
                                                #print(discAmtflt)
                                                #print(cpnUsed, limit, int(itms[dispKeys[itmX]]["qty"]))
                                                while cpnUsed <= limit and cpnUsed <= int(itms[dispKeys[itmX]]["qty"]):
                                                    discTotal -= (float(discAmtflt) * (
                                                                (float(itms[dispKeys[itmX]]["price"])) / float(
                                                            itms[dispKeys[itmX]]["qty"])))
                                                    #print(discTotal)
                                                    cpnUsed += 1
                                                    #print(cpnUsed)
                                                #print(discTotal)
                                            #print(cpnUsed)
                                            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                         "/discUsed/", cpnUsed)
                                            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                         "/discTotal/", discTotal)
                                            database.put(
                                                "/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                "/discStr/", str(
                                                    str(menuItems[mmn]["name"]) + " x " + str(
                                                        cpnUsed) + " -$" + str(float(discTotal * -1))))
                                            finalOrd += menuItems[mmn]["name"] + " x " + str(cpnUsed) + " -$" + str(
                                                float(
                                                    discTotal * -1)) + " :: "
                                            break
                    else:
                        wrtStr = str(itms[dispKeys[itmX]]["name"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["notes"])
                        wrtStr += " x "
                        wrtStr += str(itms[dispKeys[itmX]]["qty"])
                        wrtStr += " $"
                        wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                        #print(wrtStr)
                        finalOrd += wrtStr + " :: "
                        skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                        for skk in range(len(skuKeyItm)):
                            currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                            for mmn in range(len(menuItems)):
                                if (menuItems[mmn] != None):
                                    if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn]["descrip"] != "REMOVEDITM!"):
                                        if (str(menuItems[mmn]["extras"][0][0]) == str(currentSkuItm)):
                                            discAmt = menuItems[mmn]["extras"][0][1]
                                            limit = int(menuItems[mmn]["extras"][1][1])
                                            cpnUsed = int(
                                                database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                             "/discUsed/"))
                                            discTotal = float(
                                                database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                             "/discTotal/"))
                                            if (cpnUsed <= limit):
                                                try:
                                                    float(discAmt)
                                                    discAmtflt = float(discAmt)
                                                    while cpnUsed < limit and cpnUsed < int(
                                                            itms[dispKeys[itmX]]["qty"]):
                                                        discTotal -= discAmtflt
                                                        cpnUsed += 1
                                                except ValueError:
                                                    discAmt = discAmt[:-1]
                                                    discAmtflt = float(discAmt)
                                                    #print(cpnUsed, limit, int(itms[dispKeys[itmX]]["qty"]))
                                                    while cpnUsed < limit and cpnUsed < int(
                                                            itms[dispKeys[itmX]]["qty"]):
                                                        #print(cpnUsed)
                                                        #print("fsfwrrw")
                                                        discTotal -= float(
                                                            float(discAmtflt) * float(itms[dispKeys[itmX]]["price"]))
                                                        #print(discTotal)
                                                        cpnUsed += 1
                                                #print(discTotal)
                                                database.put("/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                             "/discUsed/", cpnUsed)
                                                database.put("/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                             "/discTotal/", discTotal)
                                                database.put(
                                                    "/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                    "/discStr/", str(
                                                        str(menuItems[mmn]["name"]) + " x " + str(
                                                            cpnUsed) + ":: -$" + str(round(float(discTotal * -1), 2))))
                                                finalOrd += menuItems[mmn]["name"] + " x " + str(
                                                    cpnUsed) + ":: -$" + str(round(float(discTotal * -1), 2)) + " :: "
                                                break

    DBdata = database.get("/restaurants/" + estName, "orders")
    subTotal = (DBdata[key]["linkTotal"])
    subTotal += DBdata[key]["discTotal"]
    #print(subTotal)
    disc = (DBdata[key]["discStr"])
    Tax = float(subTotal * 0.1)
    Total = float(subTotal + float(Tax) + 0.15)
    subTotalStr = ('$' + format(subTotal, ',.2f'))
    TotalStr = ('$' + format(Total, ',.2f'))
    TaxStr = ('$' + format(Tax, ',.2f'))
    return render_template("paymentMethod.html", btn=uid + "nextPay", subTotal=subTotalStr, tax=TaxStr, total=TotalStr,
                           CPN=disc)


@application.route('/' + uid + 'nextPay', methods=['POST'])
def nextPayment():
    logYM = (datetime.datetime.now().strftime("%Y-%m"))
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    dbItems = key
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    logData = database.get("/log/" + uid + "/", logYM)
    if (logData == None):
        database.put("/log/" + uid + "/" + logYM, "/newCustomers/", 0)
        database.put("/log/" + uid + "/" + logYM, "/retCustomers/", 0)
        database.put("/log/" + uid + "/" + logYM, "/paypalFees/", 0.0)
        database.put("/log/" + uid + "/" + logYM, "/CedarFees/", 0.0)
        database.put("/log/" + uid + "/" + logYM, "/totalRev/", 0.0)
        database.put("/log/" + uid + "/" + logYM, "/skus/9Null/numSold", 0)
        database.put("/log/" + uid + "/" + logYM, "/skus/9Null/rev", 0)
    currentTotal = float(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
    number = str(database.get("/restaurants/" + estName + "/orders/" + str(key), "/number"))
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    #print(rsp)
    finalOrd = ""
    if (rsp["item"] == "yes"):
        itms = database.get("/restaurants/" + estName + "/orders/" + str(key), "/item/")
        itms = database.get("/restaurants/" + estName + "/orders/" + str(key), "/item/")
        if (itms != None):
            finalOrd = ""
            dispKeys = list(itms.keys())
            for itmX in range(len(dispKeys)):
                try:
                    if (itms[dispKeys[itmX]] != None):
                        #print(itms[dispKeys[itmX]])
                        skuKeys = list(itms[dispKeys[itmX]]["skus"].keys())
                        for sk in range(len(skuKeys)):
                            currentSku = database.get("/log/" + estName + "/" + str(logYM) + "/" + "skus/",
                                                      itms[dispKeys[itmX]]["skus"][skuKeys[sk]])
                            if (currentSku != None):
                                numsold = currentSku["numSold"] + int(itms[dispKeys[itmX]]["qty"])
                                rev = currentSku["rev"] + (
                                        float(itms[dispKeys[itmX]]["qty"]) * float(itms[dispKeys[itmX]]["price"]))
                                database.put("/log/" + uid + "/" + logYM,
                                             "/skus/" + str(itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                                database.put("/log/" + uid + "/" + logYM,
                                             "/skus/" + str(itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                             numsold)
                            else:
                                numsold = int(itms[dispKeys[itmX]]["qty"])
                                rev = (float(itms[dispKeys[itmX]]["qty"]) * float(itms[dispKeys[itmX]]["price"]))
                                database.put("/log/" + uid + "/" + logYM,
                                             "/skus/" + str(itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                                database.put("/log/" + uid + "/" + logYM,
                                             "/skus/" + str(itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                             numsold)
                        wrtStr = ""
                        if (str(itms[dispKeys[itmX]]["size"]).lower() != "u"):
                            wrtStr += str(itms[dispKeys[itmX]]["size"])
                            wrtStr += " "
                            #print(wrtStr)
                            #print(str(itms[dispKeys[itmX]]["size"]))
                            wrtStr += str(itms[dispKeys[itmX]]["name"])
                            wrtStr += " "
                            wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                            wrtStr += " "
                            wrtStr += str(itms[dispKeys[itmX]]["notes"])
                            wrtStr += " x "
                            wrtStr += str(itms[dispKeys[itmX]]["qty"])
                            wrtStr += " $"
                            wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                            #print(wrtStr)
                            finalOrd += wrtStr + " :: "
                            skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                            for skk in range(len(skuKeyItm)):
                                currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                                for mmn in range(len(menuItems)):
                                    if (menuItems[mmn] != None):
                                        if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn]["descrip"] != "REMOVEDITM!"):
                                            if (str(menuItems[mmn]["extras"][0][0]) == str(currentSkuItm)):
                                                discAmt = menuItems[mmn]["extras"][0][1]
                                                limit = int(menuItems[mmn]["extras"][1][1])
                                                cpnUsed = int(
                                                    database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                                 "/discUsed/"))
                                                discTotal = float(
                                                    database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                                 "/discTotal/"))
                                                if (cpnUsed <= limit):
                                                    try:
                                                        float(discAmt)
                                                        discAmtflt = float(discAmt)
                                                        while cpnUsed < limit and cpnUsed < int(
                                                                itms[dispKeys[itmX]]["qty"]):
                                                            discTotal -= discAmtflt
                                                            cpnUsed += 1
                                                    except ValueError:
                                                        discAmt = discAmt[:-1]
                                                        discAmtflt = float(discAmt)
                                                        while cpnUsed < limit and cpnUsed < int(
                                                                itms[dispKeys[itmX]]["qty"]):
                                                            discTotal -= (float(discAmtflt) * (
                                                                        (float(itms[dispKeys[itmX]]["price"])) / float(
                                                                    itms[dispKeys[itmX]]["qty"])))
                                                            cpnUsed += 1
                                                    database.put(
                                                        "/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                        "/discUsed/", cpnUsed)
                                                    database.put(
                                                        "/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                        "/discTotal/", discTotal)
                                                    database.put(
                                                        "/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                        "/discStr/", str(
                                                            str(menuItems[mmn]["name"]) + " x " + str(
                                                                cpnUsed) + " -$" + str(float(discTotal * -1))))

                                                    finalOrd += menuItems[mmn]["name"] + " x " + str(
                                                        cpnUsed) + " -$" + str(round((discTotal * -1), 2)) + " :: "
                                                    break
                        else:
                            wrtStr = str(itms[dispKeys[itmX]]["name"])
                            wrtStr += " "
                            wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                            wrtStr += " "
                            wrtStr += str(itms[dispKeys[itmX]]["notes"])
                            wrtStr += " x "
                            wrtStr += str(itms[dispKeys[itmX]]["qty"])
                            wrtStr += " $"
                            wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                            #print(wrtStr)
                            finalOrd += wrtStr + " :: "
                            skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                            for skk in range(len(skuKeyItm)):
                                currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                                for mmn in range(len(menuItems)):
                                    if (menuItems[mmn] != None):
                                        if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn]["descrip"] != "REMOVEDITM!"):
                                            if (str(menuItems[mmn]["extras"][0][0]) == str(currentSkuItm)):
                                                discAmt = menuItems[mmn]["extras"][0][1]
                                                limit = int(menuItems[mmn]["extras"][1][1])
                                                cpnUsed = int(
                                                    database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                                 "/discUsed/"))
                                                discTotal = float(
                                                    database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                                 "/discTotal/"))
                                                if (cpnUsed <= limit):
                                                    try:
                                                        float(discAmt)
                                                        discAmtflt = float(discAmt)
                                                        while cpnUsed < limit and cpnUsed < int(
                                                                itms[dispKeys[itmX]]["qty"]):
                                                            discTotal -= discAmtflt
                                                            cpnUsed += 1
                                                    except ValueError:
                                                        discAmt = discAmt[:-1]
                                                        discAmtflt = float(discAmt)
                                                        while cpnUsed < limit and cpnUsed < int(
                                                                itms[dispKeys[itmX]]["qty"]):
                                                            discTotal -= (float(discAmtflt) * float(
                                                                itms[dispKeys[itmX]]["price"]))
                                                            cpnUsed += 1
                                                    database.put(
                                                        "/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                        "/discUsed/", cpnUsed)
                                                    database.put(
                                                        "/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                        "/discTotal/", discTotal)
                                                    database.put(
                                                        "/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                        "/discStr/", str(
                                                            str(menuItems[mmn]["name"]) + " x " + str(
                                                                cpnUsed) + " -$" + str(float(discTotal * -1))))
                                                    finalOrd += menuItems[mmn]["name"] + " x " + str(
                                                        cpnUsed) + " -$" + str(round((discTotal * -1), 2)) + " :: "
                                                    break
                except KeyError:
                    #print("exec")
                    pass
            #print(finalOrd)
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "finalOrder/", finalOrd)
            #print("final put")
            DBdata = database.get("/restaurants/" + estName, "orders")
            subTotal = float(DBdata[key]["linkTotal"])
            subTotal += DBdata[dbItems]["discTotal"]
            Tax = str(round((float(subTotal * 0.1), 2)))
            Total = str(round((float(subTotal) + float(Tax) + 0.15), 2))
            link = str(genPayment(str(Total), "", UUID))
            session.clear()
            return redirect(link)
    else:
        authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                         'cajohn0205@gmail.com', extra={'id': 123})
        database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/",
                                                authentication=authentication)
        itms = database.get("/restaurants/" + estName + "/orders/" + str(key), "/item/")
        finalOrd = ""
        if (itms != None):
            finalOrd = ""
            dispKeys = list(itms.keys())
            for itmX in range(len(dispKeys)):
                wrtStr = ""
                if (str(itms[dispKeys[itmX]]["size"]).lower() != "u"):
                    wrtStr += str(itms[dispKeys[itmX]]["size"])
                    wrtStr += " "
                    #print(wrtStr)
                    #print(str(itms[dispKeys[itmX]]["size"]))
                    wrtStr += str(itms[dispKeys[itmX]]["name"])
                    wrtStr += " "
                    wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                    wrtStr += " "
                    wrtStr += str(itms[dispKeys[itmX]]["notes"])
                    wrtStr += " x "
                    wrtStr += str(itms[dispKeys[itmX]]["qty"])
                    wrtStr += " $"
                    wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                    #print(wrtStr)
                    finalOrd += wrtStr + " :: "
                    skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                    for skk in range(len(skuKeyItm)):
                        currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                        for mmn in range(len(menuItems)):
                            if (menuItems[mmn] != None):
                                if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn]["descrip"] != "REMOVEDITM!"):
                                    if (str(menuItems[mmn]["extras"][0][0]) == str(currentSkuItm)):
                                        discAmt = menuItems[mmn]["extras"][0][1]
                                        limit = int(menuItems[mmn]["extras"][1][1])
                                        cpnUsed = int(database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                                   "/discUsed/"))
                                        discTotal = float(
                                            database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                         "/discTotal/"))
                                        if (cpnUsed <=
                                                limit):
                                            try:
                                                float(discAmt)
                                                discAmtflt = float(discAmt)
                                                while cpnUsed < limit and cpnUsed < int(itms[dispKeys[itmX]]["qty"]):
                                                    discTotal -= discAmtflt
                                                    cpnUsed += 1
                                            except ValueError:
                                                discAmt = discAmt[:-1]
                                                discAmtflt = float(discAmt)
                                                while cpnUsed < limit and cpnUsed < int(itms[dispKeys[itmX]]["qty"]):
                                                    discTotal -= (float(discAmtflt) * float(
                                                        itms[dispKeys[itmX]]["price"]))
                                                    #print(discTotal)
                                                    cpnUsed += 1
                                            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                         "/discUsed/", cpnUsed)
                                            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                         "/discTotal/", discTotal)
                                            database.put(
                                                "/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                "/discStr/", str(
                                                    str(menuItems[mmn]["name"]) + " x " + str(
                                                        cpnUsed) + " -$" + str(float(discTotal * -1))))
                                            finalOrd += menuItems[mmn]["name"] + " x " + str(cpnUsed) + " -$" + str(
                                                round((
                                                        discTotal * -1), 2)) + " :: "
                                            break

                else:
                    wrtStr = str(itms[dispKeys[itmX]]["name"])
                    wrtStr += " "
                    wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                    wrtStr += " "
                    wrtStr += str(itms[dispKeys[itmX]]["notes"])
                    wrtStr += " x "
                    wrtStr += str(itms[dispKeys[itmX]]["qty"])
                    wrtStr += " $"
                    wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                    #print(wrtStr)
                    finalOrd += wrtStr + " :: "
                    skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                    for skk in range(len(skuKeyItm)):
                        currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                        for mmn in range(len(menuItems)):
                            if (menuItems[mmn] != None):
                                if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn]["descrip"] != "REMOVEDITM!"):
                                    if (str(menuItems[mmn]["extras"][0][0]) == str(currentSkuItm)):
                                        discAmt = menuItems[mmn]["extras"][0][1]
                                        limit = int(menuItems[mmn]["extras"][1][1])
                                        cpnUsed = int(database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                                   "/discUsed/"))
                                        discTotal = float(
                                            database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                         "/discTotal/"))
                                        if (cpnUsed <= limit):
                                            try:
                                                float(discAmt)
                                                discAmtflt = float(discAmt)
                                                while cpnUsed < limit and cpnUsed < int(itms[dispKeys[itmX]]["qty"]):
                                                    discTotal -= discAmtflt
                                                    cpnUsed += 1
                                            except ValueError:
                                                discAmt = discAmt[:-1]
                                                discAmtflt = float(discAmt)
                                                while cpnUsed < limit and cpnUsed < int(itms[dispKeys[itmX]]["qty"]):
                                                    #print(discAmtflt, "effee")
                                                    discTotal -= (float(discAmtflt) * float(
                                                        itms[dispKeys[itmX]]["price"]))
                                                    #print(discTotal)
                                                    cpnUsed += 1
                                            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                         "/discUsed/", cpnUsed)
                                            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                         "/discTotal/", discTotal)
                                            database.put(
                                                "/restaurants/" + estName + "/orders/" + str(key) + "/",
                                                "/discStr/", str(
                                                    str(menuItems[mmn]["name"]) + " x " + str(
                                                        cpnUsed) + " -$" + str(float(discTotal * -1))))
                                            finalOrd += menuItems[mmn]["name"] + " x " + str(cpnUsed) + " -$" + str(
                                                round((
                                                        discTotal * -1), 2)) + " :: "
                                            break
                if (itms[dispKeys[itmX]] != None):
                    #print(itms[dispKeys[itmX]])
                    skuKeys = list(itms[dispKeys[itmX]]["skus"].keys())
                    for sk in range(len(skuKeys)):
                        currentSku = database.get("/log/" + estName + "/" + str(logYM) + "/" + "skus/",
                                                  itms[dispKeys[itmX]]["skus"][skuKeys[sk]])
                        if (currentSku != None):
                            numsold = currentSku["numSold"] + int(itms[dispKeys[itmX]]["qty"])
                            rev = currentSku["rev"] + (
                                    float(itms[dispKeys[itmX]]["qty"]) * float(itms[dispKeys[itmX]]["price"]))
                            database.put("/log/" + uid + "/" + logYM,
                                         "/skus/" + str(itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                            database.put("/log/" + uid + "/" + logYM,
                                         "/skus/" + str(itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                         numsold)
                        else:
                            numsold = int(itms[dispKeys[itmX]]["qty"])
                            rev = (float(itms[dispKeys[itmX]]["qty"]) * float(itms[dispKeys[itmX]]["price"]))
                            database.put("/log/" + uid + "/" + logYM,
                                         "/skus/" + str(itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                            database.put("/log/" + uid + "/" + logYM,
                                         "/skus/" + str(itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                         numsold)

        #print(finalOrd)
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "finalOrder/", finalOrd)
        #print(finalOrd, "put")
        DBdata = database.get("/restaurants/" + estName, "orders")
        duration = time.time() - float(DBdata[dbItems]["startTime"])
        subTotal = float(DBdata[key]["linkTotal"])
        subTotal += DBdata[dbItems]["discTotal"]
        Total = round(((subTotal + 0.15) * 1.1), 2)
        numItms = len(DBdata[dbItems]["item"])
        orderIndx = DBdata[dbItems]["orderIndx"]
        usrIndx = DBdata[dbItems]["userIndx"]
        database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(orderIndx) + "/", "total",
                     Total)
        database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(orderIndx) + "/", "tickSize",
                     numItms)
        database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(orderIndx) + "/", "items",
                     DBdata[dbItems]["item"])
        database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(orderIndx) + "/", "duration",
                     duration)
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "finalOrder/", finalOrd)
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "tickSize/", numItms)
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "filled/", "1")
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "number/", str((number) + "."))
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "endTime/", time.time())
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "duration/", duration)
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/day/",
                     calendar.day_name[datetime.datetime.now().today().weekday()])
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/hour/",
                     int(datetime.datetime.now().hour))
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/month/",
                     (datetime.datetime.now().strftime("%m")))
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/date/",
                     (datetime.datetime.now().strftime("%d")))
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/year/",
                     (datetime.datetime.now().strftime("%Y")))
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "cash/", "NOT PAID")
        logData = database.get("/log/" + uid + "/", logYM)
        cdrFees = logData['CedarFees']
        cdrFees += 0.1
        database.put("/log/" + uid + "/" + logYM, "/CedarFees/", cdrFees)
        totalRev = float(logData["totalRev"])
        totalRev += float((DBdata[dbItems]["linkTotal"] + 0.15) * 1.1)
        database.put("/log/" + uid + "/" + logYM, "/totalRev/", totalRev)
        ret = int(logData["retCustomers"])
        newCust = int(logData["newCustomers"])
        if (DBdata[dbItems]["ret"] == 0):
            ret += 1
            database.put("/log/" + uid + "/" + logYM, "/retCustomers/", ret)
        else:
            newCust += 1
            database.put("/log/" + uid + "/" + logYM, "/newCustomers/", newCust)
        reply = "-Thank you for your order, you can pick it up and pay at the counter when you arrive \n-To order again just text " + '"order"'
        updateLog()
        client.send_message({
            'from': NexmoNumber,
            'to': number,
            'text': reply
        })
        session.clear()
        return render_template("thankMsg.html")


@application.route('/')
@application.route('/index')
def mainPage():
    return " "


# when you run the code through terminal, this will allow Flask to work
if __name__ == '__main__':
    application.secret_key = 'ssKEY'
    application.config['SESSION_TYPE'] = 'filesystem'
    sess = Session()
    sess.init_app(application)
    application.debug = True
    application.run(host="0.0.0.0")
