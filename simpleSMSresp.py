from flask import Flask, request
from pprint import pprint
import nexmo

client = nexmo.Client(key='8558cb90', secret='PeRbp1ciHeqS8sDI')

app = Flask(__name__)
NexmoNumber = '13166009096'

@app.route('/sms', methods=['GET', 'POST'])
def inbound_sms():
    data = dict(request.form) or dict(request.args)
    print(data["text"])
    number = str(data['msisdn'][0])
    msg = str(data["text"][0])
    print(number,msg)


    client.send_message({
        'from': NexmoNumber,
        'to': number,
        'text': 'gbnv'
    })


    return ('', 200)


app.run(port=3000)