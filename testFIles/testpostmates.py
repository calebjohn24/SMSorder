import requests
import datetime

now = datetime.datetime.utcnow() # <-- get time in UTC
d = now + datetime.timedelta(minutes = 10)
dt = d.isoformat("T") + "Z"
print(dt)
url = "https://api.postmates.com/v1/customers/cus_MMAQ2VmJNZAVOV/delivery_quotes"
addrP = "2421112, Sahalee Dr W, Sammamish, WA, 98074"
addrD = "1645, 140th Ave NE, Bellevue, WA, 98005"
payload = {"dropoff_address":addrP,
           "pickup_address":addrD}
headers = {
    'Content-Type': "application/x-www-form-urlencoded",
    'Authorization': "Basic ODcwZWFiYWUtN2JiMS00MzZjLWFmNGEtMzNmYTJmZTc2ODhlOg==",
    'User-Agent': "PostmanRuntime/7.16.3",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "55cc61b2-a3aa-42f1-81a9-62467b9199b1,a5cb9e3d-7d0c-4834-9cde-6220fb9962a7",
    'Host': "api.postmates.com",
    'Accept-Encoding': "gzip, deflate",
    'Content-Length': "145",
    'Cookie': "__cfduid=d3e5bcc883cf1529ae363dbc64fe257f61567815844",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }


response = requests.request("POST", url, data=payload, headers=headers)
rsp = (response.json())
print(rsp)
print(rsp)
url = "https://api.postmates.com/v1/customers/cus_MMAQ2VmJNZAVOV/deliveries"
payload = {
"dropoff_address":addrP,
"pickup_address":addrD,
"quote_id":str(rsp["id"]),
"manifest":"Cedar Order",
"dropoff_phone_number":"17203269719",
"pickup_phone_number":"14257890099",
    "dropoff_name":"Caleb John",
'pickup_name':"TestRaunt",
    "dropoff_ready_dt":dt
}
headers = {
    'Content-Type': "application/x-www-form-urlencoded",
    'Authorization': "Basic ODcwZWFiYWUtN2JiMS00MzZjLWFmNGEtMzNmYTJmZTc2ODhlOg==",
    'User-Agent': "PostmanRuntime/7.16.3",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "a8e2692f-f65e-4cfb-8658-25324016b7ca,b7421a2d-8b36-4c6e-acd2-ceb641458a58",
    'Host': "api.postmates.com",
    'Accept-Encoding': "gzip, deflate",
    'Content-Length': "517",
    'Cookie': "__cfduid=d3e5bcc883cf1529ae363dbc64fe257f61567815844",
    'Connection': "keep-alive",
    'cache-control': "no-cache",
    }

response = requests.request("POST", url, data=payload, headers=headers)

rsp = (response.json())
print(rsp["tracking_url"])
print(rsp)
