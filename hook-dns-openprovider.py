#!/usr/bin/env python3

import sys
import requests
import json
import os

argc = len(sys.argv)

if ( argc != 5):
    print("Wrong number of arguments:",argc)
    sys.exit(1)

api = "https://api.openprovider.eu/v1beta"
acme = "_acme-challenge"
ttl = "600"
handler = sys.argv[1]
domain = sys.argv[2]
challenge = sys.argv[4]

# Try logging in to get a bearer-token
username = os.environ['OPENPROVIDER_API_USERNAME']
password = os.environ['OPENPROVIDER_API_PASSWORD']
sourceip = "0.0.0.0"
postdata = { "username": username, "password": password, "ip": sourceip  }
resp = requests.post(url=api + "/auth/login", data = json.dumps(postdata) )

if (resp.ok):
    data = json.loads(resp.text)
    bearer = data['data']['token']
else:
    print("Couldn't get a bearer-token, password incorrect?")
    sys.exit(20)

headers = { "Content-Type": "application/json", "Authorization": "Bearer " + bearer }

if ( handler == 'deploy_challenge'):
    add = [ { 'type': 'TXT', 'name': acme, 'value': challenge, 'ttl': ttl } ]
    postdata = {'name': domain, 'records': { 'add': add } }
elif ( handler == 'clean_challenge'):
    delchal= '"' + challenge + '"'  # I think the OpenProvider API is broken here...
    remove = [ { 'type': 'TXT', 'name': acme, 'value': delchal, 'ttl': ttl, 'creation_date': "", 'modification_date': ""} ]
    postdata = {'name': domain, 'records': { 'remove': remove } }
else:
    sys.exit(0)

resp = requests.put(url=api + "/dns/zones/" + domain, data=json.dumps(postdata), headers=headers )
print(resp.json())

sys.exit(resp.ok)
