'''
from twilio.rest import Client

account_sid = 'AC94b7b349a46b465fdbbf5ac96751f307'
auth_token = 'ea1399fcefbb293f5ab25254535d3a8a'
client = Client(account_sid, auth_token)

message = client.messages.create(
                     body="hello",
                     from_='+14253828604',
                     to='+17203269719'
                 )
'''

#Hello
#enter table Num
#enter order items
#items
#confirm order items
#extra items (0.25)
#ending message total, where to pay(link)
#food is approaching
for tb in range(0, 100):
    print(tb)