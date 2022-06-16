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


print '\n 2. res.partner - Read all (with filters, offset, limit, order):'
r = requests.get(
    'http://localhost:8069/api/res.partner',
    headers = {
        'Content-Type': 'text/html; charset=utf-8',
        'Access-Token': access_token
    },
    data = json.dumps({
        'filters':  [('name', 'like', 'ompany'), ('id', '<=', 50)],
        #'filters':  [('name', 'like', 'ser'), ('id', '<=', 50),],
        #'filters':  [('id', '<=', 20)],
        #'offset':   10,
        'limit':    5,
        'order':    'name desc'  # default 'name asc'
    }),
    #verify = False      # for TLS/SSL connection
)
print r.text
