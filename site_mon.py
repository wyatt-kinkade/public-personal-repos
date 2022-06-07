#!/usr/bin/python3
#Modules
import json
import requests
import urllib3
import os
import pwd

#Global Variables
site_list = ["https://youtube.com","https://nginx.org/"]

#Functions
def verify_internet_func():
    try:
        google_result = requests.get("https://google.com")
        github_result = requests.get("https://github.com")
    except requests.exceptions.ConnectionError as e:
        print("Cannot contact Google or GitHub, likely ongoing internet issues occurring")
        exit()

def verify_site_func(site):
    try:
        site_error = ""
        site_result = requests.get(site)
        print(site_result.status_code) #Testing function
    except requests.exceptions.SSLError as err1:
        site_error = "SSL Certificate Expired for " + site
    except requests.exceptions.ConnectionError as err2:
        site_error = "General Connection Error, likely ongoing internet issues at " + site + " occurring"
    if(site_error!=""):
      return site_error
    if(site_result.status_code!=200):
      return site + " Responded Abnormally to regular synthetic transaction monitoring Status Code is " +  str(site_result.status_code)

#Using Discord because it's low effort, again use whatever here, M365 API, SMTP, Slack, Teams, etc
def post_msg(msg):
    url = 'https://discord.com/api/webhooks/<token_info here>'
    post_data = {
      "content": "<userinfohere> " + msg,
      "attachments": []
    }
    data = requests.post(url, post_data)

#Overall Function
verify_internet_func()
#verify_site_func() #Testing Function
for i in site_list:
    info = verify_site_func(i)
    if(info):
      post_msg(info)
