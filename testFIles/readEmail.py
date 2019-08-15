import easyimap
from bs4 import BeautifulSoup
import uszipcode
from datetime import datetime

from fuzzywuzzy import fuzz
currentSecond= datetime.now().second
currentMinute = datetime.now().minute
currentHour = datetime.now().hour

currentMonth = datetime.now().month
currentYear = datetime.now().year
currentDate = datetime.now().day
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sept","Oct","Nov","Dec"]
nameFIND = "caleb john"
dateFIND = "29"
monthFIND = "Jul"
year = "2019"
time = ""
login = "payments@cedarrobots.com"
password = "CedarPayments1!"
number = "720-326-9719"
nameArr = []
addressArr = []
emailArr = []
dateTimeArr = []
imapper = easyimap.connect('imappro.zoho.com', login, password)
for mail_id in imapper.listids(limit=100):
    mail = imapper.mail(mail_id)
    bodyText = (mail.body)
    soup = BeautifulSoup(bodyText, 'lxml')
    bodyText = (soup.get_text())
    strStart = bodyText.find("Hello")
    bodyText = str(bodyText[strStart:])
    bodyText = bodyText.replace("  ", "")
    bodyText = bodyText.replace("\n", "")
    #print(bodyText)
    emailStart = bodyText.find("(")
    emailEnd = bodyText.find(")")
    email = (bodyText[(emailStart + 1):emailEnd])
    ship = (bodyText.find("Shipping"))
    shipEnd = (bodyText.find("United States"))
    adrText = str(bodyText[ship + (len("shipping")):(shipEnd)])
    adrText = adrText.replace("  ","")
    adrText = adrText.replace("confirmed","")
    adrText = adrText.replace(" address -","")
    adrText = adrText.replace(" information:", "")
    adrText = adrText.rstrip()
    adrText = adrText.lstrip()
    adrText = adrText.upper()
    name = ""
    streetAdrIndx = 0
    for ltr in range(len(adrText)):
        try:
            testStr = int(adrText[ltr])
            streetAdrIndx = ltr
            break
        except ValueError:
            name += adrText[ltr]
    name = name.upper()
    streetAdrFull = adrText[streetAdrIndx:]
    zipCode = (streetAdrFull[-5:])
    streetAdrCity = (streetAdrFull[:-5])
    search = uszipcode.SearchEngine(simple_zipcode=True)
    zipCitySearch = search.by_zipcode(zipCode).common_city_list
    score = 0
    city = ""
    if(zipCitySearch != None):
        for cities in range(len(zipCitySearch)):
            newScore = fuzz.partial_ratio(streetAdrCity,str(zipCitySearch[cities]).upper())
            if(newScore > score):
                score = newScore
                city = str(zipCitySearch[cities]).upper()
        cityIndx = streetAdrCity.find(city)
        streetAdr = streetAdrCity[:cityIndx]
        print(streetAdr,city,zipCode,name,email)
    else:
        pass



    ''' 
    ship = (bodyText.find("shipping information"))
    shipEnd = (bodyText.find("end -->"))
    UUID = (bodyText[(bodyText.find("uuid")+5) : ((bodyText.find("uuid")) + 9)])
    #print(UUID)
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
    #print(shippingInfo)
    addrBegin = shippingInfo.find(name) + (len(name)) + 3
    shippingInfo = (shippingInfo[addrBegin::])
    commaSplicer = shippingInfo.find(",")
    state = shippingInfo[(commaSplicer + 5): (commaSplicer+7)]
    zipCode = shippingInfo[(commaSplicer+11):(commaSplicer + 16)]
    addrEnd = shippingInfo.find("  ")
    streetAdr = (shippingInfo[0:addrEnd])
    city = shippingInfo[(addrEnd+3):(commaSplicer-3)]
    addressArr.append([["state",state],["zipCode",zipCode],["city",city],["streetAdr",streetAdr]])
    '''
''' 
for names in range(len(nameArr)):
    print(nameArr[names], "name")
    print(emailArr[names], "email")
    for adr in range(len(addressArr[names])):
        print(addressArr[names][adr][0], addressArr[names][adr][1])
'''