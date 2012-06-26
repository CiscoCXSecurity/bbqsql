import bbqsql

from bbq_core import bcolors
from config import RequestsConfig,bbqsqlConfig
import text
import bbq_core
from ConfigParser import RawConfigParser,NoSectionError
import readline

try:
    import readline
except ImportError:
    pass

from copy import copy

# config params that are only used in the menu and shouldn't be passed along to BlindSQLi or other parts of bbqsql
exclude_parms = ['csv_output_file']

# main menu
class bbqMenu:
    def __init__(self):
        # default name for config file
        self.config_file = 'attack.cfg'
        try:
            requests_config = RequestsConfig()
            bbqsql_config = bbqsqlConfig()

            results = None
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

                if results: print results

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
                    attack_config = RawConfigParser()
                    attack_config.add_section('Request Config')
                    attack_config.add_section('HTTP Config')
                    for key,val in requests_config.get_config().iteritems():
                        attack_config.set('Request Config', key, val)

                    for key,val in bbqsql_config.get_config().iteritems():
                        attack_config.set('HTTP Config', key, val)

                    #get filename
                    try:
                        readline.parse_and_bind('tab: complete')
                        fname = raw_input('Config file name [./%s]: '%self.config_file)
                        self.config_file = [fname,self.config_file][fname is '']
                        with open(self.config_file, 'wb') as configfile:
                            attack_config.write(configfile)
                    except KeyboardInterrupt:
                        pass 

                if choice == '4':
                    # Import Config
                    tmp_req_config = dict()
                    tmp_http_config = dict()
                    attack_config = RawConfigParser()

                    #get filename
                    try:
                        readline.parse_and_bind('tab: complete')
                        fname = raw_input('Config file name [./%s]: '%self.config_file)
                        self.config_file = [fname,self.config_file][fname is '']
                        attack_config.read(self.config_file)
                    except KeyboardInterrupt:
                        pass
                    try:
                        for key,val in attack_config.items('Request Config'):
                            tmp_req_config[key] = val
                        for key,val in attack_config.items('HTTP Config'):
                            tmp_http_config[key] = val
                        requests_config.set_config(tmp_req_config)
                        bbqsql_config.set_config(tmp_http_config)
                    except ConfigParser.NoSectionError:
                        print "bad config file. try again"

                if choice == '5' and valid:
                    # Run Exploit
                    results = None

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
                    results = bbq.run()
                    #output to a file if thats what they're into
                    if bbqsql_config['csv_output_file']['value'] is not None:
                        f = open(bbqsql_config['csv_output_file']['value'],'w')
                        f.write("\n".join(results))
                        f.close()
                    # delete stuff
                    del(bbq)

            bbq_core.ExitBBQ(0)
            
        # ## handle keyboard interrupts
        except KeyboardInterrupt:
            print "\n\n Cath you later " + bbq_core.bcolors.RED+"@" + bbq_core.bcolors.ENDC+" the dinner table."


if __name__ == '__main__':
    bbqMenu()
