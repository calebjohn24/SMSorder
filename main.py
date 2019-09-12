import calendar
import datetime
import json
import random
import smtplib
import time
import requests
import pandas as pd
import plivo
import pygsheets
import pyrebase as fbAuth
import pytz
import stripe
import dateparser
from flask import Flask, request, session
from flask import redirect, url_for
from flask import render_template
from flask_session import Session
from flask_sslify import SSLify
from fpdf import FPDF
from werkzeug.datastructures import ImmutableOrderedMultiDict
from firebase import firebase
import sys
sessionTime = 1000
infoFile = open("info.json")
info = json.load(infoFile)
uid = info['uid']
gc = pygsheets.authorize(service_file='static/CedarChatbot-70ec2d781527.json')
email = "cedarchatbot@appspot.gserviceaccount.com"
estName = info['uid']
estNameStr = info['name']
botNumber = info["number"]
payaplEmail = info['paypalEmail']
timez = info["timezone"]
mainLink = info['mainLink']
stripeToken = info['stripe']
tz = pytz.timezone(timez)
print(datetime.datetime.now(tz))
client = plivo.RestClient(auth_id='MAYTVHN2E1ZDY4ZDA2YZ', auth_token='ODgzZDA1OTFiMjE2ZTRjY2U4ZTVhYzNiODNjNDll')
mainLink = ""
authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W', 'cajohn0205@gmail.com',
                                                 extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})

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
databse = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
promoPass = "promo-" + str(estName)
addPass = "add-" + str(estName)
remPass = "remove-" + str(estName)
fontName = "helvetica"
smsTest = "sms:13166009096?body=order"
sh = gc.open('TestRaunt')
linkOrderLong = "cedarrestaurants.us-east-2.elasticbeanstalk.com" + uid + "check"
webLink = "sms:+" + botNumber + "?body=order"
sender = 'receipts@cedarrobots.com'
emailPass = "Cedar2421!"
smtpObj = smtplib.SMTP_SSL("smtp.zoho.com", 465)
smtpObj.login(sender, emailPass)
app = Flask(__name__)
sslify = SSLify(app)
app.secret_key = 'CedarKey02'


def updatelogDay():
    logYM = (datetime.datetime.now(tz).strftime("%Y-%m-%d"))
    try:
        wks = sh.worksheet_by_title(logYM + "-sales")
        logData = database.get("/log/" + uid + "/", logYM)
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        numOrders = (len(database.get("/restaurants/" + estName, "/orders/")) - 1)
        totalDF = pd.DataFrame()
        totalArr = []
        cdrFees = logData['CedarFees']
        totalArr.append(cdrFees)
        totalRev = logData['totalRev']
        totalArr.append(totalRev)
        numOrders = (len(database.get("/restaurants/" + estName, "/orders/")) - 1)
        totalArr.append(numOrders)
        newCust = logData['newCustomers']
        totalArr.append(newCust)
        retCust = logData['retCustomers']
        totalArr.append(retCust)
        pFees = logData['postmatesFees']
        totalArr.append(pFees)
        totalDF = pd.DataFrame()
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
                                        # print("found ex")
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
    except Exception:
        wks = sh.add_worksheet(str(logYM) + "-sales", rows=50, cols=60)
        header = wks.cell('A1')
        header.value = 'SKU'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('B1')
        header.value = 'NAME'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('C1')
        header.value = 'REVENUE'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('D1')
        header.value = 'NUMBER SOLD'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('E2')
        header.value = 'Cedar Fees'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('E3')
        header.value = 'Revenue'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('E4')
        header.value = 'Number of Orders'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('E5')
        header.value = 'New Customer'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('E5')
        header.value = 'Returning Customers'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('F1')
        header.value = 'Totals'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        logData = database.get("/log/" + uid + "/", logYM)
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        numOrders = (len(database.get("/restaurants/" + estName, "/orders/")) - 1)
        totalDF = pd.DataFrame()
        totalArr = []
        cdrFees = logData['CedarFees']
        totalArr.append(cdrFees)
        totalRev = logData['totalRev']
        totalArr.append(totalRev)
        numOrders = (len(database.get("/restaurants/" + estName, "/orders/")) - 1)
        totalArr.append(numOrders)
        newCust = logData['newCustomers']
        totalArr.append(newCust)
        retCust = logData['retCustomers']
        totalArr.append(retCust)
        totalDF = pd.DataFrame()
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
                            if (skuKeys[sk] == str(menuItems[men]["sizes"][sz][2]) and skuKeys[sk] != "-"):
                                # print("found size")
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
                                        # print("found ex")
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

def updateLog():
    logYM = (datetime.datetime.now(tz).strftime("%Y-%m"))
    sh = gc.open('TestRaunt')
    try:
        wks = sh.worksheet_by_title(logYM + "-sales")
        logData = database.get("/log/" + uid + "/", logYM)
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        numOrders = (len(database.get("/restaurants/" + estName, "/orders/")) - 1)
        totalDF = pd.DataFrame()
        totalArr = []
        cdrFees = logData['CedarFees']
        totalArr.append(cdrFees)
        totalRev = logData['totalRev']
        totalArr.append(totalRev)
        numOrders = (len(database.get("/restaurants/" + estName, "/orders/")) - 1)
        totalArr.append(numOrders)
        newCust = logData['newCustomers']
        totalArr.append(newCust)
        retCust = logData['retCustomers']
        totalArr.append(retCust)
        totalDF = pd.DataFrame()
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
                                        # print("found ex")
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
    except Exception:
        wks = sh.add_worksheet(str(logYM)+"-sales", rows=50, cols=60)
        header = wks.cell('A1')
        header.value = 'SKU'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('B1')
        header.value = 'NAME'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('C1')
        header.value = 'REVENUE'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('D1')
        header.value = 'NUMBER SOLD'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('E2')
        header.value = 'Cedar Fees'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('E3')
        header.value = 'Revenue'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('E4')
        header.value = 'Number of Orders'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('E5')
        header.value = 'New Customer'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('E5')
        header.value = 'Returning Customers'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        header = wks.cell('F1')
        header.value = 'Totals'
        header.text_format['bold'] = True  # make the header bold
        header.update()
        logData = database.get("/log/" + uid + "/", logYM)
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        numOrders = (len(database.get("/restaurants/" + estName, "/orders/")) - 1)
        totalDF = pd.DataFrame()
        totalArr = []
        cdrFees = logData['CedarFees']
        totalArr.append(cdrFees)
        totalRev = logData['totalRev']
        totalArr.append(totalRev)
        numOrders = (len(database.get("/restaurants/" + estName, "/orders/")) - 1)
        totalArr.append(numOrders)
        newCust = logData['newCustomers']
        totalArr.append(newCust)
        retCust = logData['retCustomers']
        totalArr.append(retCust)
        totalDF = pd.DataFrame()
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
                            if (skuKeys[sk] == str(menuItems[men]["sizes"][sz][2]) and skuKeys[sk] != "-"):
                                # print("found size")
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
                                        # print("found ex")
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
    updatelogDay()


def genUsr(name, number, dbIndx):
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    UserData = database.get("/", "/users/")
    timeStamp = datetime.datetime.today()
    database.put("/users/", "/" + str(len(UserData)) + "/name", name)
    database.put("/users/", "/" + str(len(UserData)) + "/number", number)
    database.put("/users/","/" + str(len(UserData)) + "/restaurants/" + estNameStr + "/" + str(0) + "/StartTime",
                 str(timeStamp))
    database.put("/users/", "/" + str(len(UserData)) + "/loyalty/" + str(0) + "/name/",
                 estNameStr)
    database.put("/users/", "/" + str(len(UserData)) + "/loyalty/" + str(0) + "/points/", 0)
    database.put("/restaurants/" + estName + "/orders/" + str(dbIndx) + "/", "/usrIndx/", len(UserData))


def getReply(msg, number):
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    currentTime = str((float(datetime.datetime.now(tz).hour)) + ((float(datetime.datetime.now(tz).minute)) / 100.0))
    day = datetime.datetime.today().weekday()
    startHr = float(database.get("restaurants/" + uid, "/OChrs/" + str(day) + "/open/"))
    endHr = float(database.get("restaurants/" + uid, "/OChrs/" + str(day) + "/close/"))
    if (startHr <= float(currentTime) < endHr):
        msg = msg.lower()
        msg.replace("\n", "")
        msg.replace(".", "")
        msg.replace(" ", "")
        msg = ''.join(msg.split())
        DBdata = database.get("/restaurants/" + estName, "/orders")
        UserData = database.get("/restaurants/", uid + "/users")
        if (msg == "order" or msg == "ordew" or msg == "ord" or msg == "ordet" or msg == "oderr" or msg == "ordee" or (
                "ord" in msg)):
            UUID = random.randint(9999999, 100000000)
            for dbxv in range(len(DBdata)):
                try:
                    if (DBdata[dbxv]["number"] == number):
                        database.put("/restaurants/" + estName + "/orders/" + str(dbxv) + "/", "/number/",
                                     str(number) + ".")
                except KeyError:
                    pass
            tickData = {
                "UUID":str(UUID),
                "name":"",
                "stage":1,
                "paid":0,
                "kiosk":0,
                "giftcard":0,
                "cash":"",
                "togo":"",
                "tickSize":0,
                "discUsed":0,
                "discTotal":0.0,
                "discStr":"",
                "filled":0,
                "linkTotal":0,
                "finalOrder":"",
                "startTime": float(time.time()),
                "number":str(number)
            }
            database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)), "/", tickData)
            UserData = database.get("/", "users")
            for usr in range(len(UserData)):
                if (number == UserData[usr]["number"]):
                    timeStamp = datetime.datetime.today()
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
                    linkOrder = database.get("/restaurants/" + estName, "/orderLink")
                    reply = "Hi welcome! click the link below to view the menu and order " + str(linkOrder)
                    return reply
                if ((len(UserData) - usr) == 1):
                    genUsr("", number, (len(DBdata)))
                    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/userIndx/",
                                 (len(UserData)))
                    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/orderIndx/",
                                 0)
                    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)) + "/", "/ret/", 1)
                    linkOrder = database.get("/restaurants/" + estName, "/orderLink")
                    reply = "Hi welcome! click the link below to view the menu and order " + str(linkOrder)
                    return reply
        else:
            return ("no msg")
    else:
        return ("no msg")


@app.route('/sms')
def inbound_sms():
    # Sender's phone number

    from_number = request.values.get('From')
    # Receiver's phone number - Plivo number
    to_number = request.values.get('To')
    # The text which was received
    text = request.values.get('Text')
    print('Message received - From: %s, To: %s, Text: %s' % (from_number, to_number, text))
    resp = getReply(text, from_number)
    print(str(resp))
    if (resp != "no msg"):
        client.messages.create(
            src=botNumber,
            dst=from_number,
            text=resp
        )
    return '200'

@app.route('/failed', methods=['POST'])
def transactionFailed():
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = request.json
    print(rsp)
    if(rsp['data']['object']['description'][0] == "G"):
        code = rsp['data']['object']['description'][3:]
        database.put("/restaurants/" + estName + "/giftcards/" + str(code), "/" + str("usedVal") + "/", -2)
        return "200"
    DBdata = database.get("/restaurants/" + estName, "orders")
    for dbItems in range(len(DBdata)):
        if (str(DBdata[dbItems]["UUID"]) == rsp['data']['object']['description']):
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems), "/" + str("filled") + "/", "100")
            return "200"


@app.route('/ipn', methods=['POST'])
def ipn():
    logYM = (datetime.datetime.now(tz).strftime("%Y-%m"))
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = request.json
    if(rsp['data']['object']['description'][0] == "G"):
        if (rsp['data']['object']['outcome']["risk_score"] > 65 or rsp['data']['object']["source"]["address_zip_check"] != "pass"):
            code = rsp['data']['object']['description'][3:]
            print(code)
            database.put("/restaurants/" + estName + "/giftcards/" + str(code), "/" + str("usedVal") + "/", -2)
        else:
            code = rsp['data']['object']['description'][3:]
            print(code)
            database.put("/restaurants/" + estName + "/giftcards/" + str(code), "/" + str("usedVal") + "/", 0.0)
        return "200"
    DBdata = database.get("/restaurants/" + estName, "orders")
    for dbItems in range(len(DBdata)):
        if (str(DBdata[dbItems]["UUID"]) == str(rsp['data']['object']['description'])):
            if(rsp['data']['object']['outcome']["risk_score"] > 65 or rsp['data']['object']["source"]["address_zip_check"] != "pass"):
                database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/filled/", "100")
                return "200"
            else:
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
                             calendar.day_name[datetime.datetime.now(tz).today().weekday()])
                database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/hour/",
                             int(datetime.datetime.now(tz).hour))
                database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/month/",
                             (datetime.datetime.now(tz).strftime("%m")))
                database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/date/",
                             (datetime.datetime.now(tz).strftime("%d")))
                database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/year/",
                             (datetime.datetime.now(tz).strftime("%Y")))
                numOrders = database.get("/users/" + str(usrIndx) + "/restaurants/", estNameStr)
                logData = database.get("/log/" + uid + "/", logYM)
                if (logData == None):
                    database.put("/log/" + uid + "/" + logYM, "/newCustomers/", 0)
                    database.put("/log/" + uid + "/" + logYM, "/retCustomers/", 0)
                    database.put("/log/" + uid + "/" + logYM, "/CedarFees/", 0.0)
                    database.put("/log/" + uid + "/" + logYM, "/totalRev/", 0.0)
                    database.put("/log/" + uid + "/" + logYM, "/postmatesFees/", 0.0)
                    database.put("/log/" + uid + "/" + logYM, "/skus/-/numSold", 0)
                    database.put("/log/" + uid + "/" + logYM, "/skus/-/rev", 0)
                logData = database.get("/log/" + uid + "/", logYM)
                cdrFees = logData['CedarFees']
                cdrFees += 1
                database.put("/log/" + uid + "/" + logYM, "/CedarFees/", cdrFees)
                itms = database.get("/restaurants/" + estName + "/orders/" + str(dbItems), "/item/")
                if (itms != None):
                    finalOrd = ""
                    dispKeys = list(itms.keys())
                    for itmX in range(len(dispKeys)):
                        try:
                            if (itms[dispKeys[itmX]] != None):
                                # print(itms[dispKeys[itmX]])
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
                        except KeyError:
                            pass
                totalRev = float(logData["totalRev"])
                totalRev += float((DBdata[dbItems]["linkTotal"] + 1) * 1.1)
                ret = int(logData["retCustomers"])
                newCust = int(logData["newCustomers"])
                if (DBdata[dbItems]["ret"] == 0):
                    ret += 1
                    database.put("/log/" + uid + "/" + logYM, "/retCustomers/", ret)
                else:
                    newCust += 1
                    database.put("/log/" + uid + "/" + logYM, "/newCustomers/", newCust)
                database.put("/log/" + uid + "/" + logYM, "/totalRev/", totalRev)
                logYM = (datetime.datetime.now(tz).strftime("%Y-%m-%d"))
                logData = database.get("/log/" + uid + "/", logYM)
                if (logData == None):
                    database.put("/log/" + uid + "/" + logYM, "/newCustomers/", 0)
                    database.put("/log/" + uid + "/" + logYM, "/retCustomers/", 0)
                    database.put("/log/" + uid + "/" + logYM, "/CedarFees/", 0.0)
                    database.put("/log/" + uid + "/" + logYM, "/totalRev/", 0.0)
                    database.put("/log/" + uid + "/" + logYM, "/postmatesFees/", 0.0)
                    database.put("/log/" + uid + "/" + logYM, "/skus/-/numSold", 0)
                    database.put("/log/" + uid + "/" + logYM, "/skus/-/rev", 0)
                logData = database.get("/log/" + uid + "/", logYM)
                cdrFees = logData['CedarFees']
                cdrFees += 1
                database.put("/log/" + uid + "/" + logYM, "/CedarFees/", cdrFees)
                itms = database.get("/restaurants/" + estName + "/orders/" + str(dbItems), "/item/")
                if (itms != None):
                    finalOrd = ""
                    dispKeys = list(itms.keys())
                    for itmX in range(len(dispKeys)):
                        try:
                            if (itms[dispKeys[itmX]] != None):
                                # print(itms[dispKeys[itmX]])
                                skuKeys = list(itms[dispKeys[itmX]]["skus"].keys())
                                for sk in range(len(skuKeys)):
                                    currentSku = database.get("/log/" + estName + "/" + str(logYM) + "/" + "skus/",
                                                              itms[dispKeys[itmX]]["skus"][skuKeys[sk]])
                                    if (currentSku != None):
                                        numsold = currentSku["numSold"] + int(itms[dispKeys[itmX]]["qty"])
                                        rev = currentSku["rev"] + (
                                                float(itms[dispKeys[itmX]]["qty"]) * float(
                                            itms[dispKeys[itmX]]["price"]))
                                        database.put("/log/" + uid + "/" + logYM,
                                                     "/skus/" + str(
                                                         itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                                        database.put("/log/" + uid + "/" + logYM,
                                                     "/skus/" + str(
                                                         itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                                     numsold)
                                    else:
                                        numsold = int(itms[dispKeys[itmX]]["qty"])
                                        rev = (float(itms[dispKeys[itmX]]["qty"]) * float(
                                            itms[dispKeys[itmX]]["price"]))
                                        database.put("/log/" + uid + "/" + logYM,
                                                     "/skus/" + str(
                                                         itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                                        database.put("/log/" + uid + "/" + logYM,
                                                     "/skus/" + str(
                                                         itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                                     numsold)
                        except KeyError:
                            pass
                totalRev = float(logData["totalRev"])
                totalRev += float((DBdata[dbItems]["linkTotal"] + 1) * 1.1)
                database.put("/log/" + uid + "/" + logYM, "/totalRev/", totalRev)
                ret = int(logData["retCustomers"])
                newCust = int(logData["newCustomers"])
                if (DBdata[dbItems]["ret"] == 0):
                    ret += 1
                    database.put("/log/" + uid + "/" + logYM, "/retCustomers/", ret)
                else:
                    newCust += 1
                    database.put("/log/" + uid + "/" + logYM, "/newCustomers/", newCust)
                database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/zipCode/", rsp['data']['object']['billing_details']["address"]['postal_code'])
                numItms = len(DBdata[dbItems]["item"])
                orderIndx = DBdata[dbItems]["orderIndx"]
                usrIndx = DBdata[dbItems]["userIndx"]
                database.put("/users/" + str(usrIndx) + "/", "/zipCode/", rsp['data']['object']['billing_details']["address"]['postal_code'])
                database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                    orderIndx) + "/", "total",
                             ((DBdata[dbItems]["linkTotal"] + 0.1) * 1.1))
                database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                    orderIndx) + "/",
                             "tickSize",
                             numItms)
                database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                    orderIndx) + "/", "items",
                             DBdata[dbItems]["item"])
                database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                    orderIndx) + "/",
                             "duration",
                             duration)
                # print("sending")
                rec = DBdata[dbItems]['email']
                if(rec != ""):
                    smtpObj = smtplib.SMTP_SSL("smtp.zoho.com", 465)
                    smtpObj.login(sender, emailPass)
                    try:
                        subTotal = (DBdata[dbItems]["linkTotal"]) + DBdata[dbItems]["discTotal"]
                    except KeyError:
                        subTotal = (DBdata[dbItems]["linkTotal"])
                    Tax = float(subTotal * 0.1)
                    Total = float(subTotal + float(Tax) + 0.1)
                    subTotalStr = ('$' + format(subTotal, ',.2f'))
                    TotalStr = ('$' + format(Total, ',.2f'))
                    TaxStr = ('$' + format(Tax, ',.2f'))
                    # print(TotalStr)
                    itms = str(DBdata[dbItems]["finalOrder"])
                    itms = itms.replace("::", "\n-")
                    now = datetime.datetime.now(tz)
                    try:
                        if(DBdata[dbItems]["delivFee"] != None and DBdata[dbItems]["togo"] == "delivery"):
                            writeStr = "your order on " + str(now.strftime("%Y-%m-%d @ %H:%M")) + "\nNAME:" + str(
                                DBdata[dbItems]["name"]) + "\n\nItems\n-" + str(itms) + "\n" + str(
                                DBdata[dbItems]["discStr"]) + "\n" + str(DBdata[dbItems]["togo"]) +"fee $"+str(DBdata[dbItems]["delivFee"])+"\nSubtotal " + str(subTotalStr) + "\nTaxes and fees $" + str(round((Total - subTotal), 2)) + "\nTotal " + TotalStr
                    except Exception as e:
                        writeStr = "your order on " + str(now.strftime("%Y-%m-%d @ %H:%M")) + "\nNAME:" + str(
                            DBdata[dbItems]["name"]) + "\n\nItems\n-" + str(itms) + "\n" + str(
                            DBdata[dbItems]["discStr"]) \
                                   + "\n" + str(DBdata[dbItems]["togo"])+"\n" + str(DBdata[dbItems]["time"]) + "\nSubtotal " + str(subTotalStr) + "\nTaxes and fees $" + str(round((Total - subTotal), 2)) + "\nTotal " + TotalStr
                    SUBJECT = "Your Order from " + estNameStr
                    message = 'Subject: {}\n\n{}'.format(SUBJECT, writeStr)
                    smtpObj.sendmail(sender, rec, message)
                    smtpObj.close()
                    if(DBdata[dbItems]["togo"] == "delivery"):
                        client.messages.create(
                            src=botNumber,
                            dst=DBdata[dbItems]["number"],
                            text="Your order is being prepared, we'll send you a tracking link when your order is on the way"
                        )
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "number/", str((number) + "."))
            updateLog()
    return (" ", 200)


@app.route('/' + estNameStr, methods=['GET'])
def loginPage():
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/",
                                            authentication=authentication)
    database.put("/restaurants/" + uid + "/", "loginTime", 0)
    return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@app.route('/' + estNameStr, methods=['POST'])
def loginPageCheck():
    rsp = ((request.form))
    email = str(rsp["email"])
    pw = str(rsp["pw"])
    try:
        user = auth.sign_in_with_email_and_password(str(rsp["email"]), pw)
        # print(user['localId'])
        authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                         'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
        fireapp = firebase.FirebaseApplication('https://cedarchatbot.firebaseio.com/', authentication=authentication)
        testDB = (fireapp.get("/restaurants/", user["localId"]))
        if (str(user["localId"]) == str(uid) and testDB != None):
            # print("found")
            database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/",
                                                    authentication=authentication)
            database.put("/restaurants/" + uid + "/", "loginTime", time.time())
            return redirect(url_for('panel'))
        else:
            authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                             'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
            # print("incorrect password")
            database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/",
                                                    authentication=authentication)
            database.put("/restaurants/" + uid + "/", "loginTime", 0)
            return render_template("login2.html", btn=str(estNameStr), restName=estNameStr)
    except Exception:
        authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                         'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
        database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/",
                                                authentication=authentication)
        database.put("/restaurants/" + uid + "/", "loginTime", 0)
        # print("incorrect password")
        return render_template("login2.html", btn=str(estNameStr), restName=estNameStr)


@app.route('/' + uid, methods=['GET'])
def panel():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
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
            # print(links)
        return render_template("panel.html", len=len(links),gcard=(str(uid) + "giftcardadd"), menuLinks=links, menuNames=names, restName=estNameStr,
                               viewOrders=(uid + "view"), addItm=(addPass), remItms=remPass, addCpn=promoPass,
                               promoSMS=promoPass + "smsPromo" + uid,
                               signOut=estNameStr, outStck=str(uid + "outstock"),
                               robotDeploy=str(uid + "rbt4813083403983494103934093480943109834093091341"))
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@app.route('/' + uid + "view", methods=['GET'])
def view():
    orders = database.get("/restaurants/" + estName, "orders")
    webDataDisp = []
    keys = []
    # print(orders)
    for ords in range(len(orders)):
        try:
            filled = orders[ords]["filled"]
            # print(filled)
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
                # print(TotalStr)
                writeStr = str(orders[ords]["name"]) + "-" + str(orders[ords]["number"]) + " || " + str(
                    orders[ords]["finalOrder"]) + " " + str(
                    orders[ords]["discStr"]) \
                           + " || " + str(orders[ords]["togo"]) + " || " + str(orders[ords]["time"]) + " || " \
                                                                                                       "" + TotalStr + " || " + str(
                    orders[ords]["cash"])
                keys.append(UUID)
                # print(writeStr)
                webDataDisp.append(writeStr)
        except KeyError:
            # print("exec")
            pass
    return render_template("indexV.html", len=len(webDataDisp), webDataDisp=webDataDisp, keys=keys,
                           btn=str(uid + "view"), restName=estNameStr)

@app.route('/'+uid+"giftcardadd",methods=['GET'])
def addgiftcard():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    if ((currentTime - lastLogin) < sessionTime):
        return render_template("addgcard.html", btn=(str(uid) + "giftcardadd"))
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)

@app.route('/'+uid+"giftcardadd",methods=['POST'])
def addgiftcard1():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    if ((currentTime - lastLogin) < sessionTime):
        rsp = ((request.form))
        name = rsp["name"]
        amt = rsp["amt"]
        database.put("/restaurants/" + estName + "/giftcards/" + str(name) , "/"+str("actDate")+"/", (datetime.datetime.now(tz).strftime("%Y-%m-%d")))
        database.put("/restaurants/" + estName + "/giftcards/" + str(name) , "/" + str("startVal") + "/", float(amt))
        database.put("/restaurants/" + estName + "/giftcards/" + str(name) , "/" + str("usedVal") + "/", -1)
        session['name'] = name
        Total = float(amt) * 1.1
        Total = round(Total,2)
        return render_template("payGcard.html",Total=str(Total), btn=str(uid+"giftcard2add"),name=name)
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)

@app.route('/'+uid+"giftcard2add",methods=['POST'])
def addgiftcard2():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    if ((currentTime - lastLogin) < sessionTime):
        stripe.api_key = stripeToken
        token = request.form['stripeToken']  # Using Flask
        rsp = ((request.form))
        print(rsp)
        name = session.get('name', None)
        print(name)
        card = database.get("/restaurants/" + estName,"/giftcards/" + name+ "/")
        Total = float(card["startVal"])
        Total = Total * 1.1
        Total = round(Total, 2)
        Total = int(Total * 100)
        print(Total)
        try:
            stripe.Charge.create(
                amount=Total,
                currency='usd',
                description="GC"+"-"+name,
                source=token, )
        except Exception:
            return render_template("addgcardFailed.html", btn=str(uid + "giftcardadd"))
        if(card["usedVal"] == -2):
            database.put("/restaurants/" + estName + "/giftcards/" + name, "/" + str("usedVal") + "/", -1)
        while(card["usedVal"] == -1):
            card = database.get("/restaurants/" + estName, "/giftcards/" + name)
            print
            if(card["usedVal"] == 0.0):
                logYM = (datetime.datetime.now(tz).strftime("%Y-%m"))

                updateLog()
                session.clear()
                return render_template("addgcard2.html", btn=str(uid))
            if(card["usedVal"] == -2):
                return render_template("addgcardFailed.html", btn=str(uid+"giftcardadd"))
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)

@app.route('/' + uid + "view", methods=['POST'])
def view2():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    print(rsp)
    item = (rsp['item'])
    # print(item)
    orders = database.get("/restaurants/" + estName, "orders")
    webDataDisp = []
    keys = []
    # print(orders)
    for ords in range(len(orders)):
        UUID = orders[ords]["UUID"]
        if (item == UUID):
            database.put("/restaurants/" + estName + "/orders/" + str(ords) + "/", "/filled/", "2")
            if(orders[ords]["number"][-1] == "."):
                number = orders[ords]["number"][:-1]
            else:
                number = orders[ords]["number"]
            print(number)
            if (orders[ords]["togo"] == "to-go"):
                reply = "-Your Order is ready you can pick it up at the counter\n-To order again just text " + '"order"'
            elif(orders[ords]["togo"] == "delivery"):
                url = "https://api.postmates.com/v1/customers/cus_MMAQ2VmJNZAVOV/delivery_quotes"
                addrP = database.get("/restaurants/" + estName, "address")
                addrD = orders[ords]["addrs"]
                payload = {"dropoff_address":addrP,
                           "pickup_address":addrD}
                headers = {
                    'Content-Type': "application/x-www-form-urlencoded",
                    'Authorization': "Basic ODcwZWFiYWUtN2JiMS00MzZjLWFmNGEtMzNmYTJmZTc2ODhlOg==",
                    'User-Agent': "PostmanRuntime/7.16.3",
                    'Accept': "*/*",
                    'Cache-Control': "no-cache",
                    'Postman-Token': "55cc61b2-a3aa-42f1-81a9-62467b9199b1,a5cb9e3d-7d0c-4834-9cde-6220fb9962a7",
                    'Host': "api.postmates.com",
                    'Accept-Encoding': "gzip, deflate",
                    'Content-Length': "145",
                    'Cookie': "__cfduid=d3e5bcc883cf1529ae363dbc64fe257f61567815844",
                    'Connection': "keep-alive",
                    'cache-control': "no-cache"
                    }
                response = requests.request("POST", url, data=payload, headers=headers)
                resp = (response.json())
                print(resp)
                logYM = (datetime.datetime.now(tz).strftime("%Y-%m"))
                logData = database.get("/log/" + uid + "/", logYM)
                if (logData == None):
                    database.put("/log/" + uid + "/" + logYM, "/newCustomers/", 0)
                    database.put("/log/" + uid + "/" + logYM, "/retCustomers/", 0)
                    database.put("/log/" + uid + "/" + logYM, "/CedarFees/", 0.0)
                    database.put("/log/" + uid + "/" + logYM, "/postmatesFees/", 0.0)
                    database.put("/log/" + uid + "/" + logYM, "/totalRev/", 0.0)
                    database.put("/log/" + uid + "/" + logYM, "/skus/-/numSold", 0)
                    database.put("/log/" + uid + "/" + logYM, "/skus/-/rev", 0)
                logData = database.get("/log/" + uid + "/", logYM)
                pFees = logData['postmatesFees']
                fee = float(resp["fee"])
                pFees += fee/100.0
                database.put("/log/" + uid + "/" + logYM, "/postmatesFees/", pFees)
                logYM = (datetime.datetime.now(tz).strftime("%Y-%m-%d"))
                logData = database.get("/log/" + uid + "/", logYM)
                if (logData == None):
                    database.put("/log/" + uid + "/" + logYM, "/newCustomers/", 0)
                    database.put("/log/" + uid + "/" + logYM, "/retCustomers/", 0)
                    database.put("/log/" + uid + "/" + logYM, "/CedarFees/", 0.0)
                    database.put("/log/" + uid + "/" + logYM, "/postmatesFees/", 0.0)
                    database.put("/log/" + uid + "/" + logYM, "/totalRev/", 0.0)
                    database.put("/log/" + uid + "/" + logYM, "/skus/-/numSold", 0)
                    database.put("/log/" + uid + "/" + logYM, "/skus/-/rev", 0)
                logData = database.get("/log/" + uid + "/", logYM)
                pFees = logData['postmatesFees']
                fee = float(resp["fee"])
                fee = fee/100.0
                fee = fee - orders[ords]["delivFee"]
                pFees += fee
                database.put("/log/" + uid + "/" + logYM, "/postmatesFees/", pFees)
                url = "https://api.postmates.com/v1/customers/cus_MMAQ2VmJNZAVOV/deliveries"
                payload = {
                "dropoff_address":addrP,
                "pickup_address":addrD,
                "quote_id":str(resp["id"]),
                "manifest":orders[ords]["finalOrder"],
                "dropoff_phone_number":orders[ords]["number"][:-1],
                "pickup_phone_number":database.get("/restaurants/" + estName, "number2"),
                    "dropoff_name":estNameStr,
                'pickup_name':"TestRaunt",
                }
                headers = {
                    'Content-Type': "application/x-www-form-urlencoded",
                    'Authorization': "Basic ODcwZWFiYWUtN2JiMS00MzZjLWFmNGEtMzNmYTJmZTc2ODhlOg==",
                    'User-Agent': "PostmanRuntime/7.16.3",
                    'Accept': "*/*",
                    'Cache-Control': "no-cache",
                    'Postman-Token': "a8e2692f-f65e-4cfb-8658-25324016b7ca,b7421a2d-8b36-4c6e-acd2-ceb641458a58",
                    'Host': "api.postmates.com",
                    'Accept-Encoding': "gzip, deflate",
                    'Content-Length': "517",
                    'Cookie': "__cfduid=d3e5bcc883cf1529ae363dbc64fe257f61567815844",
                    'Connection': "keep-alive",
                    'cache-control': "no-cache",
                    }
                response = requests.request("POST", url, data=payload, headers=headers)
                rsp = (response.json())
                reply = "Your food is ready and your courier is on their way click here to track your order\n"+rsp["tracking_url"]
            else:
                reply = "-Your order is ready and will be delivered to your table shortly\n-To order again just text " + '"order"'
            client.messages.create(
                src=botNumber,
                dst=number,
                text=reply
            )
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
                # print(TotalStr)
                try:
                    writeStr = str(orders[ords]["name"]) + "-" + str(orders[ords]["number"]) + " || " + str(orders[ords]["finalOrder"]) + " " + str(orders[ords]["discStr"]) + " || " + str(orders[ords]["togo"]) + " || " + str(orders[ords]["time"]) + " || " + TotalStr + " || " + str(orders[ords]["cash"])
                    keys.append(UUID)
                    # print(writeStr)
                    webDataDisp.append(writeStr)
                except Exception:
                    pass
    return render_template("indexV.html", len=len(webDataDisp), webDataDisp=webDataDisp, keys=keys,
                           btn=str(uid + "view"))


@app.route('/' + uid + "outstock", methods=['GET'])
def outStockg():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    ##print()
    if ((currentTime - lastLogin) < sessionTime):
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        ##print(menuItems)
        names = []
        keys = []
        for men in range(len(menuItems)):
            if (menuItems[men]["descrip"] != "REMOVEDITM!"):
                dispStr = ""
                keys.append(men)
                if (menuItems[men]["time"] == "oos"):
                    dispStr += menuItems[men]["name"].lower()
                    dispStr += "-"
                    dispStr += "OUT OF STOCK"
                else:
                    dispStr += menuItems[men]["name"].lower()
                    dispStr += "-"
                    dispStr += "In Stock"
                names.append(dispStr)

        return render_template("remItems.html", len=len(names), names=names, keys=keys, btn=uid + "outstock")
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@app.route('/' + uid + "outstock", methods=['POST'])
def outStockp():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    if ((currentTime - lastLogin) < sessionTime):
        request.parameter_storage_class = ImmutableOrderedMultiDict
        rsp = ((request.form))
        item = int(rsp['item'])
        names = []
        keys = []
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        itx = menuItems[item]["time"]
        if (itx == "oos"):
            rm = menuItems[item]["rm"]
            database.put("/restaurants/" + estName + "/menu/items/" + str(item) + "/", "rm", "oos")
            database.put("/restaurants/" + estName + "/menu/items/" + str(item) + "/", "time", rm)
        else:
            database.put("/restaurants/" + estName + "/menu/items/" + str(item) + "/", "rm", itx)
            database.put("/restaurants/" + estName + "/menu/items/" + str(item) + "/", "time", "oos")
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        return redirect(url_for('panel'))
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@app.route('/' + remPass, methods=['GET'])
def removeItemsDisp():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    # print()
    if ((currentTime - lastLogin) < sessionTime):
        menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
        # print(menuItems)
        names = []
        keys = []
        for men in range(len(menuItems)):
            if (menuItems[men]["descrip"] != "REMOVEDITM!"):
                names.append(menuItems[men]["name"])
                keys.append(men)
        return render_template("remItems.html", len=len(names), names=names, keys=keys, btn=remPass)
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@app.route('/' + remPass, methods=['POST'])
def removeItems():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    if ((currentTime - lastLogin) < sessionTime):
        request.parameter_storage_class = ImmutableOrderedMultiDict
        rsp = ((request.form))
        item = int(rsp['item'])
        names = []
        keys = []
        database.put("/restaurants/" + estName + "/menu/items/" + str(item) + "/", "descrip", "REMOVEDITM!")
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
                                                         'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
        database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
        menu = (database.get("restaurants/" + uid, "/menu/items/"))
        hours = (database.get("restaurants/" + uid, "/Hours/"))
        # print(hours)
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
                        # print(name)
                        # print(menu[dt]["time"], str([keys[menuNames]][0]))
                        # print(menu[dt]["time"] == str([keys[menuNames]][0]))
                        # print(str(menu[dt]["time"]).lower() == "all")
                        # print("\n")
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
            # print("\n")
        return redirect(url_for('panel'))
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@app.route('/' + addPass, methods=['GET'])
def addItmDisp():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    # print()
    if ((currentTime - lastLogin) < sessionTime):
        return render_template('addform.html', btn=addPass, restName=estNameStr)
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@app.route('/' + addPass, methods=['POST'])
def addItmForm():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    # print()
    if ((currentTime - lastLogin) < sessionTime):
        request.parameter_storage_class = ImmutableOrderedMultiDict
        rsp = ((request.form))
        name = str(rsp['name']).lower()
        numSizes = int(rsp['numSizes'])
        menTime = str(rsp['time']).lower()
        descrip = str(rsp['desc']).lower() + " "
        cat = str(rsp['category']).lower()+ " "
        warnings = str(rsp['warnings']).lower()
        # print(name)
        # print(numSizes)
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
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/cat/", cat)
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/war/", warnings)
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/rm/", "")
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


@app.route('/' + addPass + "2", methods=['POST'])
def addItmResp2():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
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


@app.route('/' + addPass + "3", methods=['GET'])
def addItmForm3():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
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


@app.route('/' + addPass + "3", methods=['POST'])
def addItmResp3():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    # print()
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
                        warn = rsp[str(sse) + "c"]
                        database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse),
                                     "/0/",
                                     exName)
                        database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse),
                                     "/1/", float(exPrice))
                        database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse),
                                     "/2/", str(sku))
                        database.put("/restaurants/" + estName + "/menu/items/" + str(sx) + "/extras/" + str(sse),
                                     "/3/", str(sku))
                    database.put("/restaurants/" + estName + "/menu/items/" + str(sx), "/inp/", "")
                    menu = (database.get("restaurants/" + uid, "/menu/items/"))
                    break
        # select the first sheet
        startHr = 0
        endHr = 0
        authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                         'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
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
            # print(fileName)
            pdf.output(fileName)
            storage = firebaseAuth.storage()
            storage.child(estNameStr + "/" + fileName).put(fileName)
            # print("\n")
        return redirect(url_for('panel'))
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@app.route('/' + promoPass, methods=['GET'])
def addCpn():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    # print()
    if ((currentTime - lastLogin) < sessionTime):
        return render_template('coupon.html', restName=estNameStr)
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@app.route('/' + promoPass + "smsPromo" + uid, methods=['GET'])
def smsPromo():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    if ((currentTime - lastLogin) < sessionTime):
        numPromos = len(database.get("/restaurants/" + estName, "/promos/"))
        lim = int(database.get("/restaurants/" + estName, "/promoLim/"))
        print(lim)
        if (numPromos < lim):
            lim = lim - numPromos
            return render_template('sendPromo.html', btn=str(promoPass + "smsPromo" + uid), lim=lim)
        else:
            return redirect(url_for('panel'))
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@app.route('/' + promoPass + "smsPromo" + uid, methods=['POST'])
def checksmsPromo():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    if ((currentTime - lastLogin) < sessionTime):
        request.parameter_storage_class = ImmutableOrderedMultiDict
        rsp = ((request.form))
        # print(rsp)
        name = rsp['promoText']
        numPromos = len(database.get("/restaurants/" + estName, "/promos/"))
        lim = int(database.get("/restaurants/" + estName, "/promoLim/"))
        print(lim)
        if (numPromos <= lim):
            database.put("/restaurants/" + estName + "/promos/" + str((numPromos)), "/name/", name)
            numUsr = len(database.get("/restaurants/" + estName, "/users/")) - 1
            lim = lim - numPromos
            database.put("/restaurants/" + estName + "/promos/" + str((numPromos)), "/numTxts/", numUsr)
            return render_template('checkPromo.html', send=str(promoPass + "smsPromo" + uid + "send2"), numUsr=numUsr,
                                   lim=lim, btn=str(promoPass + "smsPromo" + uid + "send"),
                                   back=str(promoPass + "smsPromo" + uid), name=name)
        else:
            return redirect(url_for('panel'))
    else:
        return render_template("login.html", btn=str(estNameStr), restName=estNameStr)


@app.route('/' + promoPass + "smsPromo" + uid + "send2", methods=['POST'])
def sendsmsPromo():
    smtpObj = smtplib.SMTP_SSL("smtp.zoho.com", 465)
    smtpObj.login(sender, emailPass)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    numPromos = len(database.get("/restaurants/" + estName, "/promos/"))
    lim = int(database.get("/restaurants/" + estName, "/promoLim/"))
    print(lim)
    if (numPromos <= lim):
        promoIndx = int(len(database.get("/restaurants/" + estName, "/promos/"))) - 1
        reply = database.get("/restaurants/" + estName, "/promos/" + str(promoIndx) + "/" + "name")
        numbers = []
        for nn in range((len(database.get("/restaurants/" + estName, "/users/")))):
            if (database.get("/restaurants/" + estName, "/users/" + str(nn) + "/number/") != "555555555"):
                numbers.append(database.get("/restaurants/" + estName, "/users/" + str(nn) + "/number/"))
        print(numbers)
        numStr = ""
        for nums in range(len(numbers)):
            numStr += numbers[nums]
            numStr += "<"
        numStr = numStr[:-1]
        try:
            client.messages.create(
                src=botNumber,
                dst=str(numStr),
                text=reply
            )
        except Exception:
            pass
        receivers = database.get("/restaurants/" + estName, "/email/")
        writeStr = "Your Promotion '" + reply + "' has been sent to your customers"
        SUBJECT = "Promotion Sent for " + estNameStr
        message = 'Subject: {}\n\n{}'.format(SUBJECT, writeStr)
        smtpObj.sendmail(sender, receivers, message)
        smtpObj.close()
        return redirect(url_for('panel'))
    else:
        return redirect(url_for('panel'))


@app.route('/' + promoPass, methods=['POST'])
def addCpnResp():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    # print()
    if ((currentTime - lastLogin) < sessionTime):
        request.parameter_storage_class = ImmutableOrderedMultiDict
        rsp = ((request.form))
        # print(rsp)
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
        database.put("/restaurants/" + estName + "/menu/items/" + str(keyVal), "/cat/", " ")
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


@app.route("/" + uid + "check", methods=['GET'])
def loginUUID():
    return render_template("verifyCode.html", btn=str(uid + "check"))


@app.route("/" + uid + "kiosk", methods=['POST'])
def loginKioskx():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    number = rsp['phone']
    print(number)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    currentTime = str((float(datetime.datetime.now(tz).hour)) + ((float(datetime.datetime.now(tz).minute)) / 100.0))
    day = datetime.datetime.today().weekday()
    startHr = float(database.get("restaurants/" + uid, "/OChrs/" + str(day) + "/open/"))
    endHr = float(database.get("restaurants/" + uid, "/OChrs/" + str(day) + "/close/"))
    indx = 0
    DBdata = database.get("/restaurants/" + estName, "/orders")
    UserData = database.get("/restaurants/", uid + "/users")
    UUID = random.randint(9999999, 100000000)
    for dbxv in range(len(DBdata)):
        try:
            if (DBdata[dbxv]["number"] == number):
                database.put("/restaurants/" + estName + "/orders/" + str(dbxv) + "/", "/number/",
                             str(number) + ".")
        except KeyError:
            pass
    tickData = {
        "UUID": str(UUID),
        "name": "",
        "stage": 1,
        "paid": 0,
        "kiosk": 1,
        "giftcard": 0,
        "cash": "",
        "togo": "",
        "tickSize": 0,
        "discUsed": 0,
        "discTotal": 0.0,
        "discStr": "",
        "filled": 0,
        "linkTotal": 0,
        "finalOrder": "",
        "startTime": float(time.time()),
        "number": str(number)
    }
    database.put("/restaurants/" + estName + "/orders/" + str(len(DBdata)), "/", tickData)
    session['UUID'] = UUID
    session['key'] = len(DBdata)
    UserData = database.get("/", "users")
    for usr in range(len(UserData)):
        if (number == UserData[usr]["number"]):
            timeStamp = datetime.datetime.today()
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
    return redirect(url_for('getName'))


@app.route("/" + uid + "kiosk", methods=['GET'])
def loginKiosk():
    return render_template("kioskOpen.html", btn=str(uid + "kiosk"))


@app.route("/" + uid + "chec2", methods=['GET'])
def loginRedo():
    return render_template("verifyCode3.html", btn=str(uid + "check"))


@app.route('/' + uid + 'check', methods=['POST'])
def getUUID():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    code = rsp["tickID"]
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    tickets = database.get("restaurants/" + uid, "/orders/")
    for tx in range(len(tickets)):
        try:
            if (code == tickets[tx]["number"][-4:]):
                key = tx
                UUID = tickets[tx]["UUID"]
                session['UUID'] = UUID
                session['key'] = key
                return redirect(url_for('getName'))
            elif ((len(tickets) - tx) == 1):
                return render_template("verifyCode2.html", btn=str(uid + "check"), number=botNumber)
        except Exception:
            pass


@app.route('/' + uid + 'order0', methods=['GET'])
def getName():
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    tickets = database.get("restaurants/" + uid, "/orders/")
    if(tickets[key]["kiosk"] == 0):
        return (render_template("Name.html", btn=uid + 'order0', btn2=uid + "order20", btn3=uid + 'order30'))
    else:
        return (render_template("NameKiosk.html", btn=uid + 'order0', btn2=uid + "order20", btn3=uid + 'order30'))


@app.route('/' + uid + 'order0', methods=['POST'])
def getNameTime2():
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    print(rsp)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    name = rsp["name"]
    togo = rsp["togo"]
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/name/", name)
    usrIndx = database.get("restaurants/" + uid+"/orders/"+str(key)+"/","userIndx")
    database.put("/users/" + str(usrIndx)+"/", "name", name)
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/togo/", togo)
    if (togo == "to-go"):
        return redirect(url_for('getTime'))
    elif(togo == "delivery"):
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/time/", "DELIVERY")
        return redirect(url_for('getAddr'))
    else:
        return redirect(url_for('getTable'))


@app.route('/' + uid + 'order20', methods=['GET'])
def getTime():
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    startMin = int(datetime.datetime.now(tz).minute) + 20
    startHr = int(datetime.datetime.now(tz).hour)
    print(startHr)
    day = datetime.datetime.today().weekday()
    if (startMin > 59):
        if (startHr == 23):
            startHr = 0
            startMin -= 60
        else:
            startHr += 1
            startMin -= 60
    if (startHr > 9):
        startStr = str(startHr) + ":" + str(startMin)
    else:
        startStr = "0" + str(startHr) + ":" + str(startMin)
    if (startMin < 10):
        startStr = str(startHr) + ":" + "0" + str(startMin)
    print(startStr)
    print(day)
    endHr = str(float(database.get("restaurants/" + uid, "/OChrs/" + str(day) + "/close/")))
    endSplt = endHr.split(".")
    endTimeHr = int(endSplt[0])
    endTimeMin = int(100 * (float(endSplt[1]) / 100))
    endTimeMin -= 15
    if (endTimeMin < 0):
        endTimeHr -= 1
        endTimeMin += 60
    endStr = str(endTimeHr) + ":" + str(endTimeMin)
    print(endStr)
    return (
        render_template("getTime.html", btn=uid + 'order20', btn2=uid + 'order30', back=uid + 'order0', min=startStr,
                        max=endStr))


@app.route('/' + uid + 'order20', methods=['POST'])
def getTimeY():
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/time/", "PICKUP ASAP")
    return redirect(url_for('order'))


@app.route('/' + uid + 'order30', methods=['POST'])
def getTimeX():
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    pickTime = "PICKUP @" + str(rsp["time"])
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/time/", pickTime)
    return redirect(url_for('order'))

@app.route('/' + uid + 'order40', methods=['GET'])
def getDelivery():
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    startMin = int(datetime.datetime.now(tz).minute) + 30
    startHr = int(datetime.datetime.now(tz).hour)
    print(startHr)
    day = datetime.datetime.today().weekday()
    if (startMin > 59):
        if (startHr == 23):
            startHr = 0
            startMin -= 60
        else:
            startHr += 1
            startMin -= 60
    if (startHr > 9):
        startStr = str(startHr) + ":" + str(startMin)
    else:
        startStr = "0" + str(startHr) + ":" + str(startMin)
    if (startMin < 10):
        startStr = str(startHr) + ":" + "0" + str(startMin)
    print(startStr)
    print(day)
    endHr = str(float(database.get("restaurants/" + uid, "/OChrs/" + str(day) + "/close/")))
    endSplt = endHr.split(".")
    endTimeHr = int(endSplt[0])
    endTimeMin = int(100 * (float(endSplt[1]) / 100))
    endTimeMin -= 45
    if (endTimeMin < 0):
        endTimeHr -= 1
        endTimeMin += 60
    endStr = str(endTimeHr) + ":" + str(endTimeMin)
    print(endStr)
    return (render_template("getTime.html", btn=uid + 'order40', btn2=uid + 'order60', back=uid + 'order0', min=startStr,max=endStr))


@app.route('/' + uid + 'order40', methods=['POST'])
def getTimeZ():
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/time/", "DELIVERY")
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/delivTime/", "ASAP")
    return redirect(url_for('getAddr'))


@app.route('/' + uid + 'order60', methods=['POST'])
def getTimeV():
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    pickTime = "DELIVERY @" + str(rsp["time"])
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/time/", pickTime)
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/delivTime/", str(rsp["time"]))
    return redirect(url_for('getAddr'))

@app.route('/'+uid+"address", methods=['GET'])
def getAddr():
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W','cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    usrIndx = database.get("restaurants/" + uid+"/orders/"+str(key)+"/","userIndx")
    try:
        addrs = database.get("restaurants/" + uid + "/users/" + str(usrIndx),"addrs")
        return(render_template("pickAddr.html", btn=uid+"address2x",addrs=addrs,len=len(addrs)))
    except Exception:
        return(render_template("getAddr.html", btn=uid+"address"))

@app.route('/'+uid+"address2x", methods=['POST'])
def getAddr2x():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    print(rsp)
    print(rsp["addr"])
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W','cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    if(rsp["addr"] == "new"):
        return(render_template("getAddr.html", btn=uid+"address"))
    else:
        usrIndx = database.get("restaurants/" + uid+"/orders/"+str(key)+"/","userIndx")
        addrD = database.get("restaurants/" + uid + "/users/" + str(usrIndx),"/addrs/"+str(rsp["addr"]))
        delMethod = database.get("restaurants/" + uid, "/delivery/type")
        database.put("/restaurants/" + estName + "/orders/" + str(key), "addrs", addrD)
        if(delMethod == "postmates"):
            url = "https://api.postmates.com/v1/customers/cus_MMAQ2VmJNZAVOV/delivery_quotes"
            addrP = database.get("restaurants/" + uid, "/address/")
            payload = {"dropoff_address":addrP,
                       "pickup_address":addrD}
            headers = {
                'Content-Type': "application/x-www-form-urlencoded",
                'Authorization': "Basic ODcwZWFiYWUtN2JiMS00MzZjLWFmNGEtMzNmYTJmZTc2ODhlOg==",
                'User-Agent': "PostmanRuntime/7.16.3",
                'Accept': "*/*",
                'Cache-Control': "no-cache",
                'Postman-Token': "55cc61b2-a3aa-42f1-81a9-62467b9199b1,a5cb9e3d-7d0c-4834-9cde-6220fb9962a7",
                'Host': "api.postmates.com",
                'Accept-Encoding': "gzip, deflate",
                'Content-Length': "145",
                'Cookie': "__cfduid=d3e5bcc883cf1529ae363dbc64fe257f61567815844",
                'Connection': "keep-alive",
                'cache-control': "no-cache"
                }
            response = requests.request("POST", url, data=payload, headers=headers)
            resp = (response.json())
            try:
                print(database.get("restaurants/" + uid, "/delivery/split"))
                print(resp)
                print(resp['fee'])
                print(resp['duration'])
                fee = resp['fee']
                fee = float(fee)
                fee  = float(fee/100.0)
                if((fee * float(database.get("restaurants/" + uid, "/delivery/split"))) > float(database.get("restaurants/" + uid, "/delivery/max"))):
                    fee = fee - float(database.get("restaurants/" + uid, "/delivery/max"))
                else:
                    fee = fee * float(database.get("restaurants/" + uid, "/delivery/split"))
                fee = round(fee,2)
                delivDuration = resp['duration']
                minAmt = float(database.get("restaurants/" + uid, "/delivery/minTick"))
                database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "delivFee", fee)
                return(render_template("dispQuote.html", btn=uid+"postmatesQuote",fee=str(fee), duration=str(delivDuration), minAmt=str(minAmt)))
            except Exception:
                return redirect(url_for('getAddr'))
        else:
            return redirect(url_for('inHouseDelivery'))

@app.route('/'+uid+"address", methods=['POST'])
def getAddrX():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    print(rsp)
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W','cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    delMethod = database.get("restaurants/" + uid, "/delivery/type")
    usrIndx = database.get("restaurants/" + uid+"/orders/"+str(key)+"/","userIndx")
    if(delMethod == "postmates"):
        url = "https://api.postmates.com/v1/customers/cus_MMAQ2VmJNZAVOV/delivery_quotes"
        if(rsp["aptNos"] == ""):
            addrD = rsp["addr"]+","+rsp["city"]+","+rsp["state"]+","+str(rsp["zip"])
        else:
            addrD = rsp["aptNos"]+","+rsp["addr"]+","+rsp["city"]+","+rsp["state"]+","+str(rsp["zip"])
        addrs = database.get("restaurants/" + uid + "/users/" + str(usrIndx),"addrs")
        try:
            print(len(addrs))
            database.put("restaurants/" + uid + "/users/" + str(usrIndx),"/addrs/"+str(len(addrs))+"/",addrD)
        except Exception:
            database.put("restaurants/" + uid + "/users/" + str(usrIndx),"/addrs/"+str(0)+"/",addrD)
        database.put("/restaurants/" + estName + "/orders/" + str(key), "addrs", addrD)
        addrP = database.get("restaurants/" + uid, "/address/")
        payload = {"dropoff_address":addrP,
                   "pickup_address":addrD}
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': "Basic ODcwZWFiYWUtN2JiMS00MzZjLWFmNGEtMzNmYTJmZTc2ODhlOg==",
            'User-Agent': "PostmanRuntime/7.16.3",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Postman-Token': "55cc61b2-a3aa-42f1-81a9-62467b9199b1,a5cb9e3d-7d0c-4834-9cde-6220fb9962a7",
            'Host': "api.postmates.com",
            'Accept-Encoding': "gzip, deflate",
            'Content-Length': "145",
            'Cookie': "__cfduid=d3e5bcc883cf1529ae363dbc64fe257f61567815844",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
            }
        response = requests.request("POST", url, data=payload, headers=headers)
        resp = (response.json())
        try:
            print(database.get("restaurants/" + uid, "/delivery/split"))
            print(resp)
            print(resp['fee'])
            print(resp['duration'])
            fee = resp['fee']
            fee = float(fee)
            fee  = float(fee/100.0)
            if((fee * float(database.get("restaurants/" + uid, "/delivery/split"))) > float(database.get("restaurants/" + uid, "/delivery/max"))):
                fee = fee - float(database.get("restaurants/" + uid, "/delivery/max"))
            else:
                fee = fee * float(database.get("restaurants/" + uid, "/delivery/split"))
            fee = round(fee,2)
            delivDuration = resp['duration']
            minAmt = float(database.get("restaurants/" + uid, "/delivery/minTick"))
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "delivFee", fee)
            return(render_template("dispQuote.html", btn=uid+"postmatesQuote",fee=str(fee), duration=str(delivDuration), minAmt=str(minAmt)))
        except Exception:
            return redirect(url_for('getAddr'))
    else:
        return redirect(url_for('inHouseDelivery'))

@app.route('/'+uid+"postmatesQuote", methods=['POST'])
def getDelQuote():
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W','cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    if(rsp["deliv"] == "yes"):
        return redirect(url_for('order'))
    else:
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "delivFee", 0)
        return redirect(url_for('getNameTime2'))

@app.route('/' + uid + 'order1', methods=['GET'])
def getTable():
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    return (render_template("getTable.html", btn=uid + 'order1', back=uid + 'order0'))


@app.route('/' + uid + 'order1', methods=['POST'])
def getTable2():
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    table = rsp['table']
    if (rsp['table'] == ""):
        table += "-"
    putSTR = "Table #" + table
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/time/", putSTR)
    return redirect(url_for('order'))


@app.route('/' + uid + 'order', methods=['GET'])
def order():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    currentTotal = float(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
    DBdata = database.get("/restaurants/" + estName, "orders")
    subTotal = (DBdata[key]["linkTotal"])
    Tax = float(subTotal * 0.1)
    Total = float(subTotal + float(Tax) + 0.5)
    subTotalStr = ('$' + format(subTotal, ',.2f'))
    TotalStr = ('$' + format(Total, ',.2f'))
    TaxStr = ('$' + format(Tax, ',.2f'))
    dispTotal = subTotalStr
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/linkTotal/", currentTotal)
    data = (database.get("restaurants/" + uid, "/menu/items/"))
    currentTime = str((float(datetime.datetime.now(tz).hour)) + ((float(datetime.datetime.now(tz).minute)) / 100.0))
    DBdata = database.get("/restaurants/" + estName, "orders")
    MenuHrs = ((database.get("restaurants/" + uid, "/Hours/")))
    menKeys = list(MenuHrs.keys())
    currentMenu = ""
    menuIndx = 0
    for mnx in range(len(menKeys)):
        startHrMn = (float(MenuHrs[menKeys[mnx]]["startHr"]))
        endHrMn = (float(MenuHrs[menKeys[mnx]]["endHr"]))
        if (startHrMn <= float(currentTime) < endHrMn):
            # print("current menu")
            # print(menKeys[mnx])
            menuIndx = mnx
            currentMenu = str(menKeys[mnx])
            break
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
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
                        wrtStr += str(itms[dispKeys[itmX]]["size"]).lower()
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["name"]).lower()
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["toppings"]).lower()
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["notes"]).lower()
                        wrtStr += " x "
                        wrtStr += str(itms[dispKeys[itmX]]["qty"])
                        wrtStr += " $"
                        wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                        currentItems.append(wrtStr)
                        currKeys.append(dispKeys[itmX])
                        # print(wrtStr)
                    else:
                        wrtStr = str(itms[dispKeys[itmX]]["name"]).lower()
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["toppings"]).lower()
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["notes"]).lower()
                        wrtStr += " x "
                        wrtStr += str(itms[dispKeys[itmX]]["qty"])
                        wrtStr += " $"
                        wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                        currentItems.append(wrtStr)
                        currKeys.append(dispKeys[itmX])
                        # print(wrtStr)
            except KeyError:
                pass
    else:
        dispTotal = "$0.00"
    cats = []
    catkeys2 = []
    for men in range(len(menuItems)):
        if ((menuItems[men]["time"] == currentMenu or menuItems[men]["time"] == "all")):
            if (menuItems[men]["sizes"][0][1] != -1):
                currentCat = menuItems[men]["cat"].upper()
                cats.append(currentCat)
    cats = list(dict.fromkeys(cats))
    for cc in range(len(cats)):
        catkeys2.append(cc)
    # print(catkeys2)
    return render_template("mainOrder.html", len=len(cats), names=cats, keys=catkeys2, btn=uid + "ordercat",
                           len2=(len(currentItems)), currentItms=currentItems, total=dispTotal, currKeys=currKeys,
                           btn2=uid + "order", btn3=uid + "checkpayment")


@app.route('/' + uid + 'order', methods=['POST'])
def orderX():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    itmKey = random.randint(9999, 1000000)
    # print(UUID, key, itmKey)
    print(UUID)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    currentPrice = float(
        database.get("/restaurants/" + estName + "/orders/" + str(key) + "/item/" + str((rsp["rem"])), "price"))
    # print(currentPrice)
    currentTotal = float(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
    currentTotal -= currentPrice
    # print(currentTotal)
    DBdata = database.get("/restaurants/" + estName, "orders")
    subTotal = (currentTotal)
    Tax = float(subTotal * 0.1)
    Total = float(subTotal + float(Tax) + 0.5)
    subTotalStr = ('$' + format(subTotal, ',.2f'))
    TotalStr = ('$' + format(Total, ',.2f'))
    TaxStr = ('$' + format(Tax, ',.2f'))
    dispTotal = subTotalStr
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/linkTotal/", currentTotal)
    database.delete("/restaurants/" + estName + "/orders/" + str(key) + "/item/", (rsp["rem"]))
    data = (database.get("restaurants/" + uid, "/menu/items/"))
    currentTime = str((float(datetime.datetime.now(tz).hour)) + ((float(datetime.datetime.now(tz).minute)) / 100.0))
    DBdata = database.get("/restaurants/" + estName, "orders")
    MenuHrs = ((database.get("restaurants/" + uid, "/Hours/")))
    menKeys = list(MenuHrs.keys())
    currentMenu = ""
    menuIndx = 0
    for mnx in range(len(menKeys)):
        startHrMn = (float(MenuHrs[menKeys[mnx]]["startHr"]))
        endHrMn = (float(MenuHrs[menKeys[mnx]]["endHr"]))
        if (startHrMn <= float(currentTime) < endHrMn):
            # print("current menu")
            # print(menKeys[mnx])
            menuIndx = mnx
            currentMenu = str(menKeys[mnx])
            break
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
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
                        wrtStr += str(itms[dispKeys[itmX]]["size"]).lower()
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["name"]).lower()
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["toppings"]).lower()
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["notes"]).lower()
                        wrtStr += " x "
                        wrtStr += str(itms[dispKeys[itmX]]["qty"])
                        wrtStr += " $"
                        wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                        currentItems.append(wrtStr)
                        currKeys.append(dispKeys[itmX])
                        # print(wrtStr)
                    else:
                        wrtStr = str(itms[dispKeys[itmX]]["name"]).lower()
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["toppings"]).lower()
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["notes"]).lower()
                        wrtStr += " x "
                        wrtStr += str(itms[dispKeys[itmX]]["qty"])
                        wrtStr += " $"
                        wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                        currentItems.append(wrtStr)
                        currKeys.append(dispKeys[itmX])
                        # print(wrtStr)
            except KeyError:
                pass
    else:
        dispTotal = "$0.00"
    cats = []
    catKeys2 = []
    for men in range(len(menuItems)):
        if ((menuItems[men]["time"] == currentMenu or menuItems[men]["time"] == "all")):
            if (menuItems[men]["sizes"][0][1] != -1):
                cats.append(str(menuItems[men]["cat"]).upper())
    # print(cats)
    cats = list(dict.fromkeys(cats))
    # print(cats)
    for cc in range(len(cats)):
        catKeys2.append(cc)
    # print(catKeys2)
    return render_template("mainOrder.html", len=len(cats), names=cats, keys=catKeys2, btn=uid + "ordercat",
                           len2=(len(currentItems)), currentItms=currentItems, total=dispTotal, currKeys=currKeys,
                           btn2=uid + "order", btn3=uid + "checkpayment")


@app.route('/' + uid + 'ordercat', methods=['POST'])
def orderCat():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    # print(rsp)
    key = session.get('key', None)
    UUID = session.get('UUID', None)
    catTgt = rsp["item"]
    names = []
    keys = []
    prices = []
    currentTime = str((float(datetime.datetime.now(tz).hour)) + ((float(datetime.datetime.now(tz).minute)) / 100.0))
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    UUID = session.get('UUID', None)
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    data = (database.get("restaurants/" + uid, "/menu/items/"))
    currentTime = str((float(datetime.datetime.now(tz).hour)) + ((float(datetime.datetime.now(tz).minute)) / 100.0))
    DBdata = database.get("/restaurants/" + estName, "orders")
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
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    names = []
    keys = []
    descrips = []
    cats = []
    warns = []
    for men in range(len(menuItems)):
        if ((menuItems[men]["time"] == currentMenu or menuItems[men]["time"] == "all")):
            if (menuItems[men]["sizes"][0][1] != -1):
                cats.append(str(menuItems[men]["cat"]).upper())
    # print(cats)
    cats = list(dict.fromkeys(cats))
    # print(cats)
    ct = cats[int(catTgt)]
    for men in range(len(menuItems)):
        if (menuItems[men]["cat"].upper() == ct and (
                menuItems[men]["time"] == currentMenu or menuItems[men]["time"] == "all")):
            if (menuItems[men]["sizes"][0][1] != -1):
                names.append(str(menuItems[men]["name"]).upper())
                descrips.append(str(menuItems[men]["descrip"]).lower())
                warns.append(str(menuItems[men]["war"]).lower())
                keys.append(men)
    return render_template("pickcat.html", len=len(names), warns=warns,names=names, keys=keys, prices=prices, descrips=descrips,
                           btn=uid + "orderSz", btn2=uid + "order")


@app.route('/' + uid + 'orderSz', methods=['POST'])
def orderNm():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    itmKey = random.randint(9999, 1000000)
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    print(UUID, key)
    names = []
    keys = []
    prices = []
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    numItms = database.get("/restaurants/" + estName + "/orders/" + str(key), "item")
    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/name/",
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
            names.append(str("Standard $") + str(menuItems[int(rsp['item'])]['sizes'][sz][1]))
            keys.append(0)
            prices.append(menuItems[int(rsp['item'])]['sizes'][sz][1])
    session['itmKey'] = itmKey
    session['nameKey'] = int(rsp['item'])
    return render_template("picksize.html", len=len(prices), names=names, keys=keys, prices=prices,
                           btn=uid + "ordertopping")


@app.route('/' + uid + 'ordertopping', methods=['POST'])
def ordertp():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    itmKey = session.get('itmKey', None)
    nameKey = session.get('nameKey', None)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    # print(menuItems[nameKey], "current item")
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
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    toppings = menuItems[nameKey]["extras"]
    names = []
    keys = []
    warns = []
    for ex in range(len(toppings)):
        if (toppings[ex][0] != ""):
            putStr = ""
            putStr += str(toppings[ex][0].lower())
            putStr += " $"
            putStr += str(toppings[ex][1])
            names.append(putStr)
            try:
                warns.append(toppings[ex][3])
            except Exception:
                warns.append("")
            keys.append(ex)
    # print(rsp)
    return render_template("pickToppings.html", len=len(names), warns=warns,names=names, keys=keys, prices=prices,
                           btn=uid + "ordertoppingConfirm")



@app.route('/' + uid + 'ordertoppingConfirm', methods=['POST'])
def ConfirmItm():
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    itmKey = session.get('itmKey', None)
    nameKey = session.get('nameKey', None)
    # print("nameKEY", nameKey)
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    # print(menuItems[nameKey], "topping")
    # print(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
    # print(rsp, "rsp")
    # print(len(rsp))
    putStr = ""
    addPrice = 0
    extraIndxs = []
    SKUSarr = []
    if (len(rsp) > 2):
        for itx in range(len(menuItems[nameKey]["extras"])):
            ##print(itx)
            try:
                extraIndxs.append(int(rsp[str(itx)]))
            except Exception:
                # print(str(itx), "not found")
                pass
        # print(extraIndxs)
        for exx in range(len(extraIndxs)):
            # print(menuItems[nameKey]["extras"][extraIndxs[exx]])
            putStr += str(menuItems[nameKey]["extras"][extraIndxs[exx]][0])
            # print(menuItems[nameKey]["extras"][extraIndxs[exx]])
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
        # print(currentPrice,"100")
        # print(addPrice,"200")
        currentPrice += addPrice
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
            # print(currentPrice)
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "linkTotal", currentTotal)
        else:
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/qty/",
                         int(rsp["quantity"]))
            currentPrice = currentPrice * int(rsp["quantity"])
            currentTotal = float(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
            currentTotal += currentPrice
            round(currentPrice, 2)
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "linkTotal", currentTotal)

        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/notes/",
                     rsp["notes"])
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/price/",
                     currentPrice)

    else:
        currentPrice = float(
            database.get("/restaurants/" + estName + "/orders/" + str(key) + "/item/" + str(itmKey), "price"))
        # print(currentPrice)
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/toppings/",
                     putStr)
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/notes/",
                     putStr)
        if (rsp["quantity"] == ""):
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/qty/", 1)
            currentTotal = float(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
            currentTotal += currentPrice
            round(currentPrice, 2)
            # print(currentPrice)
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/linkTotal/", currentTotal)
        else:
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/qty/",
                         int(rsp["quantity"]))
            currentPrice = currentPrice * int(rsp["quantity"])
            currentTotal = float(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
            currentTotal += currentPrice
            currentPrice = round(currentPrice, 2)
            currentTotal = round(currentTotal, 2)
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "linkTotal", currentTotal)
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/item/" + str(itmKey) + "/price/",
                         currentPrice)
    return redirect(url_for('order'))


@app.route("/" + uid + "giftcard", methods=['GET'])
def giftcard():
    key = session.get('key', None)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    return render_template("giftcard.html", back=uid + 'checkpayment', btn=uid + "giftcard")


@app.route("/" + uid + "giftcardcheck")
def giftcardcheck():
    key = session.get('key', None)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    return render_template("giftcard3.html", back=uid + 'checkpayment', btn=uid + "giftcard")


@app.route("/" + uid + "giftcard", methods=['POST'])
def giftcardx():
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    key = session.get('key', None)
    dbItems = key
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    DBdata = database.get("/restaurants/" + estName, "orders")
    if(DBdata[dbItems]["togo"] == "delivery"):
        subTotal = (DBdata[key]["linkTotal"])
        subTotal += DBdata[key]["discTotal"]
        disc = (DBdata[key]["discStr"])
        url = "https://api.postmates.com/v1/customers/cus_MMAQ2VmJNZAVOV/delivery_quotes"
        addrD = DBdata[key]["addrs"]
        addrP = database.get("restaurants/" + uid, "/address/")
        payload = {"dropoff_address":addrP,
                   "pickup_address":addrD}
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': "Basic ODcwZWFiYWUtN2JiMS00MzZjLWFmNGEtMzNmYTJmZTc2ODhlOg==",
            'User-Agent': "PostmanRuntime/7.16.3",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Postman-Token': "55cc61b2-a3aa-42f1-81a9-62467b9199b1,a5cb9e3d-7d0c-4834-9cde-6220fb9962a7",
            'Host': "api.postmates.com",
            'Accept-Encoding': "gzip, deflate",
            'Content-Length': "145",
            'Cookie': "__cfduid=d3e5bcc883cf1529ae363dbc64fe257f61567815844",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
            }
        response = requests.request("POST", url, data=payload, headers=headers)
        resp = (response.json())
        fee = float(fee)
        fee  = float(fee/100.0)
        if((fee * float(database.get("restaurants/" + uid, "/delivery/split"))) > float(database.get("restaurants/" + uid, "/delivery/max"))):
            fee = fee - float(database.get("restaurants/" + uid, "/delivery/max"))
        else:
            fee = fee * float(database.get("restaurants/" + uid, "/delivery/split"))
        fee = round(fee,2)
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "delivFee", fee)
        subTotal += fee
        Tax = float(subTotal * 0.1)
        Total = float(subTotal + float(Tax) + 0.5)
    else:
        subTotal = float(DBdata[dbItems]["linkTotal"])
        subTotal += DBdata[dbItems]["discTotal"]
        Tax = subTotal * 0.1
        Total = float(subTotal) + float(Tax) + 0.50
    cardNum = rsp['gcard']
    cards = database.get("/restaurants/" + estName,"/giftcards/")
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    logYM = (datetime.datetime.now(tz).strftime("%Y-%m"))
    cardKeys = list(cards.keys())
    for cc in range(len(cardKeys)):
        print(str(cardKeys[cc]),str(cardNum))
        if(str(cardKeys[cc]) == str(cardNum)):
            cardVal = cards[cardKeys[cc]]["startVal"] - cards[cardKeys[cc]]["usedVal"]
            print(cardVal)
            if(cardVal > 0):
                Total -= cardVal
                Total = round(Total,2)
                if(Total < 0):
                    gcRem = abs(Total)
                    Total = 0
                    database.put("/restaurants/" + estName + "/giftcards/" + str(cardKeys[cc]) + "/", "/usedVal/",
                                 cards[cardKeys[cc]]["startVal"] - gcRem)
                    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "linkTotal", Total)
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
                                # print(wrtStr)
                                # print(str(itms[dispKeys[itmX]]["size"]))
                                wrtStr += str(itms[dispKeys[itmX]]["name"])
                                wrtStr += " "
                                wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                                wrtStr += " "
                                wrtStr += str(itms[dispKeys[itmX]]["notes"])
                                wrtStr += " x "
                                wrtStr += str(itms[dispKeys[itmX]]["qty"])
                                wrtStr += " $"
                                wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                                # print(wrtStr)
                                finalOrd += wrtStr + " :: "
                                skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                                for skk in range(len(skuKeyItm)):
                                    currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                                    for mmn in range(len(menuItems)):
                                        if (menuItems[mmn] != None):
                                            if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn][
                                                "descrip"] != "REMOVEDITM!"):
                                                if (str(menuItems[mmn]["extras"][0][0]) == str(currentSkuItm)):
                                                    discAmt = menuItems[mmn]["extras"][0][1]
                                                    limit = int(menuItems[mmn]["extras"][1][1])
                                                    cpnUsed = int(
                                                        database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                                     "/discUsed/"))
                                                    discTotal = float(
                                                        database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                                     "/discTotal/"))
                                                    if (cpnUsed <=
                                                            limit):
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
                                                                # print(discTotal)
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
                                                            cpnUsed) + " -$" + str(
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
                                # print(wrtStr)
                                finalOrd += wrtStr + " :: "
                                skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                                for skk in range(len(skuKeyItm)):
                                    currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                                    for mmn in range(len(menuItems)):
                                        if (menuItems[mmn] != None):
                                            if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn][
                                                "descrip"] != "REMOVEDITM!"):
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
                                                                # print(discAmtflt, "effee")
                                                                discTotal -= (float(discAmtflt) * float(
                                                                    itms[dispKeys[itmX]]["price"]))
                                                                # print(discTotal)
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
                                                            cpnUsed) + " -$" + str(
                                                            round((
                                                                    discTotal * -1), 2)) + " :: "
                                                        break
                    logYM = (datetime.datetime.now(tz).strftime("%Y-%m"))
                    logData = database.get("/log/" + uid + "/", logYM)
                    if (logData == None):
                        database.put("/log/" + uid + "/" + logYM, "/newCustomers/", 0)
                        database.put("/log/" + uid + "/" + logYM, "/retCustomers/", 0)
                        database.put("/log/" + uid + "/" + logYM, "/CedarFees/", 0.0)
                        database.put("/log/" + uid + "/" + logYM, "/totalRev/", 0.0)
                        database.put("/log/" + uid + "/" + logYM, "/postmatesFees/", 0.0)
                        database.put("/log/" + uid + "/" + logYM, "/skus/-/numSold", 0)
                        database.put("/log/" + uid + "/" + logYM, "/skus/-/rev", 0)
                    logData = database.get("/log/" + uid + "/", logYM)
                    cdrFees = logData['CedarFees']
                    cdrFees += 1
                    database.put("/log/" + uid + "/" + logYM, "/CedarFees/", cdrFees)
                    itms = database.get("/restaurants/" + estName + "/orders/" + str(dbItems), "/item/")
                    if (itms != None):
                        finalOrd = ""
                        dispKeys = list(itms.keys())
                        for itmX in range(len(dispKeys)):
                            try:
                                if (itms[dispKeys[itmX]] != None):
                                    # print(itms[dispKeys[itmX]])
                                    skuKeys = list(itms[dispKeys[itmX]]["skus"].keys())
                                    for sk in range(len(skuKeys)):
                                        currentSku = database.get("/log/" + estName + "/" + str(logYM) + "/" + "skus/",
                                                                  itms[dispKeys[itmX]]["skus"][skuKeys[sk]])
                                        if (currentSku != None):
                                            numsold = currentSku["numSold"] + int(itms[dispKeys[itmX]]["qty"])
                                            rev = currentSku["rev"] + (
                                                    float(itms[dispKeys[itmX]]["qty"]) * float(
                                                itms[dispKeys[itmX]]["price"]))
                                            database.put("/log/" + uid + "/" + logYM,
                                                         "/skus/" + str(
                                                             itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                                            database.put("/log/" + uid + "/" + logYM,
                                                         "/skus/" + str(
                                                             itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                                         numsold)
                                        else:
                                            numsold = int(itms[dispKeys[itmX]]["qty"])
                                            rev = (float(itms[dispKeys[itmX]]["qty"]) * float(
                                                itms[dispKeys[itmX]]["price"]))
                                            database.put("/log/" + uid + "/" + logYM,
                                                         "/skus/" + str(
                                                             itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                                            database.put("/log/" + uid + "/" + logYM,
                                                         "/skus/" + str(
                                                             itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                                         numsold)
                            except KeyError:
                                pass
                    totalRev = float(logData["totalRev"])
                    totalRev += float((DBdata[dbItems]["linkTotal"] + 1) * 1.1)
                    ret = int(logData["retCustomers"])
                    newCust = int(logData["newCustomers"])
                    if (DBdata[dbItems]["ret"] == 0):
                        ret += 1
                        database.put("/log/" + uid + "/" + logYM, "/retCustomers/", ret)
                    else:
                        newCust += 1
                        database.put("/log/" + uid + "/" + logYM, "/newCustomers/", newCust)
                    database.put("/log/" + uid + "/" + logYM, "/totalRev/", totalRev)
                    logYM = (datetime.datetime.now(tz).strftime("%Y-%m-%d"))
                    logData = database.get("/log/" + uid + "/", logYM)
                    if (logData == None):
                        database.put("/log/" + uid + "/" + logYM, "/newCustomers/", 0)
                        database.put("/log/" + uid + "/" + logYM, "/retCustomers/", 0)
                        database.put("/log/" + uid + "/" + logYM, "/CedarFees/", 0.0)
                        database.put("/log/" + uid + "/" + logYM, "/totalRev/", 0.0)
                        database.put("/log/" + uid + "/" + logYM, "/postmatesFees/", 0.0)
                        database.put("/log/" + uid + "/" + logYM, "/skus/-/numSold", 0)
                        database.put("/log/" + uid + "/" + logYM, "/skus/-/rev", 0)
                    logData = database.get("/log/" + uid + "/", logYM)
                    cdrFees = logData['CedarFees']
                    cdrFees += 1
                    database.put("/log/" + uid + "/" + logYM, "/CedarFees/", cdrFees)
                    itms = database.get("/restaurants/" + estName + "/orders/" + str(dbItems), "/item/")
                    if (itms != None):
                        finalOrd = ""
                        dispKeys = list(itms.keys())
                        for itmX in range(len(dispKeys)):
                            try:
                                if (itms[dispKeys[itmX]] != None):
                                    # print(itms[dispKeys[itmX]])
                                    skuKeys = list(itms[dispKeys[itmX]]["skus"].keys())
                                    for sk in range(len(skuKeys)):
                                        currentSku = database.get("/log/" + estName + "/" + str(logYM) + "/" + "skus/",
                                                                  itms[dispKeys[itmX]]["skus"][skuKeys[sk]])
                                        if (currentSku != None):
                                            numsold = currentSku["numSold"] + int(itms[dispKeys[itmX]]["qty"])
                                            rev = currentSku["rev"] + (
                                                    float(itms[dispKeys[itmX]]["qty"]) * float(
                                                itms[dispKeys[itmX]]["price"]))
                                            database.put("/log/" + uid + "/" + logYM,
                                                         "/skus/" + str(
                                                             itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                                            database.put("/log/" + uid + "/" + logYM,
                                                         "/skus/" + str(
                                                             itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                                         numsold)
                                        else:
                                            numsold = int(itms[dispKeys[itmX]]["qty"])
                                            rev = (float(itms[dispKeys[itmX]]["qty"]) * float(
                                                itms[dispKeys[itmX]]["price"]))
                                            database.put("/log/" + uid + "/" + logYM,
                                                         "/skus/" + str(
                                                             itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                                            database.put("/log/" + uid + "/" + logYM,
                                                         "/skus/" + str(
                                                             itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                                         numsold)
                            except KeyError:
                                pass
                    totalRev = float(logData["totalRev"])
                    totalRev += float((DBdata[dbItems]["linkTotal"] + 1) * 1.1)
                    database.put("/log/" + uid + "/" + logYM, "/totalRev/", totalRev)
                    ret = int(logData["retCustomers"])
                    newCust = int(logData["newCustomers"])
                    if (DBdata[dbItems]["ret"] == 0):
                        ret += 1
                        database.put("/log/" + uid + "/" + logYM, "/retCustomers/", ret)
                    else:
                        newCust += 1
                        database.put("/log/" + uid + "/" + logYM, "/newCustomers/", newCust)
                    # print(finalOrd)
                    updateLog()
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "finalOrder/", finalOrd)
                    # print(finalOrd, "put")
                    DBdata = database.get("/restaurants/" + estName, "orders")
                    duration = time.time() - float(DBdata[dbItems]["startTime"])
                    subTotal = float(DBdata[key]["linkTotal"])
                    Total = 0
                    numItms = len(DBdata[dbItems]["item"])
                    orderIndx = DBdata[dbItems]["orderIndx"]
                    usrIndx = DBdata[dbItems]["userIndx"]
                    database.put(
                        "/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                            orderIndx) + "/", "total",
                        Total)
                    database.put(
                        "/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                            orderIndx) + "/", "tickSize",
                        numItms)
                    database.put(
                        "/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                            orderIndx) + "/", "items",
                        DBdata[dbItems]["item"])
                    database.put(
                        "/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
                            orderIndx) + "/", "duration",
                        duration)
                    number = DBdata[dbItems]["number"]
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "finalOrder/", finalOrd)
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "tickSize/", numItms)
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "filled/", "1")
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "giftcard/", 1)
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "number/",
                                 str((number) + "."))
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "endTime/", time.time())
                    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "duration/", duration)
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/day/",
                                 calendar.day_name[datetime.datetime.now(tz).today().weekday()])
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/hour/",
                                 int(datetime.datetime.now(tz).hour))
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/month/",
                                 (datetime.datetime.now(tz).strftime("%m")))
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/date/",
                                 (datetime.datetime.now(tz).strftime("%d")))
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/year/",
                                 (datetime.datetime.now(tz).strftime("%Y")))
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "cash/", "")
                    if (DBdata[dbItems]["togo"] == "to-go"):
                        reply = "-Thank you for your order, you can pick it up and pay at the counter when you arrive \n-To order again just text " + '"order"'
                    else:
                        reply = "-Thank you for your order, please pay at the counter, after you pay your food will be delivered to your table \n-To order again just text " + '"order"'
                    if (DBdata[dbItems]['email'] != ""):
                        smtpObj = smtplib.SMTP_SSL("smtp.zoho.com", 465)
                        smtpObj.login(sender, emailPass)
                        try:
                            subTotal = (DBdata[dbItems]["linkTotal"]) + DBdata[dbItems]["discTotal"]
                        except KeyError:
                            subTotal = (DBdata[dbItems]["linkTotal"])
                        Tax = 0
                        Total = 0
                        subTotalStr = ('$' + format(subTotal, ',.2f'))
                        TotalStr = ('$' + format(Total, ',.2f'))
                        TaxStr = ('$' + format(Tax, ',.2f'))
                        #add delivery code
                        if(DBdata[dbItems]["togo"] == "delivery"):
                            client.messages.create(
                                src=botNumber,
                                dst=number,
                                text="Your order is being prepared, we'll send you a tracking link when your order is on the way"
                            )
                        itms = str(DBdata[dbItems]["finalOrder"])
                        itms = itms.replace("::", "\n-")
                        now = datetime.datetime.now(tz)
                        writeStr = "your order on " + str(now.strftime("%Y-%m-%d @ %H:%M")) + "\nNAME:" + str(
                            DBdata[dbItems]["name"]) + "\n\nItems\n-" + str(itms) + "\n" + str(
                            DBdata[dbItems]["discStr"]) \
                                   + "\n" + str(DBdata[dbItems]["togo"]) + "\n" + str(
                            DBdata[dbItems]["time"]) + "\nSubtotal " + str(subTotalStr) + "\nTaxes and fees $" + str(
                            round((Total - subTotal), 2)) + "\nTotal " + TotalStr
                        SUBJECT = "Your Order from " + estNameStr
                        message = 'Subject: {}\n\n{}'.format(SUBJECT, writeStr)
                        smtpObj.sendmail(sender,DBdata[dbItems]['email'] , message)
                        smtpObj.close()
                    updateLog()
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "number/", str((number) + "."))
                    session.clear()
                    if (DBdata[dbItems]["kiosk"] == 0):
                        return render_template("giftcard2.html", btn="thankMsglnk",Total=Total, gcRem=gcRem)
                    else:
                        return render_template("giftcard2.html", btn="thankMsg2lnk",Total=Total, gcRem=gcRem)
                else:
                    gcRem = 0
                    database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "giftcard/", 1)
                    database.put("/restaurants/" + estName + "/giftcards/" + str(cardKeys[cc]) + "/", "/usedVal/", cards[cardKeys[cc]]["startVal"] - gcRem)
                    database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "linkTotal", (Total))
                    return render_template("giftcard2.html", btn="charge", Total=Total, gcRem=gcRem)
            else:
                return redirect(url_for('giftcardcheck'))
        if(len(cardKeys) - cc == 1):
            return redirect(url_for('giftcardcheck'))

@app.route("/thankMsglnk")
def dispMSGend():
    return render_template("thankMsg.html")
@app.route("/thankMsg2lnk")
def dispMSGend2():
    return render_template("thankMsg2.html",btn=uid+"kiosk")
@app.route("/charge", methods=['GET'])
def pay():
    key = session.get('key', None)
    dbItems = key
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    DBdata = database.get("/restaurants/" + estName, "orders")
    if(DBdata[dbItems]["giftcard"] == 0):
        subTotal = float(DBdata[dbItems]["linkTotal"])
        subTotal += DBdata[dbItems]["discTotal"]
        try:
            subTotal += DBdata[dbItems]["delivFee"]
        except KeyError:
            pass
        Tax = subTotal * 0.1
        Total = float(subTotal) + float(Tax) + 0.50
        Total = round(Total, 2)
        print(Total)
    else:
        subTotal = float(DBdata[dbItems]["linkTotal"])
        subTotal += DBdata[dbItems]["discTotal"]
        try:
            if(DBdata[dbItems]["delivFee"] != None and DBdata[dbItems]["togo"] == "delivery"):
                subTotal += DBdata[dbItems]["delivFee"]
        except Exception:
            pass
        Tax = subTotal * 0.1
        Total = float(subTotal) + float(Tax) + 0.50
        Total = round(Total, 2)
    return render_template("paymentFinal.html", Total=str(Total), btn="charge", token=stripeToken,back=uid + 'checkpayment')


@app.route("/charge", methods=['POST'])
def payX():
    key = session.get('key', None)
    dbItems = key
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    DBdata = database.get("/restaurants/" + estName, "orders")
    subTotal = float(DBdata[dbItems]["linkTotal"])
    subTotal += DBdata[dbItems]["discTotal"]
    UUID = DBdata[dbItems]["UUID"]
    if (DBdata[dbItems]["giftcard"] == 0):
        Tax = subTotal * 0.1
        Total = float(subTotal) + float(Tax) + 0.50
        stripe.api_key = stripeToken
        token = request.form['stripeToken']  # Using Flask
        Total = round(Total, 2)
        Total = int(Total * 100)
        try:
            stripe.Charge.create(
                amount=Total,
                currency='usd',
                description=str(UUID),
                source=token,
            )
        except Exception:
            return render_template("paymentDeclined.html", btn="charge")
    else:
        Total = float(DBdata[dbItems]["linkTotal"])
        stripe.api_key = stripeToken
        token = request.form['stripeToken']  # Using Flask
        Total = round(Total, 2)
        Total = int(Total * 100)
        try:
            stripe.Charge.create(
                amount=Total,
                currency='usd',
                description=str(UUID),
                source=token)
        except Exception:
            return render_template("paymentDeclined.html", btn="charge")
    print(DBdata[dbItems]["filled"],"testKey")
    if(DBdata[dbItems]["filled"] == "100"):
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/filled/", "200")
    while(DBdata[dbItems]["filled"] != "1"):
        DBdata = database.get("/restaurants/" + estName, "orders")
        if(DBdata[dbItems]["filled"] == "1"):
            if (DBdata[dbItems]["kiosk"] == 0):
                session.clear()
                return render_template("thankMsg.html")
            else:
                session.clear()
                return render_template("thankMsg2.html", btn=str(uid + "kiosk"))
        if(DBdata[dbItems]["filled"] == "100"):
            return render_template("paymentDeclined.html",btn="charge")

@app.route('/' + uid + 'checkpayment', methods=['POST'])
def CheckPaymentMethod():
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    itms = database.get("/restaurants/" + estName + "/orders/" + str(key), "/item/")
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    if (itms != None):
        finalOrd = ""
        dispKeys = list(itms.keys())
        for itmX in range(len(dispKeys)):
            if (itms[dispKeys[itmX]] != None):
                # print(itms[dispKeys[itmX]])
                try:
                    skuKeys = list(itms[dispKeys[itmX]]["skus"].keys())
                    wrtStr = ""
                    if (str(itms[dispKeys[itmX]]["size"]).lower() != "u"):
                        wrtStr += str(itms[dispKeys[itmX]]["size"])
                        wrtStr += " "
                        # print(wrtStr)
                        # print(str(itms[dispKeys[itmX]]["size"]))
                        wrtStr += str(itms[dispKeys[itmX]]["name"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                        wrtStr += " "
                        wrtStr += str(itms[dispKeys[itmX]]["notes"])
                        wrtStr += " x "
                        wrtStr += str(itms[dispKeys[itmX]]["qty"])
                        wrtStr += " $"
                        wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                        # print(wrtStr)
                        finalOrd += wrtStr + " :: "
                        skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                        for skk in range(len(skuKeyItm)):
                            currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                            for mmn in range(len(menuItems)):
                                if (menuItems[mmn] != None):
                                    if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn][
                                        "descrip"] != "REMOVEDITM!"):
                                        if (str(menuItems[mmn]["extras"][0][0]) == str(currentSkuItm)):
                                            # print("ggbrgebrgebr")
                                            discAmt = menuItems[mmn]["extras"][0][1]
                                            limit = int(menuItems[mmn]["extras"][1][1])
                                            cpnUsed = int(
                                                database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                             "/discUsed/"))
                                            discTotal = float(
                                                database.get("/restaurants/" + estName + "/orders/" + str(key),
                                                             "/discTotal/"))
                                            # print(cpnUsed, limit, discTotal)
                                            if (cpnUsed <= limit):
                                                try:
                                                    float(discAmt)
                                                    discAmtflt = float(discAmt)
                                                    # print(cpnUsed, limit, int(itms[dispKeys[itmX]]["qty"]))
                                                    while cpnUsed <= limit and cpnUsed <= int(
                                                            itms[dispKeys[itmX]]["qty"]):
                                                        # print("iid")
                                                        discTotal -= discAmtflt
                                                        cpnUsed += 1
                                                except ValueError:
                                                    discAmt = discAmt[:-1]
                                                    discAmtflt = float(discAmt)
                                                    # print(discAmtflt)
                                                    # print(cpnUsed, limit, int(itms[dispKeys[itmX]]["qty"]))
                                                    while cpnUsed <= limit and cpnUsed <= int(
                                                            itms[dispKeys[itmX]]["qty"]):
                                                        discTotal -= (float(discAmtflt) * (
                                                                (float(itms[dispKeys[itmX]]["price"])) / float(
                                                            itms[dispKeys[itmX]]["qty"])))
                                                        # print(discTotal)
                                                        cpnUsed += 1
                                                        # print(cpnUsed)
                                                    # print(discTotal)
                                                # print(cpnUsed)
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
                            # print(wrtStr)
                            finalOrd += wrtStr + " :: "
                            skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                            for skk in range(len(skuKeyItm)):
                                currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                                for mmn in range(len(menuItems)):
                                    if (menuItems[mmn] != None):
                                        if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn][
                                            "descrip"] != "REMOVEDITM!"):
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
                                                        # print(cpnUsed, limit, int(itms[dispKeys[itmX]]["qty"]))
                                                        while cpnUsed < limit and cpnUsed < int(
                                                                itms[dispKeys[itmX]]["qty"]):
                                                            # print(cpnUsed)
                                                            # print("fsfwrrw")
                                                            discTotal -= float(
                                                                float(discAmtflt) * float(
                                                                    itms[dispKeys[itmX]]["price"]))
                                                            # print(discTotal)
                                                            cpnUsed += 1
                                                    # print(discTotal)
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
                                                                cpnUsed) + ":: -$" + str(
                                                                round(float(discTotal * -1), 2))))
                                                    finalOrd += menuItems[mmn]["name"] + " x " + str(
                                                        cpnUsed) + ":: -$" + str(
                                                        round(float(discTotal * -1), 2)) + " :: "
                                                    break
                except Exception:
                    pass
    DBdata = database.get("/restaurants/" + estName, "orders")
    delivStr =  ""
    subTotal = (DBdata[key]["linkTotal"])
    subTotal += DBdata[key]["discTotal"]
    disc = (DBdata[key]["discStr"])
    Tax = float(subTotal * 0.1)
    Total = float(subTotal + float(Tax) + 0.5)
    subTotalStr = ('$' + format(subTotal, ',.2f'))
    TotalStr = ('$' + format(Total, ',.2f'))
    TaxStr = ('$' + format(Tax, ',.2f'))
    delivFeeStr = ""
    try:
        if (DBdata[key]["kiosk"] == 0):
            print(DBdata[key]["togo"])
            if(DBdata[key]["togo"] == "delivery"):
                subTotal = (DBdata[key]["linkTotal"])
                subTotal += DBdata[key]["discTotal"]
                disc = (DBdata[key]["discStr"])
                url = "https://api.postmates.com/v1/customers/cus_MMAQ2VmJNZAVOV/delivery_quotes"
                addrD = DBdata[key]["addrs"]
                addrP = database.get("restaurants/" + uid, "/address/")
                print(addrP)
                payload = {"dropoff_address":addrP,
                           "pickup_address":addrD}
                headers = {
                    'Content-Type': "application/x-www-form-urlencoded",
                    'Authorization': "Basic ODcwZWFiYWUtN2JiMS00MzZjLWFmNGEtMzNmYTJmZTc2ODhlOg==",
                    'User-Agent': "PostmanRuntime/7.16.3",
                    'Accept': "*/*",
                    'Cache-Control': "no-cache",
                    'Postman-Token': "55cc61b2-a3aa-42f1-81a9-62467b9199b1,a5cb9e3d-7d0c-4834-9cde-6220fb9962a7",
                    'Host': "api.postmates.com",
                    'Accept-Encoding': "gzip, deflate",
                    'Content-Length': "145",
                    'Cookie': "__cfduid=d3e5bcc883cf1529ae363dbc64fe257f61567815844",
                    'Connection': "keep-alive",
                    'cache-control': "no-cache"
                    }
                response = requests.request("POST", url, data=payload, headers=headers)
                resp = (response.json())
                print(resp)
                print(database.get("restaurants/" + uid, "/delivery/split"))
                fee = resp['fee']
                fee = float(fee)
                fee  = float(fee/100.0)
                if((fee * float(database.get("restaurants/" + uid, "/delivery/split"))) > float(database.get("restaurants/" + uid, "/delivery/max"))):
                    fee = fee - float(database.get("restaurants/" + uid, "/delivery/max"))
                else:
                    fee = fee * float(database.get("restaurants/" + uid, "/delivery/split"))
                fee = round(fee,2)
                delivDuration = resp['duration']
                minAmt = float(database.get("restaurants/" + uid, "/delivery/minTick"))
                database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "delivFee", fee)
                subTotal += fee
                delivStr =  ('$' + format(fee, ',.2f'))
                Tax = float(subTotal * 0.1)
                Total = float(subTotal + float(Tax) + 0.5)
                subTotalStr = ('$' + format(subTotal, ',.2f'))
                TotalStr = ('$' + format(Total, ',.2f'))
                TaxStr = ('$' + format(Tax, ',.2f'))
                delivStr = str(fee)
                print(subTotal)
                print(fee)
                return render_template("paymentMethod.html", btn=uid + "nextPay", subTotal=subTotalStr, tax=TaxStr,
                                       total=TotalStr,
                                       CPN=disc, btn2=uid + "order", deliv=str(fee))
            return render_template("paymentMethod.html", btn=uid + "nextPay", subTotal=subTotalStr, tax=TaxStr,
                                   total=TotalStr,
                                   CPN=disc, btn2=uid + "order", deliv=delivStr)
        else:
            return render_template("paymentMethodKiosk.html", btn=uid + "nextPay", subTotal=subTotalStr, tax=TaxStr,
                                   total=TotalStr,
                                   CPN=disc, btn2=uid + "order")
    except Exception:
        return render_template("paymentMethod.html", btn=uid + "nextPay", subTotal=subTotalStr, tax=TaxStr,
                               total=TotalStr,
                               CPN=disc, btn2=uid + "order", deliv=str("0.00"))


@app.route('/' + uid + 'nextPay', methods=['POST'])
def nextPayment():
    UUID = session.get('UUID', None)
    key = session.get('key', None)
    dbItems = key
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    menuItems = database.get("/restaurants/" + estName + "/menu/", "items")
    currentTotal = float(database.get("/restaurants/" + estName + "/orders/" + str(key), "/linkTotal"))
    number = str(database.get("/restaurants/" + estName + "/orders/" + str(key), "/number"))
    request.parameter_storage_class = ImmutableOrderedMultiDict
    rsp = ((request.form))
    # print(rsp)
    finalOrd = ""
    if(rsp["item"] == "card"):
        itms = database.get("/restaurants/" + estName + "/orders/" + str(key), "/item/")
        itms = database.get("/restaurants/" + estName + "/orders/" + str(key), "/item/")
        if (itms != None):
            finalOrd = ""
            dispKeys = list(itms.keys())
            for itmX in range(len(dispKeys)):
                try:
                    if (itms[dispKeys[itmX]] != None):
                        wrtStr = ""
                        if (str(itms[dispKeys[itmX]]["size"]).lower() != "u"):
                            wrtStr += str(itms[dispKeys[itmX]]["size"])
                            wrtStr += " "
                            # print(wrtStr)
                            # print(str(itms[dispKeys[itmX]]["size"]))
                            wrtStr += str(itms[dispKeys[itmX]]["name"])
                            wrtStr += " "
                            wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                            wrtStr += " "
                            wrtStr += str(itms[dispKeys[itmX]]["notes"])
                            wrtStr += " x "
                            wrtStr += str(itms[dispKeys[itmX]]["qty"])
                            wrtStr += " $"
                            wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                            # print(wrtStr)
                            finalOrd += wrtStr + " :: "
                            skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                            for skk in range(len(skuKeyItm)):
                                currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                                for mmn in range(len(menuItems)):
                                    if (menuItems[mmn] != None):
                                        if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn][
                                            "descrip"] != "REMOVEDITM!"):
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
                            # print(wrtStr)
                            finalOrd += wrtStr + " :: "
                            skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                            for skk in range(len(skuKeyItm)):
                                currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                                for mmn in range(len(menuItems)):
                                    if (menuItems[mmn] != None):
                                        if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn][
                                            "descrip"] != "REMOVEDITM!"):
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
                    # print("exec")
                    pass
            # print(finalOrd)
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "finalOrder/", finalOrd)
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "email/", str(rsp['email']))
            return redirect(url_for('giftcard'))
        else:
            return redirect(url_for('order'))
    if (rsp["item"] == "yes"):
        itms = database.get("/restaurants/" + estName + "/orders/" + str(key), "/item/")
        itms = database.get("/restaurants/" + estName + "/orders/" + str(key), "/item/")
        if (itms != None):
            finalOrd = ""
            dispKeys = list(itms.keys())
            for itmX in range(len(dispKeys)):
                try:
                    if (itms[dispKeys[itmX]] != None):
                        wrtStr = ""
                        if (str(itms[dispKeys[itmX]]["size"]).lower() != "u"):
                            wrtStr += str(itms[dispKeys[itmX]]["size"])
                            wrtStr += " "
                            # print(wrtStr)
                            # print(str(itms[dispKeys[itmX]]["size"]))
                            wrtStr += str(itms[dispKeys[itmX]]["name"])
                            wrtStr += " "
                            wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                            wrtStr += " "
                            wrtStr += str(itms[dispKeys[itmX]]["notes"])
                            wrtStr += " x "
                            wrtStr += str(itms[dispKeys[itmX]]["qty"])
                            wrtStr += " $"
                            wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                            # print(wrtStr)
                            finalOrd += wrtStr + " :: "
                            skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                            for skk in range(len(skuKeyItm)):
                                currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                                for mmn in range(len(menuItems)):
                                    if (menuItems[mmn] != None):
                                        if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn][
                                            "descrip"] != "REMOVEDITM!"):
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
                            # print(wrtStr)
                            finalOrd += wrtStr + " :: "
                            skuKeyItm = list(itms[dispKeys[itmX]]["skus"].keys())
                            for skk in range(len(skuKeyItm)):
                                currentSkuItm = itms[dispKeys[itmX]]["skus"][skuKeyItm[skk]]
                                for mmn in range(len(menuItems)):
                                    if (menuItems[mmn] != None):
                                        if (menuItems[mmn]["sizes"][0][1] == -1 and menuItems[mmn][
                                            "descrip"] != "REMOVEDITM!"):
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
                    # print("exec")
                    pass
            # print(finalOrd)
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "finalOrder/", finalOrd)
            # print("final put")
            DBdata = database.get("/restaurants/" + estName, "orders")
            subTotal = float(DBdata[dbItems]["linkTotal"])
            subTotal += DBdata[dbItems]["discTotal"]
            UUIDcode = DBdata[dbItems]["UUID"]
            Tax = subTotal * 0.1
            Total = float(subTotal) + float(Tax) + 0.5
            database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "email/", str(rsp['email']))
            return redirect(url_for('pay'))
        else:
            return redirect(url_for('order'))

    else:
        authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                         'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
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
                    # print(wrtStr)
                    # print(str(itms[dispKeys[itmX]]["size"]))
                    wrtStr += str(itms[dispKeys[itmX]]["name"])
                    wrtStr += " "
                    wrtStr += str(itms[dispKeys[itmX]]["toppings"])
                    wrtStr += " "
                    wrtStr += str(itms[dispKeys[itmX]]["notes"])
                    wrtStr += " x "
                    wrtStr += str(itms[dispKeys[itmX]]["qty"])
                    wrtStr += " $"
                    wrtStr += str(round(itms[dispKeys[itmX]]["price"], 2))
                    # print(wrtStr)
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
                                                    # print(discTotal)
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
                    # print(wrtStr)
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
                                                    # print(discAmtflt, "effee")
                                                    discTotal -= (float(discAmtflt) * float(
                                                        itms[dispKeys[itmX]]["price"]))
                                                    # print(discTotal)
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
            return redirect(url_for('order'))
        # print(finalOrd)
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "finalOrder/", finalOrd)
        # print(finalOrd, "put")
        DBdata = database.get("/restaurants/" + estName, "orders")
        duration = time.time() - float(DBdata[dbItems]["startTime"])
        subTotal = float(DBdata[key]["linkTotal"])
        subTotal += DBdata[dbItems]["discTotal"]
        Total = round(((subTotal + 0.5) * 1.1), 2)
        numItms = len(DBdata[dbItems]["item"])
        orderIndx = DBdata[dbItems]["orderIndx"]
        usrIndx = DBdata[dbItems]["userIndx"]
        database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
            orderIndx) + "/", "total",
                     Total)
        database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
            orderIndx) + "/", "tickSize",
                     numItms)
        database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
            orderIndx) + "/", "items",
                     DBdata[dbItems]["item"])
        database.put("/users/" + str(usrIndx) + "/restaurants/" + estNameStr + "/" + str(
            orderIndx) + "/", "duration",
                     duration)
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "finalOrder/", finalOrd)
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "tickSize/", numItms)
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "filled/", "1")
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "number/", str((number) + "."))
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "endTime/", time.time())
        database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "duration/", duration)
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/day/",
                     calendar.day_name[datetime.datetime.now(tz).today().weekday()])
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/hour/",
                     int(datetime.datetime.now(tz).hour))
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/month/",
                     (datetime.datetime.now(tz).strftime("%m")))
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/date/",
                     (datetime.datetime.now(tz).strftime("%d")))
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "/year/",
                     (datetime.datetime.now(tz).strftime("%Y")))
        database.put("/restaurants/" + estName + "/orders/" + str(dbItems) + "/", "cash/", "NOT PAID")
        logYM = (datetime.datetime.now(tz).strftime("%Y-%m"))
        logData = database.get("/log/" + uid + "/", logYM)
        if (logData == None):
            database.put("/log/" + uid + "/" + logYM, "/newCustomers/", 0)
            database.put("/log/" + uid + "/" + logYM, "/retCustomers/", 0)
            database.put("/log/" + uid + "/" + logYM, "/CedarFees/", 0.0)
            database.put("/log/" + uid + "/" + logYM, "/totalRev/", 0.0)
            database.put("/log/" + uid + "/" + logYM, "/postmatesFees/", 0.0)
            database.put("/log/" + uid + "/" + logYM, "/skus/-/numSold", 0)
            database.put("/log/" + uid + "/" + logYM, "/skus/-/rev", 0)
        logData = database.get("/log/" + uid + "/", logYM)
        cdrFees = logData['CedarFees']
        cdrFees += 1
        database.put("/log/" + uid + "/" + logYM, "/CedarFees/", cdrFees)
        itms = database.get("/restaurants/" + estName + "/orders/" + str(dbItems), "/item/")
        if (itms != None):
            finalOrd = ""
            dispKeys = list(itms.keys())
            for itmX in range(len(dispKeys)):
                try:
                    if (itms[dispKeys[itmX]] != None):
                        # print(itms[dispKeys[itmX]])
                        skuKeys = list(itms[dispKeys[itmX]]["skus"].keys())
                        for sk in range(len(skuKeys)):
                            currentSku = database.get("/log/" + estName + "/" + str(logYM) + "/" + "skus/",
                                                      itms[dispKeys[itmX]]["skus"][skuKeys[sk]])
                            if (currentSku != None):
                                numsold = currentSku["numSold"] + int(itms[dispKeys[itmX]]["qty"])
                                rev = currentSku["rev"] + (
                                        float(itms[dispKeys[itmX]]["qty"]) * float(
                                    itms[dispKeys[itmX]]["price"]))
                                database.put("/log/" + uid + "/" + logYM,
                                             "/skus/" + str(
                                                 itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                                database.put("/log/" + uid + "/" + logYM,
                                             "/skus/" + str(
                                                 itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                             numsold)
                            else:
                                numsold = int(itms[dispKeys[itmX]]["qty"])
                                rev = (float(itms[dispKeys[itmX]]["qty"]) * float(
                                    itms[dispKeys[itmX]]["price"]))
                                database.put("/log/" + uid + "/" + logYM,
                                             "/skus/" + str(
                                                 itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                                database.put("/log/" + uid + "/" + logYM,
                                             "/skus/" + str(
                                                 itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                             numsold)
                except KeyError:
                    pass
        totalRev = float(logData["totalRev"])
        totalRev += float((DBdata[dbItems]["linkTotal"] + 1) * 1.1)
        ret = int(logData["retCustomers"])
        newCust = int(logData["newCustomers"])
        if (DBdata[dbItems]["ret"] == 0):
            ret += 1
            database.put("/log/" + uid + "/" + logYM, "/retCustomers/", ret)
        else:
            newCust += 1
            database.put("/log/" + uid + "/" + logYM, "/newCustomers/", newCust)
        database.put("/log/" + uid + "/" + logYM, "/totalRev/", totalRev)
        logYM = (datetime.datetime.now(tz).strftime("%Y-%m-%d"))
        logData = database.get("/log/" + uid + "/", logYM)
        if (logData == None):
            database.put("/log/" + uid + "/" + logYM, "/newCustomers/", 0)
            database.put("/log/" + uid + "/" + logYM, "/retCustomers/", 0)
            database.put("/log/" + uid + "/" + logYM, "/CedarFees/", 0.0)
            database.put("/log/" + uid + "/" + logYM, "/totalRev/", 0.0)
            database.put("/log/" + uid + "/" + logYM, "/postmatesFees/", 0.0)
            database.put("/log/" + uid + "/" + logYM, "/skus/-/numSold", 0)
            database.put("/log/" + uid + "/" + logYM, "/skus/-/rev", 0)
        logData = database.get("/log/" + uid + "/", logYM)
        cdrFees = logData['CedarFees']
        cdrFees += 1
        database.put("/log/" + uid + "/" + logYM, "/CedarFees/", cdrFees)
        itms = database.get("/restaurants/" + estName + "/orders/" + str(dbItems), "/item/")
        if (itms != None):
            finalOrd = ""
            dispKeys = list(itms.keys())
            for itmX in range(len(dispKeys)):
                try:
                    if (itms[dispKeys[itmX]] != None):
                        # print(itms[dispKeys[itmX]])
                        skuKeys = list(itms[dispKeys[itmX]]["skus"].keys())
                        for sk in range(len(skuKeys)):
                            currentSku = database.get("/log/" + estName + "/" + str(logYM) + "/" + "skus/",
                                                      itms[dispKeys[itmX]]["skus"][skuKeys[sk]])
                            if (currentSku != None):
                                numsold = currentSku["numSold"] + int(itms[dispKeys[itmX]]["qty"])
                                rev = currentSku["rev"] + (
                                        float(itms[dispKeys[itmX]]["qty"]) * float(
                                    itms[dispKeys[itmX]]["price"]))
                                database.put("/log/" + uid + "/" + logYM,
                                             "/skus/" + str(
                                                 itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                                database.put("/log/" + uid + "/" + logYM,
                                             "/skus/" + str(
                                                 itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                             numsold)
                            else:
                                numsold = int(itms[dispKeys[itmX]]["qty"])
                                rev = (float(itms[dispKeys[itmX]]["qty"]) * float(
                                    itms[dispKeys[itmX]]["price"]))
                                database.put("/log/" + uid + "/" + logYM,
                                             "/skus/" + str(
                                                 itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/rev/", rev)
                                database.put("/log/" + uid + "/" + logYM,
                                             "/skus/" + str(
                                                 itms[dispKeys[itmX]]["skus"][skuKeys[sk]]) + "/numSold/",
                                             numsold)
                except KeyError:
                    pass
        totalRev = float(logData["totalRev"])
        totalRev += float((DBdata[dbItems]["linkTotal"] + 1) * 1.1)
        database.put("/log/" + uid + "/" + logYM, "/totalRev/", totalRev)
        ret = int(logData["retCustomers"])
        newCust = int(logData["newCustomers"])
        if (DBdata[dbItems]["ret"] == 0):
            ret += 1
            database.put("/log/" + uid + "/" + logYM, "/retCustomers/", ret)
        else:
            newCust += 1
            database.put("/log/" + uid + "/" + logYM, "/newCustomers/", newCust)
        # print(finalOrd)
        updateLog()
        if (rsp['email'] != ""):
            smtpObj = smtplib.SMTP_SSL("smtp.zoho.com", 465)
            smtpObj.login(sender, emailPass)
            try:
                subTotal = (DBdata[dbItems]["linkTotal"]) + DBdata[dbItems]["discTotal"]
            except KeyError:
                subTotal = (DBdata[dbItems]["linkTotal"])
            print(rsp['email'])
            database.put("/restaurants/" + estName + "/orders/" + str(key) + "/", "/email/", rsp['email'])
            Tax = float(subTotal * 0.1)
            Total = float(subTotal + float(Tax) + 0.1)
            subTotalStr = ('$' + format(subTotal, ',.2f'))
            TotalStr = ('$' + format(Total, ',.2f'))
            TaxStr = ('$' + format(Tax, ',.2f'))
            # print(TotalStr)
            itms = str(DBdata[dbItems]["finalOrder"])
            itms = itms.replace("::", "\n-")
            now = datetime.datetime.now(tz)
            writeStr = "your order on " + str(now.strftime("%Y-%m-%d @ %H:%M")) + "\nNAME:" + str(
                DBdata[dbItems]["name"]) + "\n\nItems\n-" + str(itms) + "\n" + str(
                DBdata[dbItems]["discStr"]) \
                       + "\n" + str(DBdata[dbItems]["togo"]) + "\n" + str(
                DBdata[dbItems]["time"]) + "\nSubtotal " + str(subTotalStr) + "\nTaxes and fees $" + str(
                round((Total - subTotal), 2)) + "\nTotal " + TotalStr
            SUBJECT = "Your Order from " + estNameStr
            message = 'Subject: {}\n\n{}'.format(SUBJECT, writeStr)
            receivers = rsp['email']
            smtpObj.sendmail(sender, receivers, message)
            smtpObj.close()
        session.clear()
        try:
            if (DBdata[dbItems]["kiosk"] == 0):
                return render_template("thankMsg.html")
            else:
                return render_template("thankMsg2.html")
        except Exception:
            return render_template("thankMsg2.html")

@app.route('/')
@app.route('/index')
def mainPage():
    return redirect(url_for('loginPage'))

@app.route("/" + uid + "rbt4813083403983494103934093480943109834093091341")
def robotInit():
    currentTime = time.time()
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    lastLogin = float(database.get("/restaurants/" + uid, "loginTime"))
    ##print()
    if ((currentTime - lastLogin) < sessionTime):
        return redirect(url_for('robotDeploy'))
    else:
        return redirect(url_for('loginPage'))

@app.route("/" + uid + "rbt1", methods=['POST'])
def robotDeployX():
    rsp = ((request.form))
    table = int(rsp["table"]) -1
    robot = int(rsp['robot']) -1
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    database.put("/restaurants/" + uid + "/robots/" + str(robot) + "/",str(table), 1)
    return redirect(url_for('robotDeploy'))

@app.route("/" + uid + "rbt1", methods=['GET'])
def robotDeploy():
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
    database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
    maxTables = len((database.get("/restaurants/" + uid, "/robots/0/")))
    rbX = len((database.get("/restaurants/" + uid, "/robots/")))
    return render_template("robotDeploy.html",max=maxTables, rbtNum=rbX,robotDeploy=str(uid + "rbt4813083403983494103934093480943109834093091341"))

'''
@app.errorhandler(500)
def not_found_error500(error):
    return redirect(url_for("loginRedo"))
@app.errorhandler(502)
def not_found_error502(error):
    return redirect(url_for("loginRedo"))
@app.errorhandler(400)
def not_found_error400(error):
    return redirect(url_for("loginRedo"))
@app.errorhandler(403)
def not_found_error403(error):
    return redirect(url_for("loginRedo"))
@app.errorhandler(405)
def not_found_error405(error):
    return redirect(url_for("loginRedo"))
@app.errorhandler(404)
def not_found_error404(error):
    return redirect(url_for("loginRedo"))
'''
if __name__ == '__main__':
    try:
        app.secret_key = 'CedarKey02'
        app.config['SESSION_TYPE'] = 'filesystem'
        sess = Session()
        sess.init_app(app)
        sess.permanent = True
        # app.debug = True
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        sys.exit()
