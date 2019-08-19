import pygsheets
import pandas as pd
import datetime
from firebase import firebase
import calendar
import json
logDate = (datetime.datetime.now().strftime("%Y-%m-%d"))
logYM = (datetime.datetime.now().strftime("%Y-%m"))
infoFile = open("info.json")
info = json.load(infoFile)
uid = info['uid']
estName = info['uid']
estNameStr = info['name']
shortUID = info['shortUID']
currentTime = str((float(datetime.datetime.now().hour))+((float(datetime.datetime.now().minute))/100.0))
authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
#authorization
gc = pygsheets.authorize(service_file='CedarChatbot-70ec2d781527.json')
email = "cedarchatbot@appspot.gserviceaccount.com"

logData = database.get("/log/" + uid + "/", logYM)
print(logData['MonthlySKUdata'])
print(type(logData['MonthlySKUdata']))
currentSKU = ["1122",3.5]
price = currentSKU[1]
for skuData in range(len(logData['MonthlySKUdata'])):
    if(logData['MonthlySKUdata'][skuData] != None):
        if(logData['MonthlySKUdata'][skuData]["SKU"] == currentSKU[0]):
            print()
            numSold = int(logData["MonthlySKUdata"][skuData]["numSold"])
            numSold +=1
            rev = float(logData["MonthlySKUdata"][skuData]["rev"])
            rev += price
            database.put("/log/" + uid + "/" + logYM, "/MonthlySKUdata/" + str(skuData) + "/rev", rev)
            database.put("/log/" + uid + "/" + logYM, "/MonthlySKUdata/" + str(skuData) + "/numSold", numSold)
            break