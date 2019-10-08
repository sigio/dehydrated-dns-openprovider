#!/usr/bin/env python3

import sys
import requests
import json

argc = len(sys.argv)

if ( argc != 5):
    print("Wrong number of arguments:",argc)
    sys.exit(1)

api = "https://api.openprovider.eu/v1beta"
bearer = "REPLACE_WITH_YOUR_TOKEN"
acme = "_acme-challenge"
ttl = "600"
handler = sys.argv[1]
domain = sys.argv[2]
challenge = sys.argv[4]
headers = { "Content-Type": "application/json", "Authorization": "Bearer " + bearer }

print( "Handler = '" + handler + "'")
print( "Domain = '" + domain + "'")
print( "Challenge = '" + challenge + "'")

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
