#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
import json
import os

argc = len(sys.argv)

if ( argc < 5):
    sys.exit(0)

api = "https://api.openprovider.eu/v1beta"
acme_str = "_acme-challenge"
acme = acme_str
ttl = "600"
handler = sys.argv[1]
hostdomain = sys.argv[2]

if ( handler == 'deploy_cert'):
    print( " * Deploy-cert\n")
    privkey_pem, cert_pem, fullchain_pem, chain_pem, timestamp = sys.argv[3:]
    filenames = [privkey_pem, fullchain_pem]
    with open('/var/lib/dehydrated/chains/' + str.replace(hostdomain, '*', 'wildcard') + '.pem', 'w') as outfile:
      for fname in filenames:
        with open(fname) as infile:
          outfile.write(infile.read())
    sys.exit(0)

challenge = sys.argv[4]

# Try logging in to get a bearer-token
try:
    bearer = os.environ['OPENPROVIDER_API_TOKEN']
except:
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


# Rest only deals with deploy or clean_challenge
if ( handler != 'deploy_challenge') and ( handler != 'clean_challenge'):
    sys.exit(0)

# If we are dealing with a wildcard, remove this section
wildcard = False
if ( hostdomain.split(".",1)[0] == "*" ):
    wildcard = True
    hostdomain = "".join(hostdomain.split(".",1)[1:])

try:
    # Find split between host and zone part
    domain = hostdomain
    record = ""
    dots = 0;
    resp = requests.get(url=api + "/dns/zones/" + domain, headers=headers )
    while not resp:
        print( "Domain " + domain + " not found, splitting further\n" )
        dots += 1
        domain = hostdomain.split(".", dots)[dots]
        record = ".".join(hostdomain.split(".")[0:dots])
        resp = requests.get(url=api + "/dns/zones/" + domain, headers=headers )
    print( "Domain " + domain + " found in your DNS zones. So record is " + record + "\n" )
    if ( dots >= 1):
        acme = acme_str + "." + ".".join(hostdomain.split(".", dots)[0:dots])
    else:
        acme = acme_str 
except:
    print( "Couldn't find your zone\n" )
    sys.exit(21)
    
if ( handler == 'deploy_challenge'):
    add = [ { 'type': 'TXT', 'name': acme, 'value': challenge, 'ttl': ttl } ]
    postdata = {'name': domain, 'records': { 'add': add } }
elif ( handler == 'clean_challenge'):
    delchal= '"' + challenge + '"'  # I think the OpenProvider API is broken here...
    remove = [ { 'type': 'TXT', 'name': acme, 'value': delchal, 'ttl': ttl, 'creation_date': "", 'modification_date': ""} ]
    postdata = {'name': domain, 'records': { 'remove': remove } }
else:
    sys.exit(0)

print( "Updating zone with domain " + domain + ", acme: " + acme + ", challenge: " + challenge + "\n")
resp = requests.put(url=api + "/dns/zones/" + domain, data=json.dumps(postdata), headers=headers )
print(resp.json())
responsedata = json.loads(resp.text)

if (resp.ok == True):
    sys.exit(0)
elif ( responsedata['desc'] == "Duplicate record" ):
    sys.exit(0)
else:
    sys.exit(1)
