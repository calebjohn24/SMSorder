from fuzzywuzzy import fuzz
import json
import math

import json
userOrder = "2 Burgers with bacon and cheese. 5 medium Iced Coffee with 10 no sugar cream. Fried Fish"
#userOrder = "3 medium iced coffee."
userOrder = userOrder.upper()
userOrder = userOrder.replace(',', '')
userOrder = userOrder.replace('AND', '')
userOrder = userOrder.replace('WITH', '')
if(userOrder[-1] == "."):
        userOrder = userOrder[:-1]
items = [x.strip() for x in userOrder.split('.')]

with open('menu.json') as data_file:
    data = json.load(data_file)

order = []
subtotal = 0
orderFin = "your order "
total = 0
if (len(items) < 1):
    items.append(userOrder)
for n in range(len(items)):
    qty = 1
    compStr = ""
    notes = ""
    toppings = ""
    tokens = [z.strip() for z in items[n].split(' ')]
    for tkn in range(len(tokens)):
        if(tokens[tkn] == "NO"):
            tokens[tkn] = ""
            notes += str("NO " + tokens[tkn + 1])
            notes += " "
            tokens[tkn + 1] = ""
            if((tkn + 2) <= len(tokens)):
                print(tokens[tkn + 2])
                toppings = notes + " " +str(tokens[tkn +2])
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
        newScore = (fuzz.token_sort_ratio(data['items'][x]['name'],compStr))
        if(newScore > score):
            score = newScore
            indx = x
        if(newScore == score):
            newScore = (fuzz.ratio(data['items'][x]['name'], compStr))
            if (newScore > score):
                score = newScore
                indx = x
    writeStr = str(data['items'][indx]['name'])
    print(score,(fuzz.partial_ratio(data['items'][x]['name'], notes)))
    if(score > 80):
        orderStr = str(qty) + "x " + writeStr  + " $" + str(data['items'][indx]['price']) + "x" + str(qty) + "("+"$" + format((qty*data['items'][indx]['price']),',.2f') + ")"
        orderStr = orderStr.rstrip()
        orderStr = orderStr.lstrip()
        order.append(orderStr)
        subtotal += data['items'][indx]['price'] * qty
        total = (subtotal + 0.20) *1.10
        total = round(total,2)
        subtotal = round(subtotal,2)
    else:
        orderStr = "invalid item"
        order.append(orderStr)

for tt in range(len(order)):
    orderFin += order[tt]
    orderFin += "| "

orderFin += "conv.fee$0.05|" +" " +"subtotal$" + str(subtotal) +"| "+ "tax$" + str(round((subtotal*0.1),2))+"| " +"total$" + str(total)
print(orderFin)
print("\n")
print(total)