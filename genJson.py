import json
file = open("menu.json","r")
data = json.load(file)
print(len(data['items']))
sizeArr = []
extras = []
name = input("enter item name ->")
name = name.upper()
numSizes = int(input("enter number of sizes ->"))
for sz in range((numSizes)):
    sizeName = input("enter size name (if only one size enter u) ->")
    sizeName = sizeName.upper()
    sizePrice = float(input("enter size price ->"))
    sizeArr.append([sizeName,sizePrice])
numExtras = int(input("enter number of extras ->"))
for ex in range(numExtras):
    extraName = input("enter extra/topping name (if none enter u) ->")
    extraName = extraName.upper()
    extraPrice = float(input("enter price ->"))
    extras.append([extraName,extraPrice])

data['items'].append({
    'name': name,
    'sizes': sizeArr,
    'extras': extras
})
file = open("menu.json","w")
json.dump(data, file)