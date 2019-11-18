#!/usr/bin/env python3

import sys
import requests
import json

argc = len(sys.argv)

if ( argc != 5):
    print("Wrong number of arguments:",argc)
    sys.exit(0)


# Bearer-token is created with get-token... needs to be an account without 2FA AFAIK
api = "https://api.openprovider.eu/v1beta"
bearer = "XXXXXXXXXXXXXXXXXX"
acme = "_acme-challenge"
ttl = "600"
handler = sys.argv[1]
domain = sys.argv[2]
challenge = sys.argv[4]
subdomain = ""
superdomain = ""

# Find the base domain for the given domainname
try:
    zonelist = ['your-domain.tls', 'other-domain.tld', 'example.com']
    for zone in zonelist:
        if zone in domain:
            subdomain = domain.split(zone)[0][:-1]
            superdomain = zone
            print(subdomain, superdomain)
            if (subdomain != ""):
                acme = acme + "." + subdomain
except:
    # Domain not found in the list, assuming it's a normal domain without subdomains
    subdomain = ""
    superdomain = domain

headers = { "Content-Type": "application/json", "Authorization": "Bearer " + bearer }

if ( handler == 'deploy_challenge'):
    add = [ { 'type': 'TXT', 'name': acme, 'value': challenge, 'ttl': ttl } ]
    postdata = {'name': superdomain, 'records': { 'add': add } }
elif ( handler == 'clean_challenge'):
    delchal= '"' + challenge + '"'
    remove = [ { 'type': 'TXT', 'name': acme, 'value': delchal, 'ttl': ttl, 'creation_date': "", 'modification_date': ""} ]
    postdata = {'name': superdomain, 'records': { 'remove': remove } }
else:
    sys.exit(0)

resp = requests.put(url=api + "/dns/zones/" + superdomain, data=json.dumps(postdata), headers=headers )
print(resp.json())

sys.exit(0)

