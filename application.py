from flask import Flask, request
from twilio.twiml.messaging_response import Message, MessagingResponse
import twilio
from firebase import firebase
import time
import json
from fuzzywuzzy import fuzz
import datetime

SendNum = "+14253828604"

databse = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
estName = "NAME"
link = "LINK"
# set up Flask to connect this code to the local host, which will
# later be connected to the internet through Ngrok
app = Flask(__name__)

def transalteOrder(msg, FBtoken):
    userOrder = msg
    userOrder = userOrder.upper()
    userOrder = userOrder.replace(',', '')
    userOrder = userOrder.replace('AND', '')
    userOrder = userOrder.replace('WITH', '')
    userOrder = userOrder.replace('OR', '')
    if (userOrder[-1] == "."):
        userOrder = userOrder[:-1]
    items = [x.strip() for x in userOrder.split('.')]

    with open('menu.json') as data_file:
        data = json.load(data_file)

    order = []
    subtotal = 0
    orderFin = "your order" + "\n"
    total = 0
    if (len(items) < 1):
        items.append(userOrder)
    for n in range(len(items)):
        qty = 1
        compStr = ""
        notes = ""
        tokens = [z.strip() for z in items[n].split(' ')]
        for tkn in range(len(tokens)):
            if (tokens[tkn] == "NO"):
                tokens[tkn] = ""
                notes += str("NO " + tokens[tkn + 1])
                notes += " "
                tokens[tkn + 1] = ""
        for tkn2 in range(len(tokens)):
            try:
                int(tokens[tkn2])
                qty = int(tokens[tkn2])
                break
            except ValueError:
                pass
        for zx in range(len(tokens)):
            compStr += tokens[zx]
            compStr += " "
        score = 0
        indx = 0
        for x in range(len(data['items'])):
            newScore = (fuzz.token_sort_ratio(data['items'][x]['name'], compStr))
            if (newScore > score):
                if (notes == ""):
                    score = newScore
                    indx = x
                elif (notes != ""):
                    compScore = fuzz.partial_ratio(data['items'][x]['name'], notes)
                    if (compScore < 50):
                        score = newScore
                        indx = x
            if (newScore == score):
                newScore = (fuzz.ratio(data['items'][x]['name'], compStr))
                if (newScore > score):
                    score = newScore
                    indx = x
        writeStr = str(data['items'][indx]['name'])
        print(score, (fuzz.partial_ratio(data['items'][x]['name'], notes)))
        if (score > 80):
            orderStr = str(qty) + "x " + writeStr + " $" + str(data['items'][indx]['price']) + "x" + str(
                qty) + "(" + "$" + format((qty * data['items'][indx]['price']), ',.2f') + ")"
            orderStr = orderStr.rstrip()
            orderStr = orderStr.lstrip()
            order.append(orderStr)
            subtotal += data['items'][indx]['price'] * qty
            total = (subtotal + 0.20) * 1.10
            total = round(total, 2)
            subtotal = round(subtotal, 2)
        else:
            orderStr = "invalid item"
            order.append(orderStr)
    for tt in range(len(order)):
        orderFin += order[tt]
        orderFin += "\n"

    orderFin += "conv. fee $0.20" + "\n" + "subtotal $" + str(subtotal) + "\n" + "tax $" + str(
        round((subtotal * 0.1), 2)) + "\n" + "total $" + str(total) + "\n" +"pay here - " + str(genPayment(total))
    databse.put("/tickets/" + str(FBtoken), "/processedOrder/", orderFin)
    databse.put("/tickets/" + str(FBtoken), "/subTotal/", subtotal)
    databse.put("/tickets/" + str(FBtoken), "/total/", total)
    orderFin = orderFin.lower()
    return orderFin

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
                   "3 Iced Coffees with Cream and sugar. Burger with Bacon.' " \
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