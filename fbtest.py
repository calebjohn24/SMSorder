from firebase import firebase
NAME = "caleb"
database = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
restaurantName = "TestRaunt"
DBdata = database.get("/restaurants/TestRaunt","orders")
print(len(DBdata))
#print(len(DBdata))
#database.put("/restaurants/" + restaurantName +"/orders/"+str(len(DBdata)),"/name/1","testPut")
for db in range(len(DBdata)):
    print(DBdata[db]["name"])