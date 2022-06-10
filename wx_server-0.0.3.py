#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import time
import json
import argparse
from os.path import exists
from js8net import *
import re
import requests
import maidenhead as mh

def openweathermap_wx_api_call(forecast_gridsquare, forecast_day, user_API_key, display_unit_type):
# Convert from requested day to number of 3 hour weather periods as provided in API
    forecast_period = int(forecast_day * 8)
    if(forecast_period > 39):
        forecast_period = 39
    if(forecast_period < 0):
        forecast_period = 0
# Convert maidenhead grid to latitude and longitude
    coords = mh.to_location(forecast_gridsquare)
    latitude = coords[0]
    longitude = coords[1]
# Set up unit display type    
    if(display_unit_type == 'metric'):
        temp_unit = 'C'
        wind_unit = 'm/s'
    if(display_unit_type == 'imperial'):
        temp_unit = 'F'
        wind_unit = 'mph'
# API Connection to Openweathermap.org
    base_url = "http://api.openweathermap.org/data/2.5/forecast?"
    Final_url = base_url + "appid=" + user_API_key + "&lat=" + str(latitude) + "&lon=" + str(longitude) + "&units=" + unit_type 
    forecast_json = requests.get(Final_url).json()
# BUILD WX_FORECAST
    grid = forecast_gridsquare + '\n'
# Date and time
    dt_txt = forecast_json['list'][forecast_period]['dt_txt'] + '\n'
# Short description of weather
    description = forecast_json['list'][forecast_period]['weather'][0]['description'] + '\n'
# Temperature at time of forecast (see dt_text Date and Time)
    temp = 'temp ' + str(int(forecast_json['list'][forecast_period]['main']['temp'])) + ' ' + temp_unit + '\n'
# Calculate the maximum temperature in the next 24 hours
    max = str(forecast_json['list'][forecast_period]['main']['temp_max'])
    forecast_step = forecast_period
#    for forecast_step in range(forecast_step, 39, 7):
#        if  (int(forecast_json['list'][forecast_step]['main']['temp_max']) > max):
#            max = forecast_json['list'][forecast_step]['main']['temp_max']
#    max = 'max ' + str(int(max)) + ' ' + temp_unit + '\n'
# Calculate the minimum temperature in the next 24 hours
    min = str(forecast_json['list'][forecast_step]['main']['temp_min'])
    forecast_step = forecast_period
#    for forecast_step in range(forecast_step, 39, 7):
#        if  (int(forecast_json['list'][forecast_step]['main']['temp_min']) < min):
#            min = str(forecast_json['list'][forecast_step]['main']['temp_min'])
#    min =  'min ' + str(int(min)) + ' ' + temp_unit + '\n'
# Barometric Pressure
    pressure = 'press ' + str(forecast_json['list'][forecast_period]['main']['pressure']) + ' hPa' + '\n'
# Wind speed at time of forecast
    wind_speed = 'wind speed ' + str(round(forecast_json['list'][forecast_period]['wind']['speed'], 1)) + ' ' +  wind_unit + '\n'
# Maximum wind gust speed in next 24 hours
    gust = str(forecast_json['list'][forecast_step]['wind']['gust'])
    forecast_step = forecast_period
#    for forecast_step in range(forecast_step, 39, 7):
#        if  (int(forecast_json['list'][forecast_step]['wind']['gust']) > gust):  # modified
#            gust = forecast_json['list'][forecast_step]['wind']['gust']  
#    gust = 'wind gust ' + str(round(gust, 1)) + ' ' +  wind_unit + '\n'
# Wind direction at time of forecast from compass reading
    wind_deg = 'wind deg ' + str(forecast_json['list'][forecast_period]['wind']['deg']) + ' deg' + '\n'
# Output to send for transmission
# Currently this is in a format for printing to screen.  There may be a need to
# remove \n from the data lines to use for transmitting in digital modes.
    wx_forecast = 'WX FOR ' + grid + dt_txt + description + temp + max + min + pressure + wind_speed + gust + wind_deg  + '\n'  + '\r'
    return wx_forecast
########################

# Main program.
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description="Example of using js8net.py")
    parser.add_argument("--js8_host",default=False,help="IP/DNS of JS8Call server (default localhost, env: JS8HOST)")
    parser.add_argument("--js8_port",default=False,help="TCP port of JS8Call server (default 2442, env: JS8PORT)")
    parser.add_argument("--clean",default=False,action="store_true",help="Start with clean spots (ie, don't load spots.json)")
    parser.add_argument("--env",default=False,action="store_true",help="Use environment variables (cli options override)")
    parser.add_argument("--listen",default=False,action="store_true",help="Listen only - do not write files")
    parser.add_argument("--verbose",default=True,action="store_true",help="Lots of status messages")
    args=parser.parse_args()

    # Load spots.json for some historical context, unless the file is
    # missing, or the user asks not to.
    if(exists("spots.json") and not(args.clean)):   #
        with spots_lock:                            # 
            f=open("spots.json")                    #
            spots=json.load(f)                      #
            f.close()                               #

    js8host=False
    js8port=False

    # If the user specified a command-line flag, that takes
    # priority. If they also specified --env, any parameters they did
    # not specify explicit flags for, try to grab from the
    # environment.
    if(args.js8_host):
        js8host=args.js8_host
    elif(os.environ.get("JS8HOST") and args.env):
        js8host=os.environ.get("JS8HOST")
    else:
        js8host="localhost"

    if(args.js8_port):
        js8port=args.js8_port
    elif(os.environ.get("JS8PORT") and args.env):
        js8port=int(os.environ.get("JS8PORT"))
    else:
        js8port=2442

    if(args.verbose):
        print("Connecting to JS8Call...")
    start_net(js8host,js8port)
    if(args.verbose):
        print("Connected.")
    get_band_activity()


################

    # To display imperial units, remove the hash mark (#) before the line with imperial text in it
    unit_type = 'metric'
    unit_type = 'imperial'

    # Set the API_key to a key registered under your name at openweathermap.org:
    API_key = "Your API key here"

################

    my_call = get_callsign()
    print('my_call: ' + my_call)

    wx_trigger = 'WX?'
#    wind_trigger = 'WIND?'

##################

    last=time.time()
    while(True):
        time.sleep(0.1)
        if(not(rx_queue.empty())):
            with rx_lock:
                rx=rx_queue.get()
                if(not(args.listen)):
                    f=open("rx.json","a")
                    f.write(json.dumps(rx))
                    f.write("\n")
                    f.close()
                    if(time.time()>=last+300):       #
                        last=time.time()             #
                        f=open("spots.json","w")     #
                        f.write(json.dumps(spots))   #
                        f.write("\n")                #
                    f.close()                        #
                # Check for a message directed to my callsign    
                if(rx['type']=="RX.DIRECTED" and my_call == rx['params']['TO']):
                    directed_message_to_my_call = rx['params']['TEXT']
                    # Split the recieved directed message
                    split_message = re.split('\s', directed_message_to_my_call)
                    
                    t = time.localtime()
                    current_time = time.strftime("%H:%M:%S", t)
                    print(current_time)

                    # Search for trigger
                    item_count = len(split_message)
                    for i in range(item_count):
                        print(split_message[i])
#                        try:
                        if split_message[i] == wx_trigger:
                            print(wx_trigger + ' found using loop and range at index: ' + str(i))
                            request_call = split_message[i-2]
                            request_grid = split_message[i+1]
                            request_day = split_message[i+2]
                            wx_output = openweathermap_wx_api_call(request_grid, request_day, API_key, unit_type)
                            print(wx_output)
                            tx_output = request_call + ' '+ wx_output
                            print(tx_output)
                            send_message(tx_output)
#                        except Exception as e:
#                            print(e)
