#!/usr/bin/python3
# Ended up listeninng to someone groan about a lack of a watch command on ASA OS, is this a watch command? nope, but still, beats having nothing, could argue that doing this via SSH would be better but response time for the web queries is far faster and is way more tolerable.

import time
import os
import requests
import json
from pprint import pprint
import ssl
import urllib3
import getpass

#General Initial Tuning
ssl._create_default_https_context = ssl._create_unverified_context
headers = {'Content-Type': 'application/json'}
urllib3.disable_warnings()

#User Input, yes, getpass is better, having some minor issues though with it, I'll bother with that another point
ip = input("Please Enter the IP or FQDN of the host: \n")
username = input("Please Enter the Username \n")
password = input("Please Enter the Password \n")
command = input("Please Enter the Command you want to watch \n")

post_data = {
  "commands": [
    command
  ]
}
#Clears Screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
#Generates Token
def get_token(ip, username, password):
    token = None
    #Directory of the ASA Tokenservice
    url = 'https://'+ username + ':' + password + '@' + ip + '/api/tokenservices'
    headers = {'Content-Type':"application/json"}
    payload = ""
    # Send POST Request to ASA, containing Username and Password in URL, empty payload, JSON Header. It doesn't verify SSL Cetificate!
    r = requests.request("POST", url, data=json.dumps(payload), headers=headers, verify=False)
    #Check if response got received, if not print an error message
    if(not r):
        print("No Data returned")
    #Search for the token in the header and stores the value.
    else:
        token = r.headers['x-auth-token']
    return token
    print('Token Generated!')
#Deletes Token
def del_token(ip, Token):
    url = 'https://' + ip + '/api/tokenservices/' + Token
    headers = Header
    r = requests.delete(url, headers = headers, verify = False)
    print('\nToken Deleted!')

# Runs Command
def data_request (ip, Token):
    urlpath = '/api/cli'
    url = 'https://' + ip + urlpath
    headers = Header
    data = requests.post(url, json.dumps(post_data), verify=False, headers = Header)
#    print(data)
    parsed = json.loads(data.text)
    value = json.dumps(parsed, indent=4, sort_keys=True)
    print(parsed.get('response')[0])

#Pulls token from ASA for Authentication
Token = get_token(ip, username, password)
Header = {
        'X-Auth-Token': Token,
        'Content-Type':"application/json"   }

#Queries Device after a 3 second interval, wanted to avoid any big risks instead of having it execute the function every 3 seconds
while True:
    try:
        clear_screen()
        data_request(ip, Token)
        time.sleep(3)
    except KeyboardInterrupt:
        clear_screen()
        break

#Deletes Token upon completion
del_token(ip, Token)

