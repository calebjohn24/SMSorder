import json
import re
from datetime import datetime
from datetime import timedelta

import requests

client_id = "AacwZ9jjS9DsRvvUdHS3T5b1HjutCtUro7Vpky8opLGDwm9Rx5YbrBqDkWEbZ8WT5jIEVWTe6fr5Q86M"
secret_id = "EJypi6G1yfgUSJmKnFLNJTsxbyj0m6AIwRF-W2jer_pK_v0mBNUC97fZ377tInigCpLU8URsetyPu13o"

def token():
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en_US',
    }

    data = [
        ('grant_type', 'client_credentials'),
    ]

    response = requests.post('https://api.paypal.com/v1/oauth2/token', headers=headers, data=data, auth=(
        client_id,
        secret_id))
    data = json.loads(response.text)

    return data['access_token']


def transaction_history(token, start_time, end_time):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
    }

    params = (
        ('start_date', start_time),  # dates must look like this: '2018-06-10T23:20:50.52Z'
        ('end_date', end_time),
        ('fields', 'payer_info, cart_info'),  # all
    )

    results = []
    response = requests.get('https://api.paypal.com/v1/reporting/transactions', headers=headers, params=params)
    if response.status_code != 200:
        print('transaction_history: failed with HTTP code', response.status_code)
        return results
    data = json.loads(response.text)
    print(data)
    print("no errors")
    file = open("transaction.json", "w")
    json.dump(data, file)


    return results


i = token()

time_end = datetime.utcnow()+ timedelta(days = 2)
time_start = time_end + timedelta(days = -3)

time_start = re.sub(r" +", "T", time_start.strftime('%Y-%m-%dT%H:%M:%S.%f'))[:-4] + 'Z'
time_end = re.sub(r" +", "T", time_end.strftime('%Y-%m-%dT%H:%M:%S.%f'))[:-4] + 'Z'

x = transaction_history(i, time_start, time_end)
