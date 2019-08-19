from fpdf import FPDF
from firebase import firebase
estNameStr = "TestRaunt"
uid =  "vjsoqWdhbEYIKH4q00Zrp20UFHH3"

fontName = "helvetica"
authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W',
                                                     'cajohn0205@gmail.com', extra={'id': 123})
database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)
menu = (database.get("restaurants/" + uid, "/menu/items/"))
hours =(database.get("restaurants/" + uid, "/Hours/"))
print(hours)
keys = list(hours.keys())
for menuNames in range(len(keys)):
    pdf = FPDF()
    pdf.add_page()
    yStart = 20
    pdf.set_font(fontName, size=24, style="BU")
    text = estNameStr + " " +str([keys[menuNames]][0]) + " Menu"
    pdf.multi_cell(200, 10, txt=text, align="C")
    yStart += 10
    for dt in range(len(menu)):
        if(menu[dt] != None):
            if((menu[dt]["sizes"][0][1] != -1)):
                name = menu[dt]["name"].lower()
                print(name)
                print(menu[dt]["time"], str([keys[menuNames]][0]))
                print(menu[dt]["time"] == str([keys[menuNames]][0]))
                print(str(menu[dt]["time"]).lower() == "all")
                print("\n")
                if(str(menu[dt]["time"]).lower() == "all" or str(menu[dt]["time"]).lower() == str([keys[menuNames]][0]).lower()):
                    name = menu[dt]["name"].lower()
                    sizes = []
                    toppings = []
                    for sz in range(len(menu[dt]["sizes"])):
                        sizes.append([str(menu[dt]["sizes"][sz][0]).lower(),menu[dt]["sizes"][sz][1]])
                    if (str(menu[dt]["extras"][0][0]) != ""):
                        for ex in range(len(menu[dt]["extras"])):
                            toppings.append([str(menu[dt]["extras"][ex][0]).lower(),menu[dt]["extras"][ex][1]])
                    #pdf.line(0, yStart, 500000, yStart)
                    pdf.set_font(fontName, size=18, style="B")
                    text = name
                    pdf.multi_cell(100, 10, txt=text, align="L")
                    yStart += 10
                    text = ""
                    pdf.set_font(fontName, size=14, style="B")
                    if (len(sizes) > 1):
                        text = "-Sizes:"
                        pdf.multi_cell(100, 7, txt=text, align="L")
                        yStart += 7
                        pdf.set_font(fontName, size=12, style="")
                        text = ""
                        for szs in range(len(sizes)):
                            text += "     -"
                            text += sizes[szs][0]
                            text += " ~ $" + str(sizes[szs][1])
                            pdf.multi_cell(100, 7, txt=text, align="L")
                            yStart += 7
                            text = ""
                    else:
                        pdf.set_font(fontName, size=12, style="")
                        text += "     ~$" + str(sizes[0][1])
                        pdf.multi_cell(100, 7, txt=text, align="L")
                        yStart += 7
                        text = ""
                    if (len(toppings) > 1):
                        pdf.set_font(fontName, size=14, style="B")
                        text = "-Toppings/Customizations:"
                        pdf.multi_cell(100, 7, txt=text, align="L")
                        yStart += 7
                        text = ""
                        pdf.set_font(fontName, size=12, style="")
                        for ex in range(len(toppings)):
                            text += "     -"
                            text += toppings[ex][0]
                            text += " ~ $" + str(toppings[ex][1])
                            pdf.multi_cell(100, 7, txt=text, align="L")
                            yStart += 7
                            text = ""
                    yStart += 7
                    text = ""
    fileName = "static/menus/"+estNameStr + "-" +str([keys[menuNames]][0]) + "-" + "menu.pdf"
    print(fileName)
    pdf.output(fileName)
    print("\n")
