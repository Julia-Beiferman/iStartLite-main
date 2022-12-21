# File    : iStartLite.py 
# Author  : Julia Beiferman
# Version : 1.0  6/6/2022
'''
Description:
    Python Flask application to provide a GUI/webpage for the iStartLite. Have all packages installed in the same folder and follow configuration guide on the 'About' page.
    On the settings page configure makerAPI (from instructions) and devices should automatically show up. On the home page you should be able to select whatever machine
    you want and turn on and off the tester. 
    
    Whenever you hit save in the IP box or record a log by clicking the first link in history, a pickle file is stored in the /templates directory in order to save info such
    as the logs or ip address so they won't have to be configured again.

    Ennumeration: (see below for more functions)
    ability to ON/OFF/RESTART the tester with a link, set the delay, set the IP, and set a power cycle.
    ex.
    http://127.0.0.1:5000/set/4%20Relay%20iStart/ip=143.182.25.21/delayrestart=30/command=on
    http://127.0.0.1:5000//set/4%20Relay%20iStart/onInterval=4/offInterval=4/cycles=2
    
'''

import os
from datetime import datetime
from flask import Flask, render_template, request, render_template
from pyhubitat import MakerAPI
import time
import pickle
from concurrent.futures import ThreadPoolExecutor
import threading

testerStatus = {}
id = 0
global accessToken
global hubURL 
global devices
testers = []
logdir = "C:/Users/Public/Documents/iStartLogs"


#FIX THIS

'''
try:
    count = 0
    with open("/makerapiInfo/hubitatAccess.txt") as fp: #reads hubitat access token / url from a stored file so the user does not have to re-enter the values
        lines = fp.readlines()
        for line in lines:
            count+=1
            if count == 1:
                accessToken = line.strip()
            elif count == 2: 
                hubURL = line.strip()
    print(acessToken)
    print(hubURL)
except:

'''
accessToken = '05bd79b6-5309-455b-9b8c-8ae67212afea'
hubURL = 'http://192.168.0.113/apps/api/673'

class Tester():
    def __init__(self, id, label, name, testerIP, command, status):
        self.id = id
        self.label = label
        self.name = name
        self.IP = testerIP
        self.command = command
        self.status = status
        self.delay = 30 #time to delay the restart in seconds
        self.history = []
        self.logpages = {} #an array containing the history array(s), user makes a new logpage when they hit record
        self.logkeys = []

    def getKeys(self):
        self.logkeys = list(self.logpages.keys())

    def logHistory(self, command, time):
        testername = self.label
        user = os.getlogin()
        log = "User: " + user + " Tester: " + testername + " " + time +  " Command: " + command
        self.history.append(log)

    def recordLogPage(self, date, history):
        #delete log pages if there are more than 4 logs, keep the others in the folder though
        if len(self.logpages) > 3:
            extraPages = len(self.logpages) - 3 #minus one extra because loop starts at 0
            for i in range(extraPages):
                (k := next(iter(self.logpages)), self.logpages.pop(k)) #this deletes the leftmost (oldest) log
        
        logKey = self.label + "_" + date.replace(":", ",") #this is what they link will appear like
        self.logpages[logKey] = history #add the history to the dictionary value

def pickleTester(testerName):
    tester = getTester(testerName)
    path = tester.label.rstrip() #remove the trailing characters
    dir = os.path.join(logdir, path)
    print(dir)
    
    try:
        os.mkdir(dir)
    except FileExistsError:
        pass


    #add all of the logs to a folder
    tester.getKeys()
    for key in tester.logkeys:
        doc = key + ".txt"
        print(dir + "/" + doc)
        try:
            f = open(dir+"/"+doc, "x")
        except FileExistsError:
            f = open(dir+"/"+doc, "a") #append to the file if it exists

        for i in range (len(tester.logpages[key])):
            f.write(tester.logpages[key][i])
            f.write("\n")

    filename = dir + "/" + tester.label + ".pickle"

    with open(filename, 'wb') as handle:
        pickle.dump(tester, handle, pickle.HIGHEST_PROTOCOL)


def unpickleObjs(): #gets saved testers from the folder, so when the program is reloaded data about the testers is not lost, mostly just ip / log history
    rootdir = os.path.join(logdir, "/testers/")
    loads = []

    try:
        for subdir in os.listdir(rootdir):
            dir = rootdir + subdir + "/" + subdir + ".pickle"
            with open(dir, 'rb') as f:
                loadedTester = pickle.load(f)
                loads.append(loadedTester)
        return loads 
    except:

        return loads 
    
def reloadTesters(): #find ones that exist in local directory and replace them
    loads = unpickleObjs()
    for load in loads:
        for tester in testers:
            if load.label == tester.label:
                #replace the new with old data

                testers.remove(tester)
                load.id = tester.id #id controls whether or not we can send commmands 
                testers.append(load)


def createAPI(token, url):
    global testers

    try:
        ph = MakerAPI(token, url)
        devices = ph.list_devices() #returns dictionary of devices
        for device in devices:
            newDevice = Tester(device['id'], device['label'], device['name'], "", "OFF", "down")
            testers.append(newDevice)
        
        
        reloadTesters() #if the devices from makerAPI match what is stored locally, then used the old pickled classes to get data 
        return devices 

        #SPECIFY THE TYPE OF EXCEPTION HERE INSTEAD OF IT BEING AMBIGIOUS
    except: #catch connection time out errors when we can't connect to MakerAPI
        print("EXCEPTION")
        devices = None
        testers = []
        #newtester = Tester("3", "samplepickle", "samplepickle", "", "", "")
        #testers.append(newtester)
        return devices
        

app = Flask(__name__)


devices = createAPI(accessToken, hubURL)
devices = []


#FAKE TESTER FOR DEVELOPMENT PURPOSES
devTester = Tester("1", "dev", "dev", "127.7.00.1", "None", "UP")
devices.append(devTester)
testers = []
testers.append(devTester)
@app.route("/")
@app.route("/devices")
def welcome():

    if(devices == None):
        return render_template('dev.html', accessToken=accessToken, hubURL=hubURL)
    else:
        return render_template('dev.html',devices=testers, accessToken=accessToken, hubURL=hubURL)


def getTester(devLabel): #look up device id in list of Tester() class 
    newDevice = Tester("0", devLabel, devLabel, "", "", "")

    for tester in testers:
        if(tester.label == devLabel) :
            newDevice = tester
        else:
            continue
    
    return newDevice

def pingTester(ip, tester): #pings the tester and updates the status

    response = os.system("ping " + ip)
    
    if response == 0: #if we get a response
        tester.status = "up"
        return True     
    else:
        tester.status = "down"
        return False
    

 
@app.route('/data/<testerName>') #return tester status for jQuery
def data(testerName):

    tester = getTester(testerName)
    state = pingTester(tester.IP, tester)

    if(state):
        tester.status = "UP"
        return tester.status
    else:
        tester.status = "DOWN"
        return tester.status


#enummeration 
#ex. http://127.0.0.1:5000/set/4%20Relay%20iStart/ip=143.182.25.21/delayrestart=30/command=on
#http://127.0.0.1:5000//set/4%20Relay%20iStart/onInterval=4/offInterval=4/cycles=2
@app.route("/set/<testerName>/ip=<ipAddress>", defaults = {'command': None, 'restartInterval': None, 'cycles': None, 'onInterval': None, "offInterval": None})
@app.route("/set/<testerName>/command=<command>", defaults = {'ip': None, 'restartInterval': None, 'cycles': None, 'onInterval': None, "offInterval": None})
@app.route("/set/<testerName>/delayrestart=<restartInterval>/command=<command>", defaults = {'ipAddress': None, 'cycles': None, 'onInterval': None, "offInterval": None})
@app.route("/set/<testerName>/ip=<ipAddress>/delayrestart=<restartInterval>/command=<command>", defaults = {'cycles': None, 'onInterval': None, "offInterval": None})
@app.route("/set/<testerName>/ip=<ipAddress>/delayrestart=<restartInterval>/onInterval=<onInterval>/offInterval=<offInterval>/cycles=<cycles>",  defaults = {'command': None})
@app.route("/set/<testerName>/onInterval=<onInterval>/offInterval=<offInterval>/cycles=<cycles>",  defaults = {'command': None, 'ipAddress': None, 'restartInterval': None})
def configTester(testerName, ipAddress, restartInterval, command, onInterval, offInterval, cycles):
    tester = getTester(testerName)
    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")

    if ipAddress != None:
        tester.IP = ipAddress
    
    if restartInterval != None:
        tester.delay = int(restartInterval)

    try:
        ph = MakerAPI(accessToken, hubURL)

        if cycles != None: #power cycling
            cycles = int(cycles)
            onInterval = int(onInterval)
            offInterval = int(offInterval)
            for i in range (0, cycles):
                print(i)
                ph.send_command(tester.id, "on")
                time.sleep(onInterval) 
                print("JUST TURNED ON")
                ph.send_command(tester.id, "off")
                time.sleep(offInterval)
                print("JUST TURNED OFF")
            
            return f"{testerName} to run {cycles} cycles. On for {onInterval} seconds and off for {offInterval} seconds"

        else:
            if command == 'on':
                tester.command = "ON"
                ph.send_command(tester.id, "on") #turn on the device

            elif command == 'off':
                tester.command = "OFF"
                ph.send_command(tester.id, "off") #turn off the device

            elif command == 'restart': #restart the device
                tester.command = "RESTART"
                ph.send_command(tester.id, "off")
                time.sleep(tester.delay)
                ph.send_command(tester.id, "on")

            tester.logHistory(tester.command, dt_string) #log event into history
    except:
        pass
    
    ennumStr = f"Set {testerName}\n IP: {ipAddress} Restart Delay: {tester.delay} seconds\n Executing Command: {tester.command} \n Power cycling to run {cycles} cycles. On for {onInterval} seconds and off for {offInterval} seconds"
    return render_template('ennumpage.html', ennumStr = ennumStr) #maybe have this redirect to original tester page?


def restartDev(tester, ph, devID, devpage):

    print("STARTED TASK")
    print(threading.current_thread().name)
    #ph.send_command(devID, "off")  
    time.sleep(tester.delay) #delay between off and on not asynchronous
    #ph.send_command(devID, "on")

    print("RESTART IS DONE")
    tester.command = "NONE"
    #return tester
    return render_template('home.html', devpage=devpage, devID=devID, tester=tester)


def api_request(tester, ph, devID, command):
    tester.command = command

    ph.send_command(devID, command)
    print("API Request is over")
    tester.command = "NONE"

    return tester


@app.route("/devpage/<devpage>/<devID>/<command>", methods = ['GET', 'POST'])
@app.route("/devpage/<devpage>/<devID>", defaults = {'command': None}, methods = ['GET', 'POST'])
def user(devpage, devID, command):
    tester = getTester(devpage)
    now = datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    tester.getKeys()

    try:

        if request.method == 'POST':
            ph = MakerAPI(accessToken, hubURL)
            if request.form.get('onButton') == 'onButton': #action after each button is pushed
                
                with ThreadPoolExecutor(max_workers=5) as executor:
                    for result in executor.map(api_request(tester, ph, devID, "on"), [i for i in range(5)]):
                        tester = result
                tester.logHistory(tester.command, dt_string) #log event into history

                return render_template('home.html', devpage=devpage, devID=devID, tester=tester)

            elif request.form.get('offButton') == 'offButton':
                
                with ThreadPoolExecutor(max_workers=5) as executor:
                    for result in executor.map(api_request(tester, ph, devID, "off"), [i for i in range(5)]):
                        tester = result

                tester.logHistory(tester.command, dt_string) #log event into history

                return render_template('home.html', devpage=devpage, devID=devID, tester=tester)

            elif request.form.get('restartButton') == 'restartButton': #restart the device
                tester.command = "RESTART"
                tester.logHistory(tester.command, dt_string) #log event into history

                threading.Thread(target = restartDev, args=[tester]).start()
                #tester = threading.Thread(target = restartDev(tester))

                return render_template('home.html', devpage=devpage, devID=devID, tester=tester)

            elif request.form.get('setIP') == 'setIP': #save the IP address then ping to get a response
                tester.IP = request.form.get('testerIP')
                pickleTester(tester.label)
                pingTester(tester.IP, tester)

                print("out of the pinger----------------") 

                return render_template('home.html', devpage=devpage, devID=devID, tester=tester)

            elif request.form.get('restartDelay') == 'restartDelay':
                tester.delay = request.form.get('restartDelay')
            
                return render_template('home.html', devpage=devpage, devID=devID, tester=tester)
            else:
                return render_template('home.html', devpage=devpage, devID=devID, tester=tester)

            
    except:
        print("ERROR: Connection Timed Out. Hubitat not connected")  #time out error if program catches an exception
        return render_template('home.html', devpage=devpage, devID=devID, tester=tester)
        
    #tester.status = pingTester(tester.IP)
    return render_template('home.html', devpage=devpage, devID=devID, tester=tester)


@app.route("/about")
def about():
    workingdir = os.path.abspath(os.getcwd())
    filepath = workingdir + '/static/files/'
    return render_template('accessInfo.html')

@app.route("/settings", methods = ['GET', 'POST'])
def settings():
    global accessToken
    global hubURL
    global edit
    global devices
    global testers
    edit = False
    if request.method == 'POST':
        if request.form.get('action1') == 'save':
            edit = False
            accessToken = request.form.get('token')
            hubURL = request.form.get('apiURL')
            testers = []
            f = open("makerapiInfo/hubitatAccess.txt", "w") #if it's connected, write down the new values
            f.write(accessToken+"\n"+hubURL) 

            devices = createAPI(accessToken, hubURL) #this also resets all the ip addresses
            print("GET DEVICES")
            print(accessToken)
            print(hubURL)
            print(devices)
            if(devices == None): #if the hubitat is not connected, don't define device
                return render_template("settings.html", edit=edit,  apiURL=hubURL, token=accessToken, disconnected="true")
            else:
                return render_template("settings.html", edit=edit, apiURL=hubURL, token=accessToken, devices=devices, disconnected="false")
                
        if request.form.get('action2') == 'edit':
            edit = True            
            return render_template("settings.html", edit=edit,  apiURL=hubURL, token=accessToken)

    
    return render_template("settings.html", edit=edit,  apiURL=hubURL, token=accessToken)

@app.route("/api-info") #info page on how to get api link and token
def apiInfo():
    return render_template("apiInfo.html")

@app.route('/info/<testerName>') #pickle all of the info of the tester class and dump into a file
def info(testerName):
    tester = getTester(testerName)
    pickled_obj = pickle.dumps(tester)

    
    return f"{pickled_obj}\n"

@app.route("/logs/<device>", methods = ['GET', 'POST'], defaults = {"logkey" : None}) #log page organized by dates
@app.route("/logs/<device>/<logkey>", methods = ['GET', 'POST']) #log page organized by dates
def logs(device, logkey):
    tester = getTester(device)
    tester.getKeys()
    now = datetime.now()
    dt_string = now.strftime("%m-%d-%Y %H:%M")
    user = os.getlogin()

    if(logkey == None):
        history = tester.history

        tester.recordLogPage(dt_string, history)
        #tester.history = [] #clear history for new page
        pickleTester(tester.label) #save the tester info locally
        return render_template("logs.html", device=device, history=history, tester=tester)
    else:
        history = tester.logpages[logkey]
        return render_template("logs.html", device=device, history=history, tester=tester)



if __name__ == '__main__':
    app.run()
