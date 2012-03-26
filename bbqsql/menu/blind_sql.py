#!/usr/bin/env python
#
###############################################
from .utils import validate_url

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
try:
   while 1:
     # Show the banner again
     bbqcore.show_banner(define_version,'1')

    ###################################################
    #        USER INPUT: SHOW MAIN MENU               #
    ###################################################

     # This is the menu that displays blind sql injection options
     main_main_menu = bbqcore.CreateMenu(text.blind_text, text.blind_main)

     # Special case of list item 99
     print '\n  99) Return back to the main menu.\n'

     blind_menu_choice = (raw_input(bbqcore.setprompt("1", "")))

     # Exit if a 99 or exit is submitted
     if blind_menu_choice == 'exit':
         print 'exit'
         break

     if blind_menu_choice == '99':
         break

     # If the user has chosen '1', then walk the user though attack configuration
     if blind_menu_choice == '1':
         url = raw_input(bbqcore.setprompt(["1"], " Enter the URL "))
         
         # Check if this is a vliad URL, and if it isn't quit
         if not validate_url(url):
             print "not a valid url...quitting\n"
             time.sleep(3)
             break

         # Show the user which types of comparison methods are available for blind sql injection
         while 1:
             if blind_menu_choice == '99':
                 break
             http_method_menu = bbqcore.CreateMenu(text.method_text, text.method_menu)
             print '\n  99) Return back to the main menu.\n'
             http_method = (raw_input(bbqcore.setprompt("1", "")))
             if http_method == '99':
                 break
             # Make sure the user slected the correct option, otherwise quit
             if range(1,3).count(int(http_method)):
                 if http_method == '1':
                     http_method_parameters = ""
                     pass
                 # If the user wants to do a POST, collect post data
                 if http_method == '2':
                     http_method_parameters = raw_input(bbqcore.setprompt(["1"], " Paste the Post parameters "))
                     pass
             else:
                 print 'you entered an invalid choice...quitting\n'
                 time.sleep(3)
                 break

             # Does the user need cookies?  yes or no otehrwise quit
             cookie_menu = bbqcore.CreateMenu(text.cookie_text, text.cookie_menu)
             print '\n  99) Return back to the main menu.\n'
             cookies_needed = (raw_input(bbqcore.setprompt("1", "")))
             if cookies_needed == '99':
                 break
             if range(1,3).count(int(http_method)):
                 if cookies_needed == '2':
                     cookie_parameters = ""
                     pass

                 if cookies_needed == '1':
                     cookie_parameters = raw_input(bbqcore.setprompt(["1"], " Paste the Cookies here"))
                     pass
             else:
                 print 'you entered an invalid choice...quitting\n'
                 time.sleep(3)
                 break

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
             print '{0:10} ==> {1:10s}'.format('URL', url)
             run_data['url'] = url
             print '{0:10} ==> {1:10s}'.format('Method', dictionaries.http_method(str(http_method)))
             run_data['method'] = dictionaries.http_method(str(http_method))
             if http_method_parameters != "":
                 print '{0:10} ==> {1:10s}'.format('Parameters', http_method_parameters)
                 run_data['post_parameters'] = http_method_parameters
             if cookie_parameters != "":
                 print '{0:10} ==> {1:10s}'.format('Parameters', cookie_parameters)
                 run_data['cookies'] = cookie_parameters
             
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

     # If the user has chosen '2', request configuration, validate, and execute attack
     if blind_menu_choice == '2': #'SQL TIME MAN
          blind_config = raw_input(bbqcore.setprompt(["1"], " Enter the filename to run (current directory only please)"))
          if os.path.isfile(blind_config):
              f = open(blind_config, 'r')
              parsed_config = yaml.load(f)
              print parsed_config
              time.sleep(5)
              #exec("import " + blind_config)
          else:
              print configs
              print 'in else'
              time.sleep(5)
                
except KeyboardInterrupt:
    print "\n\n Cath you later " + bbqcore.bcolors.RED+"@" + bbqcore.bcolors.ENDC+" the dinner table."

# #
# ## handle exceptions
except Exception, error:
# # #       setcore.log(error)
    traceback.print_exc()
    print "\n\n Something went wrong, printing the error: "+ str(error)
