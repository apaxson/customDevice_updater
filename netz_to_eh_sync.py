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

###############################################################
######## Variables                                     ########
###############################################################

csv_file = 'test.csv'     # File used to build store data
eh_host = '10.31.0.40'    # EH Host FQDN or IP
api_key = '50c03c5c9889456488887ec3037cef88'
logFileName = 'netz_to_eh_sync.log'  # Logging File for Auditing
logLevel = logging.INFO   # Level of logging.  INFO, WARNING, ERROR, DEBUG, etc
logApp = 'NETZSync'

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

###############################################################
######## Main Script                                    #######
###############################################################

conn = httplib.HTTPSConnection(eh_host,context=ssl._create_unverified_context())

