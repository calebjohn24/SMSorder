from firebase import firebase
import pyrebase as fbAuth

config = {
  "apiKey": "AIzaSyB2it4zPzPdn_bW9OAglTHUtclidAw307o",
  "authDomain": "cedarchatbot.firebaseapp.com",
  "databaseURL": "https://cedarchatbot.firebaseio.com",
  "storageBucket": "cedarchatbot.appspot.com",
}

firebaseAuth = pyrebase.initialize_app(config)
auth = firebaseAuth.auth()

# Log the user in
try:
    user = auth.sign_in_with_email_and_password("cajohn0205@gmail.com", "test123")
    print(user['localId'])
    authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W', 'cajohn0205@gmail.com', extra={'id': 123})
    fireapp = firebase.FirebaseApplication('https://cedarchatbot.firebaseio.com/',  authentication=authentication)
    print(fireapp.get("/restaurants/",user["localId"]))
except Exception:
    print("incorrect password")