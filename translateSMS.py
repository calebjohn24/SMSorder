from fuzzywuzzy import fuzz
import json
import words2num
import math

import json
userOrder = "2 Burgers with Bacon and cheese. 3 Small Iced Cofees , Cream, sugar. Chicken Burger with Avacado and bacon"
userOrder = userOrder.upper()
userOrder = userOrder.replace(',', '')
userOrder = userOrder.replace('AND', '')
userOrder = userOrder.replace('WITH', '')

items = [x.strip() for x in userOrder.split('.')]

with open('menu.json') as data_file:
    data = json.load(data_file)

order = []
subtotal = 0
orderFin = ""
total = 0
for n in range(len(items)):
    qty = 1
    tokens = [z.strip() for z in items[n].split(' ')]
    for tkn in range(len(tokens)):
        try:
            int(tokens[tkn])
            qty = int(tokens[tkn])
        except ValueError:
            pass
    score = 0
    indx = 0
    for x in range(len(data['items'])):
        newScore = (fuzz.token_sort_ratio(data['items'][x]['name'],items[n]))
        if(newScore > score):
            score = newScore
            indx = x
    orderStr = str(qty) + " x " + data['items'][indx]['name'] + "$" + str(data['items'][indx]['price']) + "x" + str(qty) + " ("+"$" + format((qty*data['items'][indx]['price']),',.2f') + ")"
    orderStr = orderStr.rstrip()
    orderStr = orderStr.lstrip()
    order.append(orderStr)
    subtotal += data['items'][indx]['price'] * qty
    total = (subtotal + 0.05) *1.1
    round(total,2)
    round(subtotal,2)

for tt in range(len(order)):
    orderFin += order[tt]
    orderFin += "| "

orderFin += "processing fee $0.05|" +" " +"subtotal $" + str(subtotal) +"| "+ "tax $" + str(round((subtotal*0.1),2))+"| " +"total $" + str(total)
print(orderFin)
print("\n")
print(total)