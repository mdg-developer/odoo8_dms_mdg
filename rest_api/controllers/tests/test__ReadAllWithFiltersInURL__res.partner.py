import requests, json


print '\n 1. Login in Odoo and get access tokens:'
r = requests.post(
    'http://localhost:8069/api/auth/get_tokens',
    headers = {'Content-Type': 'text/html; charset=utf-8'},
    data = json.dumps({
        'db':       'testdb11',
        'username': 'admin',
        'password': 'admin',
    }),
    #verify = False      # for TLS/SSL connection
)
print r.text
access_token = r.json()['access_token']


print '\n 2. res.partner - Read all (with filters in URL):'
r = requests.get(
    "http://localhost:8069/api/res.partner?filters=[('name','like','ompany'),('id','!=',50)]",
    headers = {
        'Content-Type': 'text/html; charset=utf-8',
        'Access-Token': access_token
    },
    #verify = False      # for TLS/SSL connection
)
print r.text
