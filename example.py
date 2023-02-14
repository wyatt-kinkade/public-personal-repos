#!/usr/bin/python3
#Modules
from pyzabbix.api import ZabbixAPI
from jinja2 import Environment, FileSystemLoader
from filters.ctime import ctime
import os
import pwd

#Global Variables
user = pwd.getpwuid(os.getuid()).pw_name
file_loader = FileSystemLoader('/home/' + user + '/bin/templates')
env = Environment(loader=file_loader)
env.filters['ctime'] = ctime
# Create ZabbixAPI class instance
zapi = ZabbixAPI(url='https://zabbix.hometest.local/', user='Admin', password='lmaogetfuckedifyouthinkthisislegit')


# Get all events hosts
result = zapi.do_request('problem.get',
                          {
                              'filter': {'recent': 'false'},
                              'output': 'extend'
                          })



print(result['result'])

#Pass Information to Jinja template to generate HTML file
def print_alias_file():
    template = env.get_template('zabbix.j2')
    output = template.render(result=result['result'])
    print(output)
    alias_file = open("/home/" + user + "/startpage/zabbix.html", "w")
    alias_file.write(output)
    alias_file.close()

print_alias_file()

# Logout from Zabbix
zapi.user.logout()

