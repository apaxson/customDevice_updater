###############################################################
######## NOTES:                                        ########
########   @author: Aaron Paxson / Tony Huinker        ########
########   @date: 11/14/2016                           ########
########   @description:                               ########
########     Used to sync data from NETZ to Extrahop   ########
########     in order to get up-to-date stores and     ########
########     metadata from CSV                         ########
########   @EH_Firmware:  5.3.2                        ########
###############################################################

import httplib
import logging
import urllib
import ssl
import json
import sys
import csv
import time
import ConfigParser
from Ehop import Ehop

###############################################################
######## Variables                                     ########
###############################################################

vars_file = "vars.cfg"
csv_file = 'test.csv'     # File used to build store data
eh_host = '10.31.0.40'    # EH Host FQDN or IP
api_key = '50c03c5c9889456488887ec3037cef88'
logFileName = 'netz_to_eh_sync.log'  # Logging File for Auditing
logLevel = logging.INFO   # Level of logging.  INFO, WARNING, ERROR, DEBUG, etc
logApp = 'NETZSync'

# Load Vars
config = ConfigParser.ConfigParser
config.read(vars_file)
eh_host = config.get("DEFAULT","eh_host")
csv_file = config.get("DEFAULT","datafile")
api_key = config.get("DEFAULT", "api_key")

###############################################################
######## Functions and Setup                           ########
###############################################################

logger = logging.getLogger(logApp)
logFile = logging.FileHandler(logFileName)
logCon = logging.StreamHandler(sys.stdout)
logFormat = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logFile.setFormatter(logFormat)
logCon.setFormatter(logFormat)
logger.addHandler(logFile)
logger.addHandler(logCon)
logger.setLevel(logLevel)

eh = Ehop(host=eh_host,apikey=api_key)

def load_csv_data(filename):
    f = open(filename)
    data = csv.reader(f)
    stores = {}
    for row in data:
        # It's not a good idea to load everything.  But, for now, let's just do it.
        #TODO: Load only fields needed
        stores.add(row[0])
    return stores

###############################################################
######## Main Script                                    #######
###############################################################
logger.info("Executing")

DOC = """
This script is mean to take a CSV that was merged by GPC personnel and identify 
MAC (Move/Add/Changes) to the Extrahop.

Display Name:  {Mutable}
StoreID: {Unmutable.  2nd and 3rd octets of IP}
Tags:  {Mutable.  Always Changing}
IPs:  {Mutable, but won't change, as this will conflict with StoreID (unmutable)
"""

# Load relevant CSV data into a Set of Dicts
logger.debug("Loading records from CSV")
csv_stores = load_csv_data(csv_file)

# Get All Custom Devices from ExtraHop
eh_stores = {}
logger.debug("Getting custom devices from Extrahop")
eh_data = json.loads(eh.api_request("GET", "customdevices"))
logger.debug("Loaded " + str(len(eh_data)) + " custom devices from Extrahop")
for record in eh_data:
    # Only add records from EH that are actual stores.  This is done with "Store" in the description
    if record["Description"] == "Store":
        eh_stores.add(record)

logger.info("Added " + str(len(eh_stores)) + " filtered devices as stores from ExtraHop")






    # Filter out only Stores as there could be custom devices for other things




