#!/usr/bin/env python3

import slack
import os
import sys

SLACK_TOKEN='xoxb-11717412758-1553895325171-PmTI8rkR4KIrgAUZMKZ9fNJQ'

mystring = sys.stdin.read()
#mystring = 'gamer'

client = slack.WebClient(token=SLACK_TOKEN)

client.chat_postMessage(channel='#random', text= mystring)
