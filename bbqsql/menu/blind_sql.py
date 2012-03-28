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

try:
    choice = ""
    while choice not in ['done','99','quit','exit']:
        # Show the banner again
        bbqcore.show_banner()

        # This is the menu that displays blind sql injection options
        main_main_menu = bbqcore.CreateMenu(text.blind_text, text.blind_main)

        # Special case of list item 99
        print '\n  99) Return back to the main menu.\n'

        choice = (raw_input(bbqcore.setprompt("1", "")))

        # If the user has chosen '1', then walk the user though attack configuration
        if choice == '1':
            requests_config = RequestsConfig()
            config_keys = requests_config.keys()
            choise = requests_config.run_config()
            
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

                 bbqcore.show_banner()
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
