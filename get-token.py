#!/usr/bin/env python3

import sys
import requests
import json
import os

api = "https://api.openprovider.eu/v1beta"

username = os.environ['OPENPROVIDER_API_USERNAME']
password = os.environ['OPENPROVIDER_API_PASSWORD']
sourceip = "0.0.0.0"
postdata = { "username": username, "password": password, "ip": sourceip  }

resp = requests.post(url=api + "/auth/login", data = json.dumps(postdata) )

if (resp.ok):
    data = json.loads(resp.text)
    bearertoken = data['data']['token']
    print(bearertoken)

sys.exit(resp.ok)
