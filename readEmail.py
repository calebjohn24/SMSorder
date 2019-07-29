import easyimap

login = "payments@cedarrobots.com"
password = "CedarPayments1!"

imapper = easyimap.connect('imappro.zoho.com', login, password)
for mail_id in imapper.listids(limit=100):
    mail = imapper.mail(mail_id)
    print(mail.from_addr)
    print("\n")
    print(mail.title)
    print("\n")
    print(mail.date)