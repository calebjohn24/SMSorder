from escpos.printer import Usb
authentication = firebase.FirebaseAuthentication('if7swrlQM4k9cBvm0dmWqO3QsI5zjbcdbstSgq1W', 'cajohn0205@gmail.com',extra={'id': "d1ab1a95-ddb5-4ee4-83db-9179d37f8e78"})
database = firebase.FirebaseApplication("https://cedarchatbot.firebaseio.com/", authentication=authentication)


#0483:070b
Epson = Usb(0x0483, 0x070b, timeout=0, in_ep=0x82, out_ep=0x02)
Epson.set(align='center', width=3, height=3)
Epson.text('Jubby\n')
Epson.cut()
