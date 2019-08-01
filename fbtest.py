from firebase import firebase
NAME = "caleb"
database = firebase.FirebaseApplication("https://cedarrestaurants-ad912.firebaseio.com/")
estName = "TestRaunt"
#database.put("/users/", "/" + str(1) + "/restaurants/" + estName +"/" +str(0)+"/items/" + str(0)+"/"+ "name", "NAME")
UserData = database.get("/users/" + str(1) +"/restaurants/",estName)
database.put("/users", "/" + str(1) + "/restaurants/" + estName + "/" + str(len(UserData)-1) + "/order/", "orderSTR")
print(UserData)
print(len(UserData))