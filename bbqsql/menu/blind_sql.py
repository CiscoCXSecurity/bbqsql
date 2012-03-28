# file: blind_sql.py
###############################################
from requests_config import RequestsConfig,bbqsqlConfig

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
            choice = requests_config.run_config()
            
            if type(choice) == str and choice.lower() == 'done':
                bbqsql_config = bbqsqlConfig()
                choice = bbqsql_config.run_config()

                if type(choice) == str and choice.lower() == 'done':
                    print requests_config
                    print "\n\n"
                    print bbqsql_config

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
