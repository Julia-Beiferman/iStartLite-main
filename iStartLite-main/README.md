# iStart Lite

Python Flask application to provide a GUI/webpage for the iStartLite which is run from the iStartLite.py file. Go to http://127.0.0.1:5000 after running

Have all packages installed in the same folder and follow configuration guide on the 'About' page. On the settings page configure makerAPI (from instructions) and devices should automatically show up. On the home page you should be able to select whatever machine you want and turn on and off the tester. Code to upload to the Hubitat website is in the /HubitatCode/ directory

Whenever you hit save in the IP box or record a log by clicking the first link in history, a pickle file is stored in the /templates directory in order to save info such
as the logs or ip address so they won't have to be configured again.

Ennumeration: (see below for more functions)
ability to ON/OFF/RESTART the tester with a link, set the delay, set the IP, and set a power cycle.
ex.
http://127.0.0.1:5000/set/4%20Relay%20iStart/ip=143.182.25.21/delayrestart=30/command=on
http://127.0.0.1:5000//set/4%20Relay%20iStart/onInterval=4/offInterval=4/cycles=2
