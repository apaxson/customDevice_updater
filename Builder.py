#!/usr/bin/env python2.7

import json
import os
import sys

from Discovery import Discoverer

def main():
    print_startup_message()

    discoverer = create_discoverer()

    configs = load_json_file()

    for config in configs:
        print "Taggins hosts with '%s' where %s matches %s" % (config['device_tag'],
                                                               config['metric_category'],
                                                               config['metric_key']['value'])
        try:
            discoverer.tag_by_metric_identifier(config['metric_category'],
                                                config['metric'],
                                                config['metric_key'],
                                                config['device_tag'])
        except:
            print_error_header()
            print sys.exc_info()
            print_error_footer()
            continue


    print "Config file processed..."

def create_discoverer():
    host   = raw_input('ExtraHop hostname or IP: ')
    apikey = raw_input('API key: ')
    print ''

    return Discoverer(apikey,host)

def load_json_file():
    path = raw_input('Path of .app file (without quotes): ')
    assert os.path.exists(path), "No file found at " + str(path)

    with open(path) as data_file:
        try:
            config_json = json.load(data_file)
        except:
            print 'Loading .app config JSON failed'
            raise


    print '\n\n'
    return config_json

def print_startup_message():
    print r"""
################################################################################

Welcome to the ExtraHop Application Builder. This script takes in a JSON file
which contains a *list* of objects. Each object describes an identifier in an
environment, like a specific URI path or XenApp, and a tag to apply to devices
which fit the identifier. For an example file, see the included example.app
file.

Prior to running this script, make sure the identifiers are set for the current
environment. Some defaults will be provided, but they need to be validated with
each ExtraHop customer.

Note: Regular expressions should be written in the forward slash notation:

                        /[Ee]xtra[Hh]op!*/

The only regular expression flag supported is the i flag, for case
insensitive. Feel free to include others, but they will be ignored.

################################################################################

"""

def print_error_header():
    print r"""
############################### <ERROR> ########################################"""

def print_error_footer():
    print r"""############################### </ERROR> #######################################
"""


if __name__ == "__main__":
    main()
