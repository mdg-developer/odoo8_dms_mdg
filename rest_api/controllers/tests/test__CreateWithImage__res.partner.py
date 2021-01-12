#!/usr/bin/python2

import requests, json
import base64


print "\n 1. Login in Odoo and get access tokens:"
r = requests.post(
    'http://localhost:8069/api/auth/get_tokens',
    headers = {'Content-Type': 'text/html; charset=utf-8'},
    data = json.dumps({
        'db':       'testdb12',
        'username': 'admin',
        'password': 'admin',
    }),
    #verify = False      # for TLS/SSL connection
)
print r.text
access_token = r.json()['access_token']


print "\n 2. Open image file and encode it to 'base64' encoding:"
f = open('test_image_1.png', 'r')
raw_image_data = f.read()
f.close()
# print '\n raw_image_data ==', raw_image_data
encoded_image_data = base64.encodestring(raw_image_data)
print '\n encoded_image_data ==', encoded_image_data


print "\n 3. res.partner - Create one:"
r = requests.post(
    'http://localhost:8069/api/res.partner',
    headers = {
        'Content-Type': 'text/html; charset=utf-8',
        'Access-Token': access_token
    },
    data = json.dumps({
        'name':     'TEST Partner (with Image)',
        'image':    encoded_image_data,
    }),
    #verify = False      # for TLS/SSL connection
)
print r.text
