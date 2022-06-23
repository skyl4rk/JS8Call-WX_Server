import sys
import time
import json
from js8net import *
import re
import requests

js8host="localhost"
js8port=2442

print("Connecting to JS8Call...")
start_net(js8host,js8port)
print("Connected.")
get_band_activity()
my_call = get_callsign()
print(my_call + ' WX Station Active...')
print()

trigger = 'HELP?'

last=time.time()
while(True):
    time.sleep(0.1)
    if(not(rx_queue.empty())):
        with rx_lock:
            rx=rx_queue.get()
            f=open("rx.json","a")
            f.write(json.dumps(rx))
            f.write("\n")
            f.close()
# Check for a message directed to my callsign    
            if(rx['type']=="RX.DIRECTED" and my_call == rx['params']['TO']):
                directed_message_to_my_call = rx['params']['TEXT']
# Split the recieved directed message
                split_message = re.split('\s', directed_message_to_my_call)
# Search for trigger
                item_count = len(split_message)
                for i in range(item_count):
#                    print(split_message[i])
#                    try:
                    if split_message[i] == trigger:
                        request_call_raw = split_message[0]
                        request_call = request_call_raw.strip(':')
                        report_file = open('help.txt')
                        report_msg = report_file.read()
                        print(request_call + ' ' + report_msg)
                        send_inbox_message(request_call, report_msg)
                        report_file.close()
