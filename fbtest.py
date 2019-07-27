from firebase import firebase
import datetime
import time

databse = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")

v = databse.get("/", "tickets")
print(v)
#databse.put("/tickets/" + str(len(v)), "/number/",10003000)

logDate = (datetime.datetime.now().strftime("%Y-%m"))
print(logDate)
currentVal = databse.get("/log/"+ str(logDate) + "/", "orders")
currentacct = databse.get("/log/"+ str(logDate) + "/", "acct")
print(currentVal)
databse.put("/log/" + str(logDate), "/orders/", (currentVal+1))
databse.put("/log/" + str(logDate), "/acct/", (currentacct + 0.05))
