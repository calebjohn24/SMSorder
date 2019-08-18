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
database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/")
#authorization
gc = pygsheets.authorize(service_file='CedarChatbot-70ec2d781527.json')
email = "cedarchatbot@appspot.gserviceaccount.com"

# Create empty dataframe
SkuDF = pd.DataFrame()
NameDF = pd.DataFrame()
# Create a column

#open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)
sh = gc.open('TestRaunt')
#select the first sheet
startHr = 0
endHr = 0

wks = sh.worksheet_by_title(logYM +"-sales")
log = (database.get("log/" + uid, "/"+logYM+"/"))
menu = (database.get("restaurants/" + uid, "/menu/items/"))
SKUs = []
Names = []
startHr = int(database.get("restaurants/" + uid, "/OChrs/open/"))
endHr = int(database.get("restaurants/" + uid, "/OChrs/close/"))
for dt in range(len(menu)):
    if(menu[dt] != None):
        SKUs.append(menu[dt]['sku'])
        Names.append(menu[dt]['name'])

MenuHrs = ((database.get("restaurants/" + uid, "/Hours/")))
menKeys = list(MenuHrs.keys())
print(menKeys)


''' 
SkuDF['SKU'] = SKUs
NameDF['Name'] = Names
wks.set_dataframe(SkuDF, (1, 1))
wks.set_dataframe(NameDF,(1,2))
'''
ZipCodes = database.get("log/" + uid+"/"+logYM, "/zipCodes/")
for zips in range(len(ZipCodes)):
    print(ZipCodes[zips]["name"])
    database.put("/log/" + uid + "/" + logYM + "/zipCodes/" + str(zips), "/NumOrders/", 0)

''' 
#starts with 1 not 0
#wks.set_menuframe(df,(1,1))
for MSD in range(len(menu)):
    if (menu[MSD] != None):
        database.put("/log/" + uid + "/" + logYM + "/MonthlySKUdata/" + str(MSD) ,"/SKU/", str(menu[MSD]['sku']))
        database.put("/log/" + uid + "/" + logYM + "/MonthlySKUdata/" + str(MSD) ,"/name/", str(menu[MSD]['name']))
        database.put("/log/" + uid + "/" + logYM + "/MonthlySKUdata/" + str(MSD) , "/numSold/", 0)
        database.put("/log/" + uid + "/" + logYM + "/MonthlySKUdata/" + str(MSD) , "/rev/", 0)
        database.put("/log/" + uid + "/" + logYM + "/MonthlySKUdata/" + str(MSD) , "/hours/"+str(datetime.datetime.now().hour), 0)
        database.put("/log/" + uid + "/" + logYM + "/MonthlySKUdata/" + str(MSD) , "/day/" + str(calendar.day_name[datetime.datetime.now().today().weekday()]),0)

for cal in range(len(calendar.day_name)-1):
    database.put("/log/" + uid + "/" + logYM + "/days/" +  str(calendar.day_name[cal]) , "/TicketSize/", 0)
    database.put("/log/" + uid + "/" + logYM + "/days/" +  str(calendar.day_name[cal]) , "/TotalDuration/", 0)
    database.put("/log/" + uid + "/" + logYM + "/days/" +  str(calendar.day_name[cal]) , "/NumOrders/", 0)
    database.put("/log/" + uid + "/" + logYM + "/days/" +  str(calendar.day_name[cal]) , "/TicketTotal/", 0)

for hrs in range(startHr,endHr):
    database.put("/log/" + uid + "/" + logYM + "/hours/" + str(hrs), "/TicketSize/", 0)
    database.put("/log/" + uid + "/" + logYM + "/hours/" + str(hrs), "/TotalDuration/", 0)
    database.put("/log/" + uid + "/" + logYM + "/hours/" + str(hrs), "/NumOrders/", 0)
    database.put("/log/" + uid + "/" + logYM + "/hours/" + str(hrs), "/TicketTotal/", 0)

'''