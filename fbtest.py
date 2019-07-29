from paypalrestsdk import Invoice, configure, WebProfile
import logging

configure({
  "mode": "live", # sandbox or live
  "client_id": "AacwZ9jjS9DsRvvUdHS3T5b1HjutCtUro7Vpky8opLGDwm9Rx5YbrBqDkWEbZ8WT5jIEVWTe6fr5Q86M",
  "client_secret": "EJypi6G1yfgUSJmKnFLNJTsxbyj0m6AIwRF-W2jer_pK_v0mBNUC97fZ377tInigCpLU8URsetyPu13o" })
logging.basicConfig(level=logging.INFO)

logging.basicConfig(level=logging.INFO)

history = WebProfile.all()
print(history)

print("List WebProfile:")
for profile in history:
    print("  -> WebProfile[%s]" % (profile.name))