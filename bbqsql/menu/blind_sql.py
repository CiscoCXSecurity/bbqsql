# file: blind_sql.py
###############################################
from requests_config import RequestsConfig

import subprocess
import os
import time
import re
import sys
import socket
import bbqcore
import text
import yaml
import dictionaries
import traceback
###############################################
# Define path and set it to the bbqsql root dir
###############################################
definepath = os.getcwd()
#os.chdir(definepath)
sys.path.append(definepath)

# Version should be defined here for now until fixed
define_version = '1'

sys.path.append("../")

requests_config = RequestsConfig()
config_keys = requests_config.keys()

try:
    choice = ""
    while choice not in ['done','99','quit','exit']:
        # Show the banner again
        bbqcore.show_banner(define_version,'1.0')

        # This is the menu that displays blind sql injection options
        main_main_menu = bbqcore.CreateMenu(text.blind_text, text.blind_main)

        # Special case of list item 99
        print '\n  99) Return back to the main menu.\n'

        choice = (raw_input(bbqcore.setprompt("1", "")))

        # If the user has chosen '1', then walk the user though attack configuration
        if choice == '1':
            choice = ''
            while not ((choice in ['done'] and requests_config.validate(quiet=True)) or choice in ['quit','exit',99,'99']):
                bbqcore.show_banner(define_version,'1.0')
                http_main_menu = bbqcore.CreateMenu(text.http_text, [])
                
                for ki in xrange(len(config_keys)):
                    key = config_keys[ki]
                    print "\t%d) %s" % (ki,key)
                    if requests_config[key]['value'] is not None:
                        print "\t   Value: %s" % requests_config[key]['value']
                    if requests_config[key]['description'] != '':
                        print "\t   Description: %s" % requests_config[key]['description']
                print "\n"
                requests_config.validate()

                #get input
                choice = (raw_input(bbqcore.setprompt("1", "")))
                #convert to int
                try:
                    choice = int(choice)
                except ValueError:
                    pass
                
                if choice in range(len(config_keys)):
                    key = config_keys[choice]
                    bbqcore.show_banner(define_version,'1.0')
                    print "Parameter    : %s" % key
                    print "Value        : %s" % repr(requests_config[key]['value'])
                    print "Description  : %s" % requests_config[key]['description']
                    print "Allowed types: %s" % repr([t.__name__ for t in requests_config[key]['types']])
                    print "Required     : %s" % repr(requests_config[key]['required'])
                    print "\nPlease enter a new value for %s.\n" % key
                    value = raw_input('value: ')
                    try:
                        value = eval(value)
                    except:
                        pass
                    requests_config[key]['value'] = value 
                    requests_config.validate()
            
            if type(choice) == str and choice.lower() == 'done':
                 # What type of attribute are we gonna use?  
                 attr_main_menu = bbqcore.CreateMenu(text.comparison_text, text.comparison_menu)
                 print '\n  99) Return back to the main menu.\n'
                 attr = (raw_input(bbqcore.setprompt("1", "")))
                 if attr == '99':
                     break
                 if range(1,4).count(int(attr)):
                     pass
                 else:
                     print 'you entered an invalid number\n'
                     time.sleep(3)
                     break

                        # Describe to the user how to construct a query, give examples, then let them type it up
    #                     while 1:
    #                         if blind_menu_choice == '99':
    #                             break
                 query_main_menu = bbqcore.CreateMenu(text.query_text, text.query_menu)
                 print '\n  99) Return back to the main menu.\n'
                 query = raw_input(bbqcore.setprompt(["1"], " Enter the query string"))
                 if query == '99':
                     break

                 bbqcore.show_banner(define_version,'1')
                 run_data = {}
                 print """
                 This is what you provided BBQ sql for attacking. If you provided everytihng we need then we are good to go.



                 \n"""
                 print "http ==> %s" % str(requests_config)
                 
                 print '{0:10} ==> {1:10s}'.format('Injection', query)
                 run_data['injection'] = query
                 print '{0:10} ==> {1:10s}'.format('Comparision', dictionaries.comparison(str(attr)))
                 run_data['comparision'] = dictionaries.comparison(str(attr))
                 print """


                 \n"""
                 print run_data

              #print '\n' + url, query, dictionaries.comparison(str(http_method)), http_method_parameters, cookie_parameters, attr
                 final_check = raw_input(bbqcore.setprompt(["1"], " DOes this look correct?"))
                 bbqcore.ExitBBQ()

    if choice in ['quit','exit']:
        print "later"
        quit()

                
except KeyboardInterrupt:
    print "\n\n Cath you later " + bbqcore.bcolors.RED+"@" + bbqcore.bcolors.ENDC+" the dinner table."

# #
# ## handle exceptions
except Exception, error:
# # #       setcore.log(error)
    traceback.print_exc()
    print "\n\n Something went wrong, printing the error: "+ str(error)
