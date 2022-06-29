#!/usr/bin/env python3
# coding: utf-8

# JS8Call WX Server
# Version 0.1.8.2 Alpha - Code modified by Joe, K0OG

# User Definition Area:

# To display imperial units, remove the hash mark (#) before the line with imperial text in it
#unit_type = 'metric'
unit_type = 'imperial'

# Set the API_key to a key registered under your name at openweathermap.org:
API_key = "Your_API_Key_Here"

# If no grid is specified or of the wrong format, then a default grid will be used.
# Set the default maidenhead gridsquare here:
default_grid = 'EN61EV'


# To enable email forwarding, uncomment ENABLE_EMAIL = True and add email account information below.
ENABLE_EMAIL = False
#ENABLE_EMAIL = True
# SMTP email server account information:
email_address = "Your_Email_Address"
email_server = 'Your_Email_Server_URL'
email_password = "Your_Email_Password"

# End User Definition Area
##################################

import sys
import time
import json
from js8net import *
import re
import requests
import maidenhead as mh
import os
import mimetypes
import smtplib
from email.message import EmailMessage

def email_push(request_callsign, recipient_email_address, body_text, SMTP_email_address, SMTP_email_server, SMTP_email_password):
    mail_server = smtplib.SMTP_SSL(SMTP_email_server)
    sender = SMTP_email_address
    recipient = recipient_email_address
    password = SMTP_email_password
    message = EmailMessage()
    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = 'Email forwarded from amateur radio operator ' + request_callsign
    footer = '\n\nEnd of message. \n\nThis email was received as a radio signal and may contain errors. Do not reply to this email. This email address is not monitored.'
    full_body_text = 'Forwarded message from ' + request_callsign + '\n\nBegin message:\n\n' + body_text + footer
    try:
# login and send email
        message.set_content(full_body_text)
        mail_server.login(sender, password)
        mail_server.send_message(message)
        mail_server.quit()
        print('Email sent.')
        send_inbox_message(request_callsign, 'Email sent to ' + recipient_email_address)
    except Exception as e:
        send_inbox_message(request_callsign, 'Sorry, email to' + recipient_email_address + ' did not go through.') 
        print(e)
        
def openweathermap_wind_api_call(forecast_day, user_API_key, display_unit_type, request_callsign, latitude, longitude):
    # Convert maidenhead grid to coordinates
#     coords = mh.to_location(forecast_gridsquare)
#     latitude = coords[0]
#     longitude = coords[1]

    try:
# Build url for openweathermap request
        base_url = "http://api.openweathermap.org/data/2.5/forecast?"
        Final_url = base_url + "appid=" + user_API_key + "&lat=" + str(latitude) + "&lon=" + str(longitude) + "&units=" + display_unit_type 
# Get openweathermap json with url
        forecast_json = requests.get(Final_url).json()
    except Exception as e:
        print(e)
# Select a forecast period in the desired forecast_day (8 forecast periods per day)
    forecast_period = int(forecast_day * 8)
# Make sure the forecast period is within the range of 0 to 39
    if(forecast_period > 39):
        forecast_period = 39
    if(forecast_period < 0):
        forecast_period = 0
# Pull date and time string out of json using forecast period
    dt_txt = forecast_json['list'][forecast_period]['dt_txt']
# Split out the date from the date - time string
    day_of_interest = dt_txt.split()[0]
# Set display units
    if (display_unit_type == 'imperial'):
        temp_unit = ' F'
        speed_unit = ' mph'
    if (display_unit_type == 'metric'):
        temp_unit = ' C'
        speed_unit = ' m/s'
# Print header
# Build WIND_FORECAST tx_string Header Needed City Name in WIND? output
    city_name = str(forecast_json['city']['name']) +'\n'
    tx_string = ('\nWIND FORECAST for ' + city_name +'\n')
# Go through data in forecast_json, and select data with requested day of interest
    for count in range(0, 40, 2):
        date_time = forecast_json['list'][count]['dt_txt']
        try:
# If the data is of the correct date, print it out, then continue loop through range
            if day_of_interest == date_time.split()[0]:
                tx_string += date_time[:-3] + '\n'
                tx_string += 'pressure ' + str(forecast_json['list'][count]['main']['pressure']) + ' mbar' + '\n'
                tx_string += 'wind ' + str(round(forecast_json['list'][count]['wind']['speed'])) + speed_unit + '\n'
                tx_string += 'gust ' + str(round(forecast_json['list'][count]['wind']['gust'])) + speed_unit + '\n'
                tx_string += 'deg ' + str(forecast_json['list'][count]['wind']['deg']) + ' deg' + '\n\r'
        except Exception as e:
            print(e)
    print(request_callsign + ' ' + tx_string)
    send_inbox_message(request_callsign, tx_string)

def openweathermap_wx_api_call(forecast_day, user_API_key, display_unit_type, request_callsign, latitude, longitude):
# Convert from requested day to number of 3 hour weather periods as provided in API
    forecast_period = int(forecast_day * 8)
    if(forecast_period > 39):
        forecast_period = 39
    if(forecast_period < 0):
        forecast_period = 0
# Convert maidenhead grid to latitude and longitude
#    try:
#        coords = mh.to_location(forecast_gridsquare)
#        latitude = coords[0]
#        longitude = coords[1]
#    except Exception as e:
#        print(e)
# Set up unit display type    
    if(display_unit_type == 'metric'):
        temp_unit = 'C'
        wind_unit = 'm/s'
    if(display_unit_type == 'imperial'):
        temp_unit = 'F'
        wind_unit = 'mph'
# Check for NOAA weather alerts
    try:
        NOAA_url = 'https://api.weather.gov/alerts/active?point=' + str(latitude) + ',' + str(longitude)
        NOAA_alert = requests.get(NOAA_url).json()
        alert_message = ''
        alert_message = NOAA_alert['features'][0]['properties']['event']
        alert_message = '\nALERT NOW: ' + alert_message
    except:
        pass
# Connect to Openweathermap.org API and get json dictionary
    base_url = "http://api.openweathermap.org/data/2.5/forecast?"
    Final_url = base_url + "appid=" + user_API_key + "&lat=" + str(latitude) + "&lon=" + str(longitude) + "&units=" + unit_type 
    try:
        forecast_json = requests.get(Final_url).json()
    except Exception as e:
        print(e)
# Build WX_FORECAST
    city_name = str(forecast_json['city']['name']) +'\n'
# Pull date and time string out of json
    dt_txt = forecast_json['list'][forecast_period]['dt_txt']
# Split date separate from date - time
    forecast_date = dt_txt.split()[0]
    display_date = forecast_date + '\n'
# If required, convert strings to ints
    try:
        maximum_temp_int = int(get_maximum_temp_from_day(forecast_date, forecast_json))
        minimum_temp_int = int(get_minimum_temp_from_day(forecast_date, forecast_json))
        maximum_wind_speed_int = int(get_maximum_wind_speed_from_day(forecast_date, forecast_json))
        maximum_gust_speed_int = int(get_maximum_gust_speed_from_day(forecast_date, forecast_json))
    except Exception as e:
        print(e)
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
    try:
        wx_forecast = alert_message + '\nFORECAST FOR ' + city_name + display_date + description + maximum_temp + minimum_temp + pressure + maximum_wind_speed + maximum_gust_speed + wind_deg  + '\r'
        print(request_callsign + ' ' + wx_forecast)
        send_inbox_message(request_callsign, wx_forecast)
    except Exception as e:
        print(e)

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

# Check for API key
if API_key == "Your_API_key_Here":
    print('Please enter your openweathermap.org API key in script in User Definition Area.')

########################
# Connect to JS8Call

js8host="localhost"
js8port=2442

print("Connecting to JS8Call...")
start_net(js8host,js8port)
print("Connected.")
get_band_activity()

#######################
# Print my call and server connection status 

my_call = get_callsign()
print(my_call + ' WX Server Active...')

# Text to trigger forecast transmission
wx_trigger = 'WX?'
wind_trigger = 'WIND?'
email_trigger = 'EMAIL?'
request_grid = ''
# Set initial values of latitude and longitude to default settings
coords = mh.to_location(default_grid)
latitude = str(coords[0])
longitude = str(coords[1])
# TEST
#wx_trigger = 'HEARTBEAT'
#wind_trigger = 'HEARTBEAT'
# END TEST

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
# Iterate through split text 
                item_count = len(split_message)
                for i in range(item_count):
                    print('** i = ', i, ' ', split_message[i])
# START WX SECTION
# Check for weather trigger
                    if split_message[i] == wx_trigger or split_message[i] == wind_trigger or split_message[i] == email_trigger:
# The following print can be removed - it is used as a debug test probe - K0OG
                        print('\n *** Input *** \n', split_message[1], split_message[2], split_message[3], split_message[4], split_message[5])
                        if re.search('[0-9]*[0-9]*\.[0-9]*[0-9]*', split_message[4]) and re.search('[0-9]*[0-9]*[0-9]*\.[0-9]*[0-9]*', split_message[5]):
# The following print can be removed - it is used as a debug test probe - K0OG
                            print('   ***   Lat/Lon Success   ***\n')
                            try:
                                latitude = split_message[4]
                                longitude = split_message[5]
                                request_day = split_message[6]
                            except Exception as e:
                                print(e)
                        else:
# The following print can be removed - it is used as a debug test probe - K0OG
                            print('\n *** Output ***\n', split_message[1], split_message[2], split_message[3], split_message[4], split_message[5])
                            try:
                                if re.search('[A-Za-z][A-Za-z][0-9][0-9]', split_message[4]):
                                    coords = mh.to_location(split_message[4])
                                    latitude = str(coords[0])
                                    longitude = str(coords[1])
                                    request_day = split_message[5]
# The following print can be removed - it is used as a debug test probe - K0OG
                                    print('   ***   Grid Success   ***')
                                else:
                                    coords = mh.to_location(default_grid)
                                    latitude = str(coords[0])
                                    longitude = str(coords[1])
                                    request_day = split_message[4]
                            except Exception as e:
                                print(e)
# Print current local time of directed message (now)
                        t = time.localtime()
                        current_time = time.strftime("%H:%M:%S", t)
                        print()
                        print(current_time)
# Remove colon from incoming request callsign
                        request_call = split_message[0].strip(':')
# Make sure request_day is between 0 and 5                        
                        try:
                            days = ['0', '1', '2', '3', '4', '5']
                            if request_day not in days:
                                request_day = 0
                            request_day = int(request_day)
                        except Exception as e:
                            print(e)
# Run wx function to print and send wx report
                        if split_message[i] == wx_trigger:
                            openweathermap_wx_api_call(request_day, API_key, unit_type, request_call, latitude, longitude)
# Run wind function to print and send wind report
                        if split_message[i] == wind_trigger:
                            openweathermap_wind_api_call(request_day, API_key, unit_type, request_call, latitude, longitude)
# Email function
                        if split_message[i] == email_trigger and ENABLE_EMAIL:
                            recipient_email = split_message[i+1]
                            message_body = directed_message_to_my_call
# TEST                            
                            print('Message body: ')
                            print(message_body)
                            print('End message body.')
# END TEST
                            email_push(request_call, recipient_email, message_body, email_address, email_server, email_password)
                        split_message[i] = ''
