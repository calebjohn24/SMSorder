import time
from flask import Flask, request, Response
import plivo
from plivo import plivoxml
botNumber = "14255992978"
client = plivo.RestClient(auth_id='MAYTVHN2E1ZDY4ZDA2YZ', auth_token='ODgzZDA1OTFiMjE2ZTRjY2U4ZTVhYzNiODNjNDll')
app = Flask(__name__)

def getResp(msg):
    retStr = "this is a test" + " " + msg
    return retStr

@app.route('/sms',methods=['GET','POST'])
def inbound_sms():
    # Sender's phone number
    from_number = request.values.get('From')
    # Receiver's phone number - Plivo number
    to_number = request.values.get('To')
    # The text which was received
    text = request.values.get('Text')
    print('Message received - From: %s, To: %s, Text: %s' % (from_number, to_number, text))
    print(type(text))
    resp = getResp(text)
    response = plivoxml.ResponseElement()
    response.add(
        plivoxml.MessageElement(
            resp,  # body/The text which was received
            src=to_number,  # Sender's phone number
            dst=from_number,  # Receiver's phone Number
            type='sms',
            callback_url='https://61296054.ngrok.io/sms status/',
            callback_method='POST'))
    return Response(response.to_string(), mimetype='application/xml')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)