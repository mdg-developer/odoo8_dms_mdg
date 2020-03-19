import requests
import json
import time
from requests.auth import AuthBase

headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
print "Hello"
user= 'mdgtest'
password= '5329303b-4839-4c72-a1d0-fc72776755ca'
url='https://mpg-ids.mytel.com.mm/auth/realms/eis/protocol/openid-connect/token'
payload = {'grant_type': 'client_credentials'}
response = requests.post(url,headers=headers,auth=(user, password), data=payload, verify=False)

print "hello step1"

if response.status_code == 200:
    print ("Success")
    content = json.loads(response.content)
    token = content['access_token'] 
    print "token>>>",token
    #header = {  'Content-Type': 'application/json;charset=UTF-8',
    #'Authorization': 'Bearer {}'.format(token),}
    header = {'Content-Type': 'application/json',
           'Authorization': 'Bearer {0}'.format(token)}
    print "header>>>",header
    sms_url = 'https://mytelapigw.mytel.com.mm/msg-service/v1.3/smsmt/sent'
    sms_payload = {
	"source":"MYTELFTTH",
	"dest":"+959697182277",
	"content":"Hnin fighting"
    }
    #time.sleep(1)
    print "response post"
    
    response = requests.post(sms_url,  json = sms_payload, headers = header,verify=False)
    print "response",response.text
    if response.status_code == 200:
        print" sms send completed "
    
    