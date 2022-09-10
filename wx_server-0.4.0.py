#!/usr/bin/env python3
# coding: utf-8

# JS8Call WX Server
#######################
# User Definition Area:

# To display imperial units, remove the hash mark (#) before the line with imperial text in it
unit_type = 'metric'
#unit_type = 'imperial'

# Set the API_key to a key registered under your name at openweathermap.org:
API_key = 'Your_API_key_Here'

# If no grid is specified or of the wrong format, then a default grid will be used.
# Set the default maidenhead gridsquare here:
default_grid = 'EN61EV'

# To enable email forwarding, uncomment ENABLE_EMAIL = True and add email account information below.
ENABLE_EMAIL = False
#ENABLE_EMAIL = True
MSG_EMAIL_NOTIFICATION = False
#MSG_EMAIL_NOTIFICATION = True
# SMTP email server account information:
email_address = 'Your_email_address'
email_server = 'Your_SMTP_email_server'
email_password = 'Your_SMTP_email_server_password'
message_email_address = 'email_address_to_receive_messages'
# Message beacon settings
ENABLE_MESSAGE_BEACON_1 = False # Enable by replacing False with True
message_period_1 = 121 # Number of minutes between transmissions
message_file_path_1 = 'qso_party.txt' # Path and file name of message
ENABLE_MESSAGE_BEACON_2 = False # Enable by replacing False with True
message_period_2 = 165 # Number of minutes between transmissions
message_file_path_2 = 'help_test.txt' # Path and file name of message
ENABLE_MESSAGE_BEACON_3 = False # Enable by replacing False with True
message_period_3 = 159 # Number of minutes between transmissions
message_file_path_3 = 'wxsnr.txt' # Path and file name of message#
ENABLE_MESSAGE_BEACON_4 = False # Enable by replacing False with True
message_period_4 = 60 # Number of minutes between transmissions
message_file_path_4 = 'heartbeat.txt' # Path and file name of message
ENABLE_MESSAGE_BEACON_5 = False # Enable by replacing False with True
message_period_5 = 243 # Number of minutes between transmissions
message_file_path_5 = 'emcomm_services.txt' # Path and file name of message
# Mouse click simulator
ENABLE_MOUSE_CLICK_SIMULATOR = False # Enable by replacing False with True
mouse_click_period = 240 # Number of minutes between mouse clicks

# End User Definition Area
##################################

import time
import json
from js8net import *
import re
import requests
import maidenhead as mh
#import os
#import mimetypes
import smtplib
from email.message import EmailMessage
import threading
from pynput import mouse
import pyautogui as pg

def on_click(x, y, button, pressed):
    global xvar
    global yvar
    if button == mouse.Button.left:
        xvar = x
        yvar = y
        return False

def message_beacon(path_to_file):
    message_file = open(path_to_file)
    message_content = message_file.read()
    send_message(message_content)
    message_file.close()
        
def msg_email_notification(sender_callsign, operator_callsign, operator_email_address, body_text, SMTP_email_address, SMTP_email_server, SMTP_email_password):
    mail_server = smtplib.SMTP_SSL(SMTP_email_server)
    sender = SMTP_email_address
    recipient = operator_email_address
    password = SMTP_email_password
    message = EmailMessage()
    message['From'] = sender
    message['To'] = recipient
    message['Subject'] = 'JS8Call message from ' + sender_callsign + ' to ' + operator_callsign
    footer = '\n\nEnd of message.'
    full_body_text = 'JS8Call message from ' + sender_callsign + '\n\nBegin message:\n\n' + body_text + footer
    try:
# login and send email
        message.set_content(full_body_text)
        mail_server.login(sender, password)
        mail_server.send_message(message)
        mail_server.quit()
        print('Message sent to station operator at ' + operator_email_address + ' by email.')
        transcript_file = 'transcript.txt'
        with open(transcript_file, 'a') as file:
            file.write('\n' + sender_callsign + ': ' + operator_callsign  + ' Message sent to station operator ' + operator_email_address + ' by email.')
    except Exception as e:
        print('Error: ')
        print(e)
        print('\nSorry, message forwarded by email did not go through.')
        transcript_file = 'transcript.txt'
        with open(transcript_file, 'a') as file:
            file.write('\n' + sender_callsign + ': ' + operator_callsign + '\nSorry, message forwarded by email did not go through.')
 
def email_push(request_callsign, sender_callsign, recipient_email_address, body_text, SMTP_email_address, SMTP_email_server, SMTP_email_password):
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
        print('Email sent to ' + recipient_email_address + '.')
        send_inbox_message(request_callsign, 'Email sent to ' + recipient_email_address)
        transcript_file = 'transcript.txt'
        with open(transcript_file, 'a') as file:
            file.write('\n' + sender_callsign + ': ' + request_callsign  + ' MSG Email sent to ' + recipient)
    except Exception as e:
        send_inbox_message(request_callsign, 'Sorry, email to ' + recipient_email_address + ' did not go through.') 
        print('Error: ')
        print(e)
        print('\nSorry, email to ' + recipient_email_address + ' did not go through.')
        transcript_file = 'transcript.txt'
        with open(transcript_file, 'a') as file:
            file.write('\n' + sender_callsign + ': ' + request_callsign + ' MSG Sorry, email to ' + recipient + ' did not go through.')
        
def openweathermap_wind_api_call(forecast_day, user_API_key, display_unit_type, sender_callsign, request_callsign, latitude, longitude, coordinate_check):
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
    city_name = str(forecast_json['city']['name'])
    if coordinate_check:
        city_name = str(forecast_json['city']['name']) +'\n' + str(latitude) + ', ' + str(longitude)
    tx_string = ('Wind Forecast for ' + city_name + '\n\n')
# Go through data in forecast_json, and select data with requested day of interest
    for count in range(0, 40, 2):
        date_time = forecast_json['list'][count]['dt_txt']
        try:
# If the data is of the correct date, print it out, then continue loop through range
            if day_of_interest == date_time.split()[0]:
                tx_string += date_time[:-3] + '\n'
                tx_string += 'press ' + str(forecast_json['list'][count]['main']['pressure']) + ' mbar' + '\n'
                tx_string += 'wind ' + str(round(forecast_json['list'][count]['wind']['speed'])) + speed_unit + '\n'
                tx_string += 'gust ' + str(round(forecast_json['list'][count]['wind']['gust'])) + speed_unit + '\n'
                tx_string += 'dir ' + str(forecast_json['list'][count]['wind']['deg']) + ' deg' + '\n\n'
        except Exception as e:
            print(e)
    print(sender_callsign + ': ' + request_callsign + ' MSG' + '\n' + tx_string)
    send_inbox_message(request_callsign, tx_string)
    transcript_file = 'transcript.txt'
    with open(transcript_file, 'a') as file:
        file.write('\n' + my_call + ': ' + request_callsign + ' MSG ' +'\n' + tx_string + '\n')

def openweathermap_wx_api_call(forecast_day, user_API_key, display_unit_type, sender_callsign, request_callsign, latitude, longitude, coordinate_check):
# Convert from requested day to number of 3 hour weather periods as provided in API
    forecast_period = int(forecast_day * 8)
    if(forecast_period > 39):
        forecast_period = 39
    if(forecast_period < 0):
        forecast_period = 0
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
    city_name = str(forecast_json['city']['name'])
    if coordinate_check:
        city_name = str(forecast_json['city']['name']) +'\n' + str(latitude) + ', ' + str(longitude)
# Pull date and time string out of json
    dt_txt = forecast_json['list'][forecast_period]['dt_txt']
# Split date separate from date - time
    forecast_date = dt_txt.split()[0]
    display_date = forecast_date
# If required, convert strings to ints
    try:
        maximum_temp_int = int(get_maximum_temp_from_day(forecast_date, forecast_json))
        minimum_temp_int = int(get_minimum_temp_from_day(forecast_date, forecast_json))
        maximum_wind_speed_int = int(get_maximum_wind_speed_from_day(forecast_date, forecast_json))
        maximum_gust_speed_int = int(get_maximum_gust_speed_from_day(forecast_date, forecast_json))
    except Exception as e:
        print(e)
# Short description of weather
    description = forecast_json['list'][forecast_period]['weather'][0]['description']
# Calculate the maximum temperature of the day
    maximum_temp =  'max ' + str(maximum_temp_int)  + ' ' + temp_unit 
# Calculate the minimum temperature in the day
    minimum_temp =  'min ' + str(minimum_temp_int)  + ' ' + temp_unit 
# Barometric Pressure
    pressure = 'press ' + str(forecast_json['list'][forecast_period]['main']['pressure']) + ' hPa'
# Calculate maximum wind speed of the day
    maximum_wind_speed = 'wind ' + str(maximum_wind_speed_int) + ' ' + wind_unit
# Calculate maximum gust of day
    maximum_gust_speed = 'gust ' + str(maximum_gust_speed_int) + ' ' + wind_unit
# Wind direction at time of forecast from compass reading
    wind_deg = 'wind dir ' + str(forecast_json['list'][forecast_period]['wind']['deg']) + ' deg'
# Output to send for transmission
    try:
        wx_forecast = alert_message + '\nForecast for ' + city_name + '\n' + display_date +'\n' + description +'\n' + maximum_temp +'\n' + minimum_temp +'\n' + pressure +'\n' + maximum_wind_speed +'\n' + maximum_gust_speed +'\n' + wind_deg  + '\n'
        print(sender_callsign + ': ' + request_callsign + ' MSG' + wx_forecast)
        send_inbox_message(request_callsign, wx_forecast)
        transcript_file = 'transcript.txt'
        with open(transcript_file, 'a') as file:
            file.write('\n' + my_call + ': ' + request_callsign + ' MSG' + wx_forecast + '\n')
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

def print_time():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print()
    print(current_time)

def return_time():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return(current_time)

def return_date_and_time():
    t = time.localtime()
    current_date_and_time = time.strftime("%n%Y %b %d %H:%M:%S %t%n", t)
    return(current_date_and_time)

# Check for API key
if API_key == 'Your_API_key_Here':
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
help_trigger = 'HELP?'
message_trigger = 'MSG'
# Initialize values and paths
request_grid = ''
transcript_file = 'transcript.txt'
# Set initial values of latitude and longitude to default settings
coords = mh.to_location(default_grid)
latitude = str(coords[0])
longitude = str(coords[1])

# Message Beacon Timers
previous_message_time_1 = time.time() 
previous_message_time_2 = time.time() 
previous_message_time_3 = time.time() 
previous_message_time_4 = time.time() 
previous_message_time_5 = time.time() 

# Mouse Click Simulator
xvar = 1
yvar = 1
previous_mouse_click_time = time.time()

if ENABLE_MOUSE_CLICK_SIMULATOR:
# Display alert screen
    pg.alert('Mouse Click Simulator: Click OK, then click the desired mouse click location on the screen.')
# Start listener for mouse clicks
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()
    
##################
# BEGIN RUNTIME SECTION
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
# Remove colon from incoming request callsign
                request_call = split_message[0].strip(':')
# print incoming directed message time and text
                print_time()
                print(directed_message_to_my_call)
# Initialize coordinate_format as not a decimal lat, lon
                coordinate_format = False
# Iterate through split text 
#                item_count = len(split_message)
#                for i in range(item_count):
                for i in range(1,4):
# START TRIGGERED RESPONSE SECTION
# Check for trigger keywords
                    if split_message[i] == wx_trigger or split_message[i] == wind_trigger or split_message[i] == email_trigger or split_message[i] == help_trigger or split_message[i] == message_trigger:
# Run message function
                        if split_message[i] == message_trigger and MSG_EMAIL_NOTIFICATION:
                            try:
                                message_body = directed_message_to_my_call
                                with open(transcript_file, 'a') as file:
                                    file.write('\n')
                                    file.write(return_date_and_time())
                                    file.write(directed_message_to_my_call)
                                msg_email_notification(request_call, my_call, message_email_address, message_body, email_address, email_server, email_password)
                            except Exception as e:
                                print(e)
                            
# Run email function
                        if split_message[i] == email_trigger and ENABLE_EMAIL:
                            try:
                                recipient_email = split_message[i+1]
                                message_body = directed_message_to_my_call
                                with open(transcript_file, 'a') as file:
                                    file.write('\n')
                                    file.write(return_date_and_time())
                                    file.write(directed_message_to_my_call)
                                email_push(request_call, my_call, recipient_email, message_body, email_address, email_server, email_password)
                            except Exception as e:
                                print(e)
# Help file server
                        if split_message[i] == help_trigger:
                            try:
                                file_path = 'help.txt'
                                print('Help file sent to: ' + request_call)
                                with open(file_path) as f:
                                    help_txt = f.read()
                                    send_inbox_message(request_call, help_txt)
                                with open(transcript_file, 'a') as file:
                                    file.write('\n' + return_date_and_time())
                                    file.write(directed_message_to_my_call + '\n')
                                    file.write('Help file sent to ' + request_call)
                            except Exception as e:
                                print(e)
# Check for decimal lat and lon format
                        split_message[4] = split_message[4].strip(',')
                        if re.search('[0-9]*\.[0-9]*', split_message[4]) and re.search('[0-9]*\.[0-9]*', split_message[5]) and -90 < float(split_message[4]) < 90 and -180 < float(split_message[5]) < 180:
                            try:
                                latitude = split_message[4]
                                longitude = split_message[5]
                                request_day = split_message[6]
# Toggle coordinate_format to indicate decimal lat, lon status
                                coordinate_format = True
                            except Exception as e:
                                print(e)
                        else:
# Check for maidenhead grid format
                            try:
                                if re.search('[A-Ra-r][A-Ra-r][0-9][0-9]', split_message[4]):
                                    coords = mh.to_location(split_message[4])
                                    latitude = str(coords[0])
                                    longitude = str(coords[1])
                                    request_day = split_message[5]
                                else:
# if not, set lat and lon to default grid location
                                    coords = mh.to_location(default_grid)
                                    latitude = str(coords[0])
                                    longitude = str(coords[1])
                                    request_day = split_message[4]
                            except Exception as e:
                                print(e)
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
                            try:
                                with open(transcript_file, 'a') as file:
                                    file.write(return_date_and_time())
                                    file.write(directed_message_to_my_call)
                                openweathermap_wx_api_call(request_day, API_key, unit_type, my_call, request_call, latitude, longitude, coordinate_format)
                            except Exception as e:
                                print(e)
# Run wind function to print and send wind report
                        if split_message[i] == wind_trigger:
                            try:
                                with open(transcript_file, 'a') as file:
                                    file.write(return_date_and_time())
                                    file.write(directed_message_to_my_call)
                                openweathermap_wind_api_call(request_day, API_key, unit_type, my_call, request_call, latitude, longitude, coordinate_format)
                            except Exception as e:
                                print(e)
# Check message beacon time and send if over period
    if ENABLE_MESSAGE_BEACON_1:
        if time.time() > (message_period_1 * 60) + previous_message_time_1:
            print()
            print(return_time())
            print('Sending Message 1', message_file_path_1)
            previous_message_time_1 = time.time()
            message_beacon(message_file_path_1)
    if ENABLE_MESSAGE_BEACON_2:
        if time.time() > (message_period_2 * 60) + previous_message_time_2:
            print()
            print(return_time())
            print('Sending Message 2', message_file_path_2)
            previous_message_time_2 = time.time()
            message_beacon(message_file_path_2)
    if ENABLE_MESSAGE_BEACON_3:
        if time.time() > (message_period_3 * 60) + previous_message_time_3:
            print()
            print(return_time())
            print('Sending Message 3', message_file_path_3)
            previous_message_time_3 = time.time()
            message_beacon(message_file_path_3)
    if ENABLE_MESSAGE_BEACON_4:
        if time.time() > (message_period_4 * 60) + previous_message_time_4:
            print()
            print(return_time())
            print('Sending Message 4', message_file_path_4)
            previous_message_time_4 = time.time()
            message_beacon(message_file_path_4)
    if ENABLE_MESSAGE_BEACON_5:
        if time.time() > (message_period_5 * 60) + previous_message_time_5:
            print()
            print(return_time())
            print('Sending Message 5', message_file_path_5)
            previous_message_time_5 = time.time()
            message_beacon(message_file_path_5)
    if ENABLE_MOUSE_CLICK_SIMULATOR:
        if time.time() > (mouse_click_period * 60) + previous_mouse_click_time:
            pg.click(xvar, yvar)
            t = time.localtime()
            current_time = time.strftime("%c", t)
            print()
            print('Mouse click at:', current_time)
            print('Next mouse click in '+ str(mouse_click_period) + ' minute(s).')
            previous_mouse_click_time = time.time()
