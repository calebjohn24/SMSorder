from flask import Flask, request
from twilio import twiml
import time
from firebase import firebase
import datetime
import json

database = firebase.FirebaseApplication('https://cedarrestaurants-ad912.firebaseio.com/', None)
# set up Flask to connect this code to the local host, which will
# later be connected to the internet through Ngrok
EstName = "Name"
menuLink = "url"
with open('menu.json') as f:
    menuFile = json.load(f)
foodI = menuFile["Items"]

def genBill(order):
    items = []
    order = str(order)
    order = order.upper()
    print(order)
    items = [x.strip() for x in order.split(',')]
    for indx in range(len(items)):
        item = (items[indx])
        max = 0
        index = 0
        for x in range(len(foodI)):
            menuItem = (foodI[x]["Name"])
            a = list(set(menuItem) & set(item))
            if(len(a) > max):
                max = len(a)
                index = x
        items.append([foodI[index]["Name"],foodI[index]["Price"]])



def genPaymentLink(orderNum, total):
    print(orderNum)


def getReply(msg, number):
    print(msg)
    if (msg == "order" or msg == "oder" or msg == "prder" or msg == "ordet"):
        reply = "Hi, welcome to " + EstName + " what would you like to order today, please use peroidsto seperate items" \
                                              "you can view the menu here "+ menuLink
        return reply
    else:
        db = database.get("/", "tickets")
        for nums in range(len(db) - 1):
            if (db[nums]["number"] == number and abs(int(db[nums][time]) - time.time()) < 3600):
                stageVal = database.get("/tickets/" + str(db[nums]) + "/", "stage")
                if (stageVal == 0):
                    # convert string to order
                    order = "str"
                    total = 0
                    reply = order + ".....enter 1 if order is to-go, or 2 if order is for here"
                    database.put('/tickets/' + str(db[nums]) + "/", "stage", 1)
                    database.put('/tickets/' + str(db[nums]) + "/", "subtotal", total)
                    database.put('/tickets/' + str(db[nums]) + "/", "Total", (total * 1.1 + 0.12))
                    database.put('/tickets/' + str(db[nums]) + "/", "stage", 1)
                    return reply

                elif (stageVal == 1):
                    if (msg == "1"):
                        database.put('/tickets/' + str(db[nums]) + "/", "togo", 0)
                    elif (msg == "2"):
                        database.put('/tickets/' + str(db[nums]) + "/", "togo", 1)
                    database.put('/tickets/' + str(db[nums]) + "/", "stage", 2)
                    reply = "Enter 1 to pay online and skip the line, enter 2 to pay at store"
                    return reply

                elif (stageVal == 2):
                    togo = database.get("/tickets/" + str(db[nums]) + "/", "togo")
                    if (msg == "1"):
                        database.put('/tickets/' + str(db[nums]) + "/", "pay", 0)
                        genPayment(db[nums])
                        url = ""
                        link = "click this link to pay " + url
                        database.put('/tickets/' + str(db[nums]) + "/", "stage", 3)
                        if (togo == 0):
                            reply = "Thank you for your order, you can skip the line and take a seat." \
                                    "Once you take a seat please enter the number at your table" + link
                            now = datetime.datetime.now()
                            mn = now.month
                            yr = now.year
                            logDate = str(mn) + "-" + str(yr)
                            numOrders = database.get("/log/", str(logDate))
                            database.put('/log/', str(logDate), (numOrders + 1))
                            return reply
                        elif (togo == 1):
                            reply = "Thank you for your order, you can pick up your order at the counter, " \
                                    "and skip the line!" + link
                            now = datetime.datetime.now()
                            mn = now.month
                            yr = now.year
                            logDate = str(mn) + "-" + str(yr)
                            numOrders = database.get("/log/", str(logDate))
                            database.put('/log/', str(logDate), (numOrders + 1))
                            return reply
                    elif (msg == "2"):
                        database.put('/tickets/' + str(db[nums]) + "/", "pay", 1)
                        database.put('/tickets/' + str(db[nums]) + "/", "stage", 3)
                        if (togo == 0):
                            reply = "Thank you for your order once you take a set please enter the number at your table"
                            now = datetime.datetime.now()
                            mn = now.month
                            yr = now.year
                            logDate = str(mn) + "-" + str(yr)
                            numOrders = database.get("/log/", str(logDate))
                            database.put('/log/', str(logDate), (numOrders + 1))
                            return reply
                        elif (togo == 1):
                            reply = "Thank you for your order, please pay at the register once you have paid"
                            now = datetime.datetime.now()
                            mn = now.month
                            yr = now.year
                            logDate = str(mn) + "-" + str(yr)
                            numOrders = database.get("/log/", str(logDate))
                            database.put('/log/', str(logDate), (numOrders + 1))
                            return reply

                elif (stageVal == 3):
                    print("s1")
                    togo = database.get("/tickets/" + str(db[nums]) + "/", "togo")
                    if (togo == 0):
                        for tb in range(0, 101):
                            if (str(tb) == msg):
                                database.put('/tickets/' + str(db[nums]) + "/", "tableNum", int(tb))
                                database.put('/tables/' + str(tb) + "/", "deliver", 1)
                                reply = "Thank you, you will receive a text when your food is on the way"
                                return reply


def genTicket(number):
    ticket = str(number) + "-" + str(int(time.time()))
    rx = database.get("/", "tickets")
    idNos = (len(rx))
    database.put('/tickets/', idNos, ticket)
    database.put('/tickets/' + str(idNos) + "/" + str(ticket) + "/", "stage", 0)
    return ticket


app = Flask(__name__)


# Main method. When a POST request is sent to our local host through Ngrok
# (which creates a tunnel to the web), this code will run. The Twilio service # sends the POST request - we will set this up on the Twilio website. So when # a message is sent over SMS to our Twilio number, this code will run
@app.route('/', methods=['POST'])
def sms():
    # Get the text in the message sent
    number = request.form['From']
    message_body = request.form['Body']
    if (message_body == "order"):
        genTicket(number)
    # Create a Twilio response object to be able to send a reply back (as per         # Twilio docs)
    resp = twiml.Response()

    # Send the message body to the getReply message, where
    # we will query the String and formulate a response
    replyText = getReply(message_body, number)

    # Text back our response!
    resp.message(replyText)
    return str(resp)


# when you run the code through terminal, this will allow Flask to work
if __name__ == '__main__':
    app.run()
