#!/usr/bin/env python
#########################################
#
###############################################
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
     main_main_menu = bbqcore.CreateMenu(text.main_text, text.blind_main)

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
     if blind_menu_choice == '1': #'SQL TIME MAN
         url = raw_input(bbqcore.setprompt(["1"], " Enter the URL "))

         # Show the user which types of comparison methods are available for blind sql injection
         while 1:
             if blind_menu_choice == '99':
                 break
             http_method_menu = bbqcore.CreateMenu(text.method_text, text.method_menu)
             print '\n  99) Return back to the main menu.\n'
             http_method = (raw_input(bbqcore.setprompt("1", "")))
             if blind_menu_choice == '99':
                 break
             if http_method == '1':
                 http_method_parameters = ""
                 break
             if http_method == '2':
                 http_method_parameters = raw_input(bbqcore.setprompt(["1"], " Paste the Post parameters "))
                 break
         while 1:
             if blind_menu_choice == '99':
                 break
             cookie_menu = bbqcore.CreateMenu(text.cookie_text, text.cookie_menu)
             print '\n  99) Return back to the main menu.\n'
             cookies_needed = (raw_input(bbqcore.setprompt("1", "")))
             if cookies_needed == '99':
                 break
             if cookies_needed == '2':
                 cookie_parameters = ""
                 break
             if cookies_needed == '1':
                 cookie_parameters = raw_input(bbqcore.setprompt(["1"], " Paste the Cookies here"))
                 break

         while 1:
             if blind_menu_choice == '99':
                 break
             attr_main_menu = bbqcore.CreateMenu(text.comparison_text, text.comparison_menu)
             print '\n  99) Return back to the main menu.\n'
             attr = (raw_input(bbqcore.setprompt("1", "")))
             break
         # Describe to the user how to construct a query, give examples, then let them type it up
         while 1:
             if blind_menu_choice == '99':
                 break
#             query_main_menu = bbqcore.CreateMenu(text.query_text, text.query_menu)
             print text.query_text
             query = raw_input(bbqcore.setprompt(["1"], " Enter the query string"))
             print '\n  99) Return back to the main menu.\n'
             break
         print '\n' + url, query, dictionaries.comparison(str(http_method)), http_method_parameters, cookie_parameters, attr
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
