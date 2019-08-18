import datetime
import calendar
import json
logDate = (datetime.datetime.now().strftime("%Y-%m-%d"))
print(datetime.datetime.now().today().weekday())
print("ll")
print(int(datetime.datetime.now().hour))
print((int(datetime.datetime.now().minute)))
currentTime = str(int(datetime.datetime.now().hour))+"."+str(((datetime.datetime.now().minute)))
print(currentTime)
print("lll")
print(calendar.day_name[datetime.datetime.now().today().weekday()])
print(len(calendar.day_name))
print(logDate)