import subprocess
import sys
import os.path


#functions
#---------------------------------------------------------------------------
def listArgs():
    print("\nList of available arguments:\n [c] Start SMB using ethernet\n[wc] Start SMB using wifi\n [d] Stop SMB\n [s] Show status\n [r] Restart SMB server")

def down(SSID):
    subprocess.run('nmcli con down ' + SSID + " &> /dev/null",shell=True)
                                                                            #the output of both down and up are
def up(SSID):                                                               #silenced, for prettiness' sake
    subprocess.run('nmcli con up ' + SSID + " &> /dev/null",shell=True)

def active(service):
    return subprocess.check_output('systemctl -l status ' + service + ' --no-pager | grep -wq active && echo -n \"True\" || echo -n \"False\"',shell=True).decode('UTF-8') == 'True'

def isWifi():
    return subprocess.check_output("nmcli con show --active | tail -1 | awk '{print $3;}' | tr -d '\n'",shell=True).decode('UTF-8') == 'wifi'

def getSSID():
    return subprocess.check_output("nmcli con show --active | tail -1 | awk '{print $1;}' | tr -d '\n'",shell=True).decode('UTF-8')
#---------------------------------------------------------------------------

#checks if there were arguments passed
if(len(sys.argv) < 2):
    print("No arguments used")
    listArgs()
    exit(0)
elif(len(sys.argv) > 2):
    print("too many arguments")
    exit(0)

arg = sys.argv[1]

#initializing variables
SMB_SSID = ""
prevSSID = ""

#setting path for the config file
HOME = subprocess.check_output("echo -n $HOME",shell=True).decode('UTF=8')
filepath = HOME + "/.psmb.conf"

#checking if a config file exists and opening it accordingly
if(os.path.isfile(filepath)):
    config = open(filepath,"r+")
else:
    print("config file doesn't exist, creating...")
    config = open(filepath,"w+")

#reads the lines from the config file
lines = config.read().splitlines()

#print("config file: ")
#print(lines)

#check completion of config file and assign contents to variables
if(len(lines) < 2):
    if(len(lines) == 0): #there's no SMB_SSID set
        SMB_SSID = input("SSID of the router connected to the PS2: ")
        config.writelines([SMB_SSID,""])
    else:
        print("prevSSID missing from config file")
        SMB_SSID = lines[0]
    print("")
else:
    SMB_SSID = lines[0]
    prevSSID = lines[1]

config.close()


if(arg == "wc"): #start SMB with wifi

    #checks if the router connected to the PS2 is available before trying to connect
    if(SMB_SSID in subprocess.check_output("nmcli dev wifi list",shell=True).decode('UTF-8')):
        #saves the current SSID before changing the connection so it can be restored later
        prevSSID = getSSID()

        #disconnects from the internet and connects to the PS2's router
        down(prevSSID)
        up(SMB_SSID)
        print("")
        print("Previous SSID: " + prevSSID)
        currentSSID = getSSID()
        print("Now connected to " + currentSSID)

        #actually starts smb and nmb
        subprocess.run('sudo systemctl start smb nmb',shell=True)

        #checks if everything necessary is working
        if(active("smb") and active("nmb") and (SMB_SSID in currentSSID)):
            print("started w/ wifi")
        else:
            print("something went wrong")
    else:
        print("PS2's router not found")

elif(arg == "c"): #start SMB with ethernet
    prevSSID = getSSID()
    subprocess.run('nmcli radio wifi off',shell=True)
    subprocess.run('sudo systemctl start smb nmb',shell=True)
    print("started w/o wifi")

elif(arg == "d"): #stop SMB server
    #stops the smb and nmb services
    subprocess.run('sudo systemctl stop smb nmb',shell=True)
    if(not active("smb") and not active("nmb")):
        print("smb and nmb stopped\n")

    if(isWifi()):
        #downs current network
        currentSSID = getSSID()
        down(currentSSID)
        print("Disconnected from " + currentSSID + "\n")
    else:
        #turns wifi back on
        subprocess.run('nmcli radio wifi on',shell=True)

    #reconnect to prevSSID
    up(prevSSID)
    if(prevSSID in getSSID()):
        print("Reconnected to " + prevSSID)

elif(arg == "r"): #restart SMB server
    subprocess.run('sudo systemctl restart smb nmb',shell=True)
    print("restarted")

elif(arg == "s"): #show status
    currentSSID = getSSID()
    print("Current network: " + currentSSID)
    if(SMB_SSID in currentSSID):
        print("(in the PS2's Network)")
    else:
        print("(NOT in the PS2's Network)")

    print("")
    if(active("smb")):
        print("smb is active")
    else:
        print("smb is inactive")

    if(active("nmb")):
        print("nmb is active")
    else:
        print("nmb is inactive")

else:
    print(arg + " is not a valid command")
    listArgs()

#write changes to config file
config = open(HOME + "/.psmb.conf","w")
print(SMB_SSID + "\n" + prevSSID, file=config)
config.close()
