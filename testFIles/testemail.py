import smtplib
sender = 'receipts@cedarrobots.com'
emailPass = "Cedar2421!"
FROM = sender


smtpObj = smtplib.SMTP_SSL("smtp.zoho.com",465)
smtpObj.login(sender,emailPass)
SUBJECT = "Test email"
TEXT = "Hello"
message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
receivers = 'cajohn0205@gmail.com'
smtpObj.sendmail(sender, receivers, message)
smtpObj.close()
print("Successfully sent email")