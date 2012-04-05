import bbqsql

import bbqcore

try:
    import readline
except ImportError:
    pass

from bbqcore import bcolors
from config import RequestsConfig,bbqsqlConfig

import text
from copy import copy


# main menu
class bbqMenu:
    def __init__(self):
        try:
            requests_config = RequestsConfig()
            bbqsql_config = bbqsqlConfig()

            results = None
            valid = False

            # intitial user menu
            choice = ''
            while choice not in ['99',99,'quit','exit']:
                bbqcore.show_banner()
                show_main_menu = bbqcore.CreateMenu(text.main_text, text.main_menu)
         
                 # special case of list item 99
                print '\n  99) Exit the bbqsql injection toolkit\n'
                
                rvalid = requests_config.validate()
                bvalid = bbqsql_config.validate()
                valid = rvalid and bvalid

                if results: print results

                # mainc ore menu
                choice = (raw_input(bbqcore.setprompt()))

                if choice == '1': # Binary Blind SQL Injection Test
                    requests_config.run_config()
                
                if choice == '2':
                    bbqsql_config.run_config()
                
                if choice == '5' and valid:
                    requests_config.convert_to_query()
                    
                    # combine them into one dictionary
                    attack_config = {}
                    attack_config.update(requests_config.get_config())
                    attack_config.update(bbqsql_config.get_config())
                    # launch attack
                    bbq = bbqsql.BlindSQLi(**attack_config)
                    results = bbq.run()
                    del(bbq)
                    del(results)
                    results = None


            bbqcore.ExitBBQ(0)
            
        # ## handle keyboard interrupts
        except KeyboardInterrupt:
            print "\n\n Cath you later " + bbqcore.bcolors.RED+"@" + bbqcore.bcolors.ENDC+" the dinner table."


if __name__ == '__main__':
    bbqMenu()
