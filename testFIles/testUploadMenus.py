import pyrebase
config = {
  "apiKey": "AIzaSyB2it4zPzPdn_bW9OAglTHUtclidAw307o",
  "authDomain": "cedarchatbot.firebaseapp.com",
  "databaseURL": "https://cedarchatbot.firebaseio.com",
  "storageBucket": "cedarchatbot.appspot.com",
}
estNameStr = "TestRaunt"
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()
path = "TestRaunt-lunch-dinner-menu.pdf"
storage.child(estNameStr +"/menus/"+path).put(path)
