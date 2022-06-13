#!/usr/bin/env python3
# coding: utf-8

# JS8Call WX Server

# To display imperial units, remove the hash mark (#) before the line with imperial text in it
#unit_type = 'metric'
unit_type = 'imperial'

# Set the API_key to a key registered under your name at openweathermap.org:
API_key = "Your API key Here"

# End User Definition Area
##################################

import sys
import time
import json
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
    try:
        coords = mh.to_location(forecast_gridsquare)
        latitude = coords[0]
        longitude = coords[1]
    except Exception as e:
        print(e)
# Set up unit display type    
    if(display_unit_type == 'metric'):
        temp_unit = 'C'
        wind_unit = 'm/s'
    if(display_unit_type == 'imperial'):
        temp_unit = 'F'
        wind_unit = 'mph'
# Connect to Openweathermap.org API and get json dictionary
    base_url = "http://api.openweathermap.org/data/2.5/forecast?"
    Final_url = base_url + "appid=" + user_API_key + "&lat=" + str(latitude) + "&lon=" + str(longitude) + "&units=" + unit_type 
    try:
        forecast_json = requests.get(Final_url).json()
    except Exception as e:
        print(e)
# Build WX_FORECAST
    grid = forecast_gridsquare + '\n'
# Pull date and time string out of json
    dt_txt = forecast_json['list'][forecast_period]['dt_txt']
    forecast_date = dt_txt.split()[0]
    display_date = forecast_date + '\n'
# If required, convert strings to ints
#try
    maximum_temp_int = int(get_maximum_temp_from_day(forecast_date, forecast_json))
    minimum_temp_int = int(get_minimum_temp_from_day(forecast_date, forecast_json))
    maximum_wind_speed_int = int(get_maximum_wind_speed_from_day(forecast_date, forecast_json))
    maximum_gust_speed_int = int(get_maximum_gust_speed_from_day(forecast_date, forecast_json))
# except Exception as e:
# print(e)
# print('String to int error')
# Short description of weather
    description = forecast_json['list'][forecast_period]['weather'][0]['description'] + '\n'
# Calculate the maximum temperature of the day
    maximum_temp =  'max ' + str(maximum_temp_int)  + ' ' + temp_unit + '\n'
# Calculate the minimum temperature in the day
    minimum_temp =  'min ' + str(minimum_temp_int)  + ' ' + temp_unit + '\n'
# Barometric Pressure
    pressure = 'press ' + str(forecast_json['list'][forecast_period]['main']['pressure']) + ' hPa' + '\n'
# Calculate maximum wind speed of the day
    maximum_wind_speed = 'wind ' + str(maximum_wind_speed_int) + ' ' + wind_unit + '\n'
# Calculate maximum gust of day
    maximum_gust_speed = 'gust ' + str(maximum_gust_speed_int) + ' ' + wind_unit + '\n'
# Wind direction at time of forecast from compass reading
    wind_deg = 'wind deg ' + str(forecast_json['list'][forecast_period]['wind']['deg']) + ' deg'
# Output to send for transmission
    wx_forecast = 'WX FOR ' + grid + display_date + description + maximum_temp + minimum_temp + pressure + maximum_wind_speed + maximum_gust_speed + wind_deg  + '\r'
    return wx_forecast

def get_maximum_temp_from_day(day_of_interest, forecast_data):
# Written for openweathermap API data
    new_max_temp = 0
# Go through data with day of interest, and select the maximum temp
    for count in range(0, 40, 1):
        dt_txt_iteration = forecast_data['list'][count]['dt_txt']
        if day_of_interest == dt_txt_iteration.split()[0]:
            variable_value = int(forecast_data['list'][count]['main']['temp_max'])
            if variable_value > new_max_temp:
                new_max_temp = variable_value
    return new_max_temp
    
def get_minimum_temp_from_day(day_of_interest, forecast_data):
# Written for openweathermap API data
    new_min_temp = 1000
# Go through data with day of interest, and select the minimum temp
    for count in range(0, 40, 1):
        dt_txt_iteration = forecast_data['list'][count]['dt_txt']
        if day_of_interest == dt_txt_iteration.split()[0]:
            variable_value = int(forecast_data['list'][count]['main']['temp_min'])
            if variable_value < new_min_temp:
                new_min_temp = variable_value
    return new_min_temp

def get_maximum_wind_speed_from_day(day_of_interest, forecast_data):
# Written for openweathermap API data
    new_max_wind_speed = 0
# Go through data from day of interest, select the highest wind speed
    for count in range(0, 40, 1):
        dt_txt_iteration = forecast_data['list'][count]['dt_txt']
        if day_of_interest == dt_txt_iteration.split()[0]:
            variable_value = int(forecast_data['list'][count]['wind']['speed'])
            if variable_value > new_max_wind_speed:
                new_max_wind_speed = variable_value
    return new_max_wind_speed
   
def get_maximum_gust_speed_from_day(day_of_interest, forecast_data):
# Written for openweathermap API data
    new_max_gust_speed = 0
# Go through data from day of interest, select the highest wind gust
    for count in range(0, 40, 1):
        dt_txt_iteration = forecast_data['list'][count]['dt_txt']
        if day_of_interest == dt_txt_iteration.split()[0]:
            variable_value = int(forecast_data['list'][count]['wind']['gust'])
            if variable_value > new_max_gust_speed:
                new_max_gust_speed = variable_value
    return new_max_gust_speed

########################
# Connect to JS8Call

js8host="localhost"
js8port=2442

print("Connecting to JS8Call...")
start_net(js8host,js8port)
print("Connected.")
get_band_activity()

#######################
# Status report

my_call = get_callsign()
print(my_call + ' WX Server Active...')

# Text to trigger forecast transmission
# Testing
#wx_trigger = 'HEARTBEAT'
# End Test

wx_trigger = 'WX?'

#    wind_trigger = 'WIND?'

##################
# Check if anything is in receive queue, if so, get json data
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
                    print('index: ' + str(i) + ' ' + split_message[i])
#                    try:
                    if split_message[i] == wx_trigger:
                        request_call = split_message[0]
                        request_grid = split_message[i+1]
                        request_day = int(split_message[i+2])
# Print current local time of directed message (now)
                        t = time.localtime()
                        current_time = time.strftime("%H:%M:%S", t)
                        print()
                        print(current_time)
# Testing
#                        request_grid = 'EN63uj14'
#                        request_day = 4
# End Test
                        if (type(request_day) == int):
                            if not(request_day >= 0 and request_day < 6):
                                request_day = 0
                        else:
                            request_day = 0
                        wx_output = openweathermap_wx_api_call(request_grid, request_day, API_key, unit_type)
#                            print(wx_output)
                        tx_output = my_call + ' ' + request_call + ' ' + wx_output
                        print(tx_output)
                        send_message(tx_output)
#                    except Exception as e:
#                        print(e)
