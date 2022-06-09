JS8Call WX_Server 

JS8Call is a low power digital mode application which uses amateur radio to provide keyboard to keyboard communication. It can be used to exchange text messages and for real-time text chat. 

JS8Call WX_Server is a python script which connects to JS8Call and runs at the same time that JS8Call is running.  It allows an operator of a JS8Call station connected to the internet to provide a brief weather forecast for any maidenhead grid location to a an operator requesting a forecast.

The requesting operator sends a directed call to the weather forecast server:

?WX EN43 1

Where "?WX" is the text which triggers a response from the weather forecast server, "EN43" is a maidenhead grid square, which could be any grid square location, and "1" is the number of days in the future for the forecast, which may be a number between 0 and 5, as desired by the requesting operator.

Example weather forecast:

2022-06-10 00:00:00

EN61EV

SCATTERED CLOUDS

TEMP 20 C

MAX 20 C

MIN 15 C

PRESS 1013 HPA

WIND SPEED 1.9 M/S

WIND GUST 4.9 M/S

WIND DEG 297 DEG 

This message would take 3 minutes 15 seconds to complete on JS8Call in normal speed mode.

