from firebase import firebase
import json
database = firebase.FirebaseApplication("https://cedarfb2.firebaseio.com/")
uid = "JYzVI5fR5KW399swMP9zgEMNTxu2"
data = (database.get("restaurants/" + uid,"/menu/items/"))
print(type(data))
for mn in range(len(data)):
    if(data[mn] != None):
        print(data[mn]['extras'])