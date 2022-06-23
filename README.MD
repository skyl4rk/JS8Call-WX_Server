JS8Call WX_Server 

JS8Call is a low power digital mode application which uses amateur radio to provide keyboard to keyboard communication. It can be used to exchange text messages and for real-time text chat. 

JS8Call WX_Server is a python script which connects to JS8Call and runs at the same time that JS8Call is running.  It allows an operator of a JS8Call station connected to the internet to provide a brief weather forecast for any maidenhead grid location to a an operator requesting a forecast.

The requesting operator sends a directed call to the weather forecast server:

?WX EN43 1

Where "?WX" is the text which triggers a response from the weather forecast server, "EN43" is a maidenhead grid square, which could be any grid square location, and "1" is the number of days in the future for the forecast, which may be a number between 0 and 5, as desired by the requesting operator.

Example weather forecast:

WX FOR EN61EV

2022-06-10 00:00:00

SCATTERED CLOUDS

TEMP 20 C

MAX 20 C

MIN 15 C

PRESS 1013 HPA

WIND SPEED 1.9 M/S

WIND GUST 4.9 M/S

WIND DEG 297 DEG 

This message would take 3 minutes 15 seconds to complete on JS8Call in normal speed mode.

The JS8Call WX_Server will also send a WIND? forecast in a similar manner:

WIND? "grid" "days in future (0-5)"

If configured, it will also allow sending an email out:

EMAIL? "email address" "message" 

The JS8Net library is courtesy of Jeff Francis, the project is at: https://github.com/jfrancis42/js8net

Weather forecaasts are provided by openweathermap.com, under the following licenses: https://creativecommons.org/licenses/by-sa/4.0/ and https://opendatacommons.org/licenses/odbl/

Use Case: Mariners sailing offshore have limited weather forecast options, and are very much in need of weather prediction on their route.  Close to shore, NOAA weather forecasts are available over VHF radio and cell phone data.  Once the mariner moves offshore beyond range of these services, detailed weather forecasts require a satellite transciever.  

If there were a number of amateur operators along the coast running the WX_Server on JS8Call, mariners would be able to request a local weather forecast for their location, as well as locations in the future as they travel.  The radio requirements for accessing this service are low, a qrp transciever, a modest computer such as a Raspberry Pi 4 and a dipole or whip antenna tuned to a ham band.  20 and 40 meter bands would be a good options, 20 m during the day, 40 m at other times.

My goal for this script is to add a detailed wind forecast showing wind speed, gust speed and wind direction every three hours for a 24 hour period, with the ability to request up to 5 days into the future. 

A companion to this script would be a script which converts latitude and longitude to a maidenhead grid identifier and then sends the wind or weather request over JS8Call.  This script would be used by the mariner to input his latitude and longitude and with a mouse click, request a forecast.

The JS8Call WX_Server could be a very valuable service provided by amateur radio operators to mariner amateur operators.

Use Case: Some mountain or remote areas have no cell phone data and poor VHF radio reception. People who live or travel in these off-grid areas may have limited access to weather forecasts.  Using the JS8Call WX_Server would allow amateur operators who are off-grid to have a local weather forecast using HF radio connections, which are more likely to be recieved from remote areas.

Use Case: In the case of an emergency where telecommunication systems are not functional, amateur operators outside the blackout area using the JS8Call WX_Server could provide amateur operators in the blackout area a source of weather information when other providers are no longer functioning.  The experience in Nashville when telecommunications went down is a good example of the type of event where a JS8Call WX_Server would be valuable. Amateur operators can provide a valuable emergency service using this application.


Installation

Assuming a working JS8Call application:

pip install maidenhead
pip install requests

Download JS8Net.py and wx_server.x.x.x.py

Extract into a folder

Edit wx_server.x.x.x.py

Select unit type by uncommenting the desired unit type.

Paste your API_key from openweathermap.org in API_key

Set the default grid, if desired 

Start JS8Call

Start wx_server.x.x.x.py in command line or IDE

If the trigger WX? is detected, it will get a weather forecast and send it to the requesting operator.

If you install a wx_server at your station, please consider adding @WX to your groups in JS8Call, File: Settings: Station: Callsign Groups.
