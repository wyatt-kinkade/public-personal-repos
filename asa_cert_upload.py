#!/usr/bin/python3
# Certs usually cost money, this is my cheap/lazy solution to not pay people for my ASA's certs

# Requirements
# I only had to install the following, but there might be more on your systems
# certbot >= 1.18.0
# certbot-dns-cloudflare >= 1.18.0
# cryptography >= 3.0.0

# openssl binary

# I'd found another solution using acme.sh which I did like too especially since it's already written in shell, I might post it later given that I edited my copy
# but this has the advantage of python being available on windows as well as openssl.
import requests
import json
import certbot.main
from datetime import date
from cryptography import x509
import ssl
import urllib3
import random
import string
import os
from pathlib import Path

#General Initial Variables
ssl._create_default_https_context = ssl._create_unverified_context
headers = {'Content-Type': 'application/json'}
urllib3.disable_warnings()
today_date = date.today()
certname = "asa-ssl-python-" + str(today_date)
available_chars = string.ascii_letters + string.digits
pfx_pass = ''.join((random.choice(available_chars) for i in range(10)))
home = str(Path.home())

#Obviously this needs to be changed and configured accordingly, if you use another DNS provider you will need to setup certbot accordingly and adjust the script accordingly
cf_ini = home + "/cloudflare_api_token.ini"

#User Input, yes, getpass is better for the password, but this is a demo more than anything else
#For production use these values should be hard coded and the script should be set to a cronjob
#ip = input("Please Enter the IP or FQDN of the host: \n")
#username = input("Please Enter the Username: \n")
#password = input("Please Enter the Password: \n")
#extintf = input("Please Enter the name of the External Interface: \n")
#email = input("Please Enter an email used for this certificate: \n")
#domain = input("Please Enter the FQDN of the domain name of the outside IP for the ASA: \n")

#Assigning more variables for use later
path = '/tmp/config-dir/live/' + domain + '/'
pfx_path = path + 'cert.pfx'
key_path = path + 'privkey.pem'
cert_path = path + 'cert.pem'
chain_path = path + 'chain.pem'

def compare_certs():
  with open(cert_path, "rb") as f:
      cert_raw = f.read()
      #print(cert_raw)
  cert_info = x509.load_pem_x509_certificate(cert_raw)
  expiry_date = cert_info.not_valid_after
  #print(expiry_date.date())
  #print(today_date)

  time_left = expiry_date.date() - today_date

  compare_certs.days_left = int(time_left.days)
  print('Certificate has ' + str(compare_certs.days_left) + ' days remaining')

def provision_cert(email, domain):
  certbot.main.main([
    'certonly',                             # Obtain a cert but don't install it
    '-n',                                   # Run in non-interactive mode
    '--agree-tos',                          # Agree to the terms of service,
    '--email', email,                       # Email
    '--dns-cloudflare',                     # Use dns challenge with Cloudflare if you use another DNS prodvider this needs to be changed and configured accordingly, if you use another DNS provider you will need to setup certbot accordingly and adjust the script accordingly
    '--dns-cloudflare-credentials', cf_ini,                     # Use dns challenge with Cloudflare
    '-d', domain,                          # Domain to provision certs for
    '--config-dir', '/tmp/config-dir/',       # Override directory paths so script doesn't have to be run as root
    '--work-dir', '/tmp/work-dir/',
    '--logs-dir', '/tmp/logs-dir/',
  ])
  #I'm leaving this commented out and directly calling openssl for now... I'll eventually start calling cryptography, I just want a handle on this for now...
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
#Checks if Path Exists
if not os.path.exists(cert_path):
    print('No Existing Certificate Found, Creating New Certificate...\n')
    #Creates Cert
    provision_cert(email, domain)

    #Pulls token from ASA for Authentication
    Token = get_token(ip, username, password)
    #Adds Token to Header
    Header = {
            'X-Auth-Token': Token,
            'Content-Type':"application/json"   }

    #Uploads Certificate
    upload_certificate(ip, Token, domain)
    #Applies Certificate to Interface
    apply_trustpoint(ip, Token)

    #Deletes Token upon completion
    del_token(ip, Token)
else:
    #check if cert can be renewed
    compare_certs()
    if compare_certs.days_left < 30:
        print('Certificate Requires Renewal, Beginning Renewal Process...\n')
        provision_cert(email, domain)

        #Pulls token from ASA for Authentication
        Token = get_token(ip, username, password)
        #Adds Token to Header
        Header = {
                'X-Auth-Token': Token,
                'Content-Type':"application/json"   }

        #Uploads Certificate
        upload_certificate(ip, Token, domain)
        #Applies Certificate to Interface
        apply_trustpoint(ip, Token)

        #Deletes Token upon completion
        del_token(ip, Token)
    else:
        print('Certificate cannot yet be updated, Ending script')
