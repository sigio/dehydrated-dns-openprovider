#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
import json
import os

# Configurable items

# Bearer-token is created with get-token... needs to be an account without 2FA AFAIK
bearer = os.environ['OPENPROVIDER_API_BEARER']
# Default TTL for records
ttl = "600"

argc = len(sys.argv)

# We only respond on deploy_challenge / cleanup_challenge calls
# These have 5 arguments

if ( argc < 5):
    sys.exit(0)

api = "https://api.openprovider.eu/v1beta"
headers = { "Content-Type": "application/json", "Authorization": "Bearer " + bearer }
acme = "_acme-challenge"
handler = sys.argv[1]
domain = sys.argv[2]
challenge = sys.argv[4]
subdomain = ""
superdomain = ""

if ( handler == 'deploy_cert'):
    print( " * Deploy-cert\n")
    privkey_pem, cert_pem, fullchain_pem, chain_pem, timestamp = sys.argv[3:]
    filenames = [privkey_pem, fullchain_pem]
    with open('/var/lib/dehydrated/chains/' + str.replace(domain, '*', 'wildcard') + '.pem', 'w') as outfile:
      for fname in filenames:
        with open(fname) as infile:
          outfile.write(infile.read())
    sys.exit(0)

# Rest only deals with deploy or clean_challenge
if ( handler != 'deploy_challenge') and ( handler != 'clean_challenge'):
    sys.exit(0)

# If we are dealing with a wildcard, remove this section
wildcard = False
if ( domain.split(".",1)[0] == "*" ):
    wildcard = True
    domain = "".join(domain.split(".",1)[1:])


# Find the base domain for the given domainname
try:
    data = requests.get(url=api + "/dns/zones/", headers=headers ).json()
    zonelist = list(r['name'] for r in data['data']['results'])

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

if ( handler == 'deploy_challenge'):
    add = [ { 'type': 'TXT', 'name': acme, 'value': challenge, 'ttl': ttl } ]
    postdata = {'name': superdomain, 'records': { 'add': add } }
elif ( handler == 'clean_challenge'):
    delchal= '"' + challenge + '"'  # I think the OpenProvider API is broken here...
    remove = [ { 'type': 'TXT', 'name': acme, 'value': delchal, 'ttl': ttl, 'creation_date': "", 'modification_date': ""} ]
    postdata = {'name': superdomain, 'records': { 'remove': remove } }
else:
    sys.exit(0)

print( "Updating zone with domain " + domain + ", acme: " + acme + ", challenge: " + challenge + "\n")
resp = requests.put(url=api + "/dns/zones/" + superdomain, data=json.dumps(postdata), headers=headers )
print(resp.json())
responsedata = json.loads(resp.text)

if (resp.ok == True):
    sys.exit(0)
elif ( responsedata['desc'] == "Duplicate record" ):
    sys.exit(0)
else:
    sys.exit(1)
