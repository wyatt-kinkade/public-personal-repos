#Literally just built to pass Standard Input into Slack
#!/usr/bin/env python3

import slack
import os
import sys

SLACK_TOKEN=''

mystring = sys.stdin.read()
#mystring = 'test'

client = slack.WebClient(token=SLACK_TOKEN)

client.chat_postMessage(channel='#random', text= mystring)
