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

import logging
import json
import sys
import csv
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

def load_csv_records(filename):
    logger.debug("Loading records from CSV")
    f = open(filename)
    data = csv.reader(f)
    stores = {}
    for row in data:
        # It's not a good idea to load everything.  But, for now, let's just do it.
        #TODO: Load only fields needed
        stores.add(row[0])
    logger.debug("Loaded " + str(len(stores)) + " records from " + filename)
    return stores

def load_eh_records(extrahop):
    loaded_stores = {}
    logger.debug("Getting custom devices from Extrahop")
    eh_data = json.loads(extrahop.api_request("GET", "customdevices"))
    
    for record in eh_data:
        if record["description"] == "Store":
            loaded_stores.add(record)
    
    logger.debug("Added " + str(len(loaded_stores)) + " filtered devices as stores from Extrahop")
    return loaded_stores
    
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

csv_stores = load_csv_records(csv_file)

# Get All Custom Devices from ExtraHop
eh_stores = {}
eh_records = load_eh_records(eh)

for record in eh_records:
    # Only add records from EH that are actual stores.  This is done with "Store" in the description
    if record["Description"] == "Store":
        eh_stores.add(record)


