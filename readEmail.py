import easyimap

login = "payments@cedarrobots.com"
password = "CedarPayments1!"
nameArr = []
addressArr = []
emailArr = []
dateTimeArr = []
imapper = easyimap.connect('imappro.zoho.com', login, password)
for mail_id in imapper.listids(limit=100):
    mail = imapper.mail(mail_id)
    nameSTR = (mail.from_addr).lower()
    nameEnd = nameSTR.find("via") - 1
    name = nameSTR[0:nameEnd]
    nameArr.append(name)
    emailSTR = mail.title
    emailEnd = emailSTR.find("from")+5
    email = emailSTR[emailEnd::]
    emailArr.append(email)
    dateTimeSTR = mail.date
    dateTimeZoneEnd = dateTimeSTR.find("-")
    timeZone = dateTimeSTR[dateTimeZoneEnd::]
    dateTimeDayEnd = dateTimeSTR.find(",")
    day = dateTimeSTR[0:dateTimeDayEnd]
    timeEnd = dateTimeSTR.find(":")
    time = dateTimeSTR[(timeEnd-2):(timeEnd+6)]
    year = dateTimeSTR[(timeEnd-7):(timeEnd-3)]
    month = dateTimeSTR[(timeEnd-11):(timeEnd-8)]
    date = dateTimeSTR[(timeEnd-14):(timeEnd-12)]
    dateTimeArr.append([["timezone",timeZone],["day", day],["time",time],["year",year],["month",month],["date",date]])
    bodyText = (mail.body)
    bodyText = bodyText.lower()
    ship = (bodyText.find("shipping information"))
    shipEnd = (bodyText.find("end -->"))
    shippingInfo = (bodyText[ship:shipEnd])
    shippingInfo =shippingInfo.replace("<","")
    shippingInfo =shippingInfo.replace("/", "")
    shippingInfo =shippingInfo.replace(">", "")
    shippingInfo =shippingInfo.replace('style="display:inline;"', "")
    shippingInfo =shippingInfo.replace("br", "")
    shippingInfo =shippingInfo.replace("span", "")
    shippingInfo = shippingInfo.replace('style="display: inline;"', "")
    shippingInfo = shippingInfo.replace("-- addressdisplaywrapper : start --  ", "")
    shippingInfo = shippingInfo.replace("!", "")
    shippingInfo = shippingInfo.replace("-", "")
    shippingInfo = shippingInfo.replace("addressdisplaywrapper", "")
    addrBegin = shippingInfo.find(name) + (len(name)) + 3
    shippingInfo = (shippingInfo[addrBegin::])
    commaSplicer = shippingInfo.find(",")
    state = shippingInfo[(commaSplicer + 5): (commaSplicer+7)]
    zipCode = shippingInfo[(commaSplicer+11):(commaSplicer + 16)]
    addrEnd = shippingInfo.find("  ")
    streetAdr = (shippingInfo[0:addrEnd])
    city = shippingInfo[(addrEnd+3):(commaSplicer-3)]
    addressArr.append([["state",state],["zipCode",zipCode],["city",city],["streetAdr",streetAdr]])

for names in range(len(nameArr)):
    print(nameArr[names])
    print(emailArr[names])
    print(dateTimeArr[names])
    print(addressArr[names])