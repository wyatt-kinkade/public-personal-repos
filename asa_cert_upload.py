#!/usr/bin/python3
# Certs usually cost money, this is my cheap/lazy solution to not pay people for my VPN's certs

import requests
import json
import certbot.main
from pprint import pprint
from datetime import date
import ssl
import urllib3
import getpass
import random
import string
import os

#General Initial Variables
ssl._create_default_https_context = ssl._create_unverified_context
headers = {'Content-Type': 'application/json'}
urllib3.disable_warnings()
today_date = date.today()
certname = "asa-ssl-python-" + str(today_date)
available_chars = string.ascii_letters + string.digits
pfx_pass = ''.join((random.choice(available_chars) for i in range(10)))
cf_ini = "/home/janny/cloudflare_api_token.ini"
# Only thing I'd need would be the certdata for this from the ACME functionality, I would need the data converted to PFX format so it will need to have the pfx pass variable added when converting this
# certdata = 

#User Input, yes, getpass is better, having some minor issues though with it, I'll bother with that another point
ip = input("Please Enter the IP or FQDN of the host: \n")
username = input("Please Enter the Username: \n")
password = input("Please Enter the Password: \n")
extintf = input("Please Enter the name of the External Interface: \n")
email = input("Please Enter an email used for this certificate: \n")
domain = input("Please Enter the FQDN of the domain name of the outside IP for the ASA: \n")

#
def read_and_delete_file(path):
  with open(path, 'r') as file:
    contents = file.read()
  os.remove(path)
  return contents

def provision_cert(email, domain):
  certbot.main.main([
    'certonly',                             # Obtain a cert but don't install it
    '-n',                                   # Run in non-interactive mode
    '--agree-tos',                          # Agree to the terms of service,
    '--email', email,                       # Email
    '--dns-cloudflare',                     # Use dns challenge with Cloudflare
    '--dns-cloudflare-credentials', cf_ini,                     # Use dns challenge with Cloudflare
    '-d', domain,                          # Domain to provision certs for
    '--config-dir', '/tmp/config-dir/',       # Override directory paths so script doesn't have to be run as root
    '--work-dir', '/tmp/work-dir/',
    '--logs-dir', '/tmp/logs-dir/',
  ])
  #I'm leaving this commented out and directly calling openssl for now... I'll eventually start calling cryptography, I just want a handle on this for now...
  path = '/tmp/config-dir/live/' + domain + '/'
  pfx_path = path + 'cert.pfx'
  key_path = path + 'privkey.pem'
  cert_path = path + 'cert.pem'
  chain_path = path + 'chain.pem'
  #return {
  #  'private_key': read_and_delete_file(path + 'privkey.pem'),
  #  'certificate_with_chain': read_and_delete_file(path + 'fullchain.pem')
  #}
  os.system('openssl pkcs12 -export -out ' + pfx_path + ' -inkey ' + key_path + ' -in ' + cert_path + ' -certfile ' + chain_path + ' -password pass:' + pfx_pass)


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

# Provide Certificate to ASA
def upload_certificate (ip, Token, domain):
    urlpath = '/api/certificate/identity'
    path = '/tmp/config-dir/live/' + domain + '/'
    pfx_path = path + 'cert.pfx'
    os.system("echo -----BEGIN PKCS12----- > /tmp/" + domain + certname )
    os.system("openssl base64 -in " + pfx_path + " >> /tmp/" + domain + certname )
    os.system("echo -----END PKCS12----- >> /tmp/" + domain + certname )
    with open('/tmp/' + domain + certname) as file:
        cert_lines = file.readlines()
        cert_lines = [ line for line in cert_lines]
    #Making this bit quiet, but I'm keeping it around
    #print(cert_lines)
    post_data = {
      "certPass": pfx_pass, 
      "kind": "object#IdentityCertificate",
      "certText": cert_lines,
      "name": certname
    }
    #Making this bit quiet, but I'm keeping it around
    #print(post_data)
    url = 'https://' + ip + urlpath
    headers = Header
    data = requests.post(url, json.dumps(post_data), verify=False, headers = Header)
    #Making this bit quiet, but I'm keeping it around
    #parsed = json.loads(data.text)
    #value = json.dumps(parsed, indent=4, sort_keys=True)
    #print(parsed.get('response')[0])
    if os.path.exists('/tmp/' + domain + certname ):
      os.remove('/tmp/' + domain + certname )

# Runs Commands to apply certificate to Exterior Interface of Device for the web SSL
# If you need it to be applied for IKEv2 normally or for X-Auth/Site-to-Sites you need to independently add logic to do so
def apply_trustpoint (ip, Token):
    urlpath = '/api/cli'
    post_data = {
      "commands": [
        "ssl trust-point " + certname + ' ' + extintf ,
        "write memory"
      ]
    }
    url = 'https://' + ip + urlpath
    headers = Header
    data = requests.post(url, json.dumps(post_data), verify=False, headers = Header)
    parsed = json.loads(data.text)
    value = json.dumps(parsed, indent=4, sort_keys=True)
    print(parsed.get('response')[0])

#Done with Functions, time to have fun
provision_cert(email, domain)

#I will eventually bother with trying to take a stab at using cryptography for this...
#The below line is more of a note for me to remain aware of
#cryptography.hazmat.primitives.serialization.pkcs12.serialize_key_and_certificates(key, cert, cas, encryption_algorithm)


#Pulls token from ASA for Authentication
Token = get_token(ip, username, password)
Header = {
        'X-Auth-Token': Token,
        'Content-Type':"application/json"   }

#Queries Device after a 3 second interval, wanted to avoid any big risks instead of having it execute the function every 3 seconds

upload_certificate(ip, Token, domain)
apply_trustpoint(ip, Token)

#Deletes Token upon completion
del_token(ip, Token)
