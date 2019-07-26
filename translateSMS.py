from fuzzywuzzy import fuzz
import json
import words2num

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
    orderStr = "" + data['items'][indx]['name']
    orderStr = orderStr.rstrip()
    orderStr = orderStr.lstrip()
    order.append(orderStr)
    total += data['items'][indx]['price'] * qty

print(order,total)