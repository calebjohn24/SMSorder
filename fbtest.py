from firebase import firebase
import datetime
NAME = "caleb"
database = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
estName = "TestRaunt"
#database.put("/users/", "/" + str(1) + "/restaurants/" + estName +"/" +str(0)+"/items/" + str(0)+"/"+ "name", "NAME")
def genUsr(name,number):


    timeStamp = datetime.datetime.today()
    #database.put("/users/", "/" + str(len(UserData)) +  "/name", name)
    #database.put("/users/", "/" + str(len(UserData)) +  "/number", number)
    #database.put("/users/", "/" + str(len(UserData)-1) + "/restaurants/" + estName +"/" +str(len(UserData[]))+ "/time", str(timeStamp))
'''
UserData = database.get("/","users")
for usr in range(len(UserData)):
    print(UserData[usr])
'''
indx = 1
numOrders = database.get("/users/"+str(indx)+"/restaurants/", estName)
numOrders = database.get("/users/" + str(indx) + "/restaurants/", estName)
loyaltyCard = numOrders[len(numOrders)-1]["loyaltyCard"]
print(loyaltyCard)
#database.put("/users/", "/" + str(1) + "/restaurants/" + estName + "/" + str((len(numOrders)-1)) + "/time",str(76))

logDate = (datetime.datetime.now().strftime("%Y-%m"))
database.put("/log/" + estName + "/" + str(logDate), "/exp/", 0)
currentVal = (database.get("/log/" + str(estName) + "/" + str(logDate) + "/", "orders"))
currentacct = (database.get("/log/" + str(estName) + "/" + str(logDate) + "/", "acct"))
if(currentacct == None):
    database.put("/log/" + estName + "/" + str(logDate), "/orders/", (1))
    database.put("/log/" + estName + "/" + str(logDate), "/acct/", (0.2))
else:
    database.put("/log/" + estName + "/" + str(logDate), "/orders/", (currentVal + 1))
    database.put("/log/" + estName + "/" + str(logDate), "/acct/", (currentacct + 0.20))