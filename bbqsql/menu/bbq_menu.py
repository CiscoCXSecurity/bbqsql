import bbqcore
from bbqcore import bcolors
from config import RequestsConfig,bbqsqlConfig
import text


# main menu
class bbqMenu:
    def __init__(self):
        define_version = 1.0

        try:
            requests_config = RequestsConfig()
            bbqsql_config = bbqsqlConfig()

            # intitial user menu
            choice = ''
            while choice not in ['99',99,'quit','exit']:
                bbqcore.show_banner()
                show_main_menu = bbqcore.CreateMenu(text.main_text, text.main_menu)
         
                 # special case of list item 99
                print '\n  99) Exit the bbqsql injection toolkit\n'
         
                requests_config.validate()
                bbqsql_config.validate()

                # mainc ore menu
                choice = (raw_input(bbqcore.setprompt("0", "")))

                if choice == '1': # Binary Blind SQL Injection Test
                    requests_config.run_config()
                
                if choice == '2':
                    bbqsql_config.run_config()

            
            bbqcore.ExitBBQ(0)
            
        # ## handle keyboard interrupts
        except KeyboardInterrupt:
            print "\n\n Cath you later " + bbqcore.bcolors.RED+"@" + bbqcore.bcolors.ENDC+" the dinner table."
        # #
        # ## handle exceptions
        except Exception, error:
        # # #       setcore.log(error)
            print "\n\n Something went wrong, printing the error: "+ str(error)


if __name__ == '__main__':
    bbqMenu()