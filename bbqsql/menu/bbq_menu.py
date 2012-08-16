import bbqsql

from bbq_core import bcolors
from config import RequestsConfig,bbqsqlConfig
import text
import bbq_core
import time
import os
import sys

import argparse
from ConfigParser import RawConfigParser,NoSectionError,MissingSectionHeaderError
from copy import copy


# config params that are only used in the menu and shouldn't be passed along to BlindSQLi or other parts of bbqsql
exclude_parms = ['csv_output_file','hooks_file']

# main menu
class bbqMenu():
    def __init__(self, run_config=None):
        # default name for config file
        self.config_file = 'attack.cfg'
        try:
            requests_config = RequestsConfig()
            bbqsql_config = bbqsqlConfig()

            results = None
            error = None
            valid = False

            # intitial user menu
            choice = ''
            while choice not in ['99',99,'quit','exit']:
                bbq_core.show_banner()
                show_main_menu = bbq_core.CreateMenu(text.main_text, text.main_menu)
         
                 # special case of list item 99
                print '\n  99) Exit the bbqsql injection toolkit\n'
                
                rvalid = requests_config.validate()
                bvalid = bbqsql_config.validate()
                valid = rvalid and bvalid

                # Big results?  throw that in a csv file!
                if results and len(results) <= 100:
                    print results
                elif results:
                    print '\n\nbbqsql recieved ' + str(len(results)) + ' rows of data, results truncated to last 100'
                    print results[-100:]
                    print '\n\nplease provide a filename so we can save all the results for you'
                    try:
                        import readline
                        readline.parse_and_bind('tab: complete')
                    except ImportError:
                        print 'readline module not found'
                        pass
                    try:
                        readline.parse_and_bind('tab: complete')
                        fname = raw_input('CSV file name [./results.csv]: ')
                    except:
                        print "something went wrong, didn't write results to a file"
                        pass

                    if fname is not None:
                        f = open(fname,'w')
                        f.write("\n".join(",",results))
                        f.close()


                if error: print bbq_core.bcolors.RED+error+ bbq_core.bcolors.ENDC

                if run_config:
                    tmp_req_config = dict()
                    tmp_http_config = dict()
                    try:
                        attack_config = RawConfigParser()
                        self.config_file = [run_config,self.config_file][run_config is '']
                        attack_config.read(self.config_file)
                    except:
                        pass
                    try:
                        for key,val in attack_config.items('Request Config'):
                            tmp_req_config[key] = val
                        for key,val in attack_config.items('HTTP Config'):
                            tmp_http_config[key] = val
                        requests_config.set_config(tmp_req_config)
                        bbqsql_config.set_config(tmp_http_config)
                    except NoSectionError:
                        print "bad config file. try again"

                # Loaded config so clear it out
                run_config = None

                # mainc ore menu
                choice = (raw_input(bbq_core.setprompt()))

                if choice == '1':
                    # Run configuration REPL for HTTP variables
                    requests_config.run_config()
                
                if choice == '2':
                    # Run configuration REPL for bbqsql variables
                    bbqsql_config.run_config()
                
                if choice == '3':                    
                    # Export Config
                    try:
                        import readline
                        readline.parse_and_bind('tab: complete')
                    except ImportError:
                        pass
                    attack_config = RawConfigParser()
                    attack_config.add_section('Request Config')
                    attack_config.add_section('HTTP Config')
                    for key,val in requests_config.get_config().iteritems():
                        attack_config.set('Request Config', key, val)

                    for key,val in bbqsql_config.get_config().iteritems():
                        attack_config.set('HTTP Config', key, val)

                    #get filename
                    try:
                        fname = raw_input('Config file name [./%s]: '%self.config_file)
                        self.config_file = [fname,self.config_file][fname is '']
                        with open(self.config_file, 'wb') as configfile:
                            attack_config.write(configfile)
                    except IOError:
                        print 'Invalid Config or File Path'
                        pass
                    except KeyboardInterrupt:
                        pass 

                if choice == '4':
                    # Import Config
                    try:
                        import readline
                        readline.parse_and_bind('tab: complete')
                    except ImportError:
                        pass
                    tmp_req_config = dict()
                    tmp_http_config = dict()
                    attack_config = RawConfigParser()

                    #get filename
                    try:
                        readline.parse_and_bind('tab: complete')
                        fname = raw_input('Config file name [./%s]: '%self.config_file)
                        self.config_file = [fname,self.config_file][fname is '']
                        attack_config.read(self.config_file)
                    except:
                        pass
                    try:
                        for key,val in attack_config.items('Request Config'):
                            tmp_req_config[key] = val
                        for key,val in attack_config.items('HTTP Config'):
                            tmp_http_config[key] = val
                        requests_config.set_config(tmp_req_config)
                        bbqsql_config.set_config(tmp_http_config)
                    except NoSectionError:
                        print "bad config file. try again"

                if choice == '5' and valid:
                    # Run Exploit
                    results = None

                    # add user defined hooks to our config
                    if bbqsql_config['hooks_file'] and bbqsql_config['hooks_file']['hooks_dict']:
                        bbqsql_config['hooks'] = {'value':bbqsql_config['hooks_file']['hooks_dict'],'name':'hooks','validator':lambda x:True}

                    # combine them into one dictionary
                    attack_config = {}
                    attack_config.update(requests_config.get_config())
                    attack_config.update(bbqsql_config.get_config())

                    #delete unwanted config params before sending the config along
                    for key in exclude_parms:
                        if key in attack_config:
                            del(attack_config[key])

                    # launch attack
                    bbq = bbqsql.BlindSQLi(**attack_config)
                    if not bbq.error:
                        error = None
                        try:
                            ok = raw_input('Everything lookin groovy?[y,n] ')
                        except KeyboardInterrupt:
                            ok = False
                        if ok and ok[0] != 'n':
                            #print bbq
                            #time.sleep(5)
                            results = bbq.run()
                            #output to a file if thats what they're into
                            if bbqsql_config['csv_output_file']['value'] is not None:
                                f = open(bbqsql_config['csv_output_file']['value'],'w')
                                f.write("\n".join(results))
                                f.close()
                    else:
                        error = bbq.error
                    # delete stuff
                    del(bbq)
                if choice == '6':
                    bbq_core.about()

            bbq_core.ExitBBQ(0)
            
        # ## handle keyboard interrupts
        except KeyboardInterrupt:
            print "\n\n Cath you later " + bbq_core.bcolors.RED+"@" + bbq_core.bcolors.ENDC+" the dinner table."


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='bbqsql')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-c',  metavar='config', nargs='+', help='import config file', default=None)

    results = parser.parse_args()
    print results

    if results.c is not None:
        bbqMenu(results.c[0])
    else:
        bbqMenu()
