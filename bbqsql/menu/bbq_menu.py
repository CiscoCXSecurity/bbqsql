import bbqcore
from bbqcore import bcolors
import text


# main menu
class bbqMenu:
    def __init__(self):
        define_version = 1.0

        try:
         
             # intitial user menu
            while 1:
                bbqcore.show_banner(define_version,'1')
                show_main_menu = bbqcore.CreateMenu(text.main_text, text.main_menu)
         
                 # special case of list item 99
                print '\n  99) Exit the bbqsql injection toolkit\n'
         
                # mainc ore menu
                main_menu_choice = (raw_input(bbqcore.setprompt("0", "")))

                # quit out
                if main_menu_choice == 'exit' or main_menu_choice == "99" or main_menu_choice == "quit":
                    bbqcore.ExitBBQ(0)
                   # cleans up stale processes from SET

                if main_menu_choice == '1': # Binary Blind SQL Injection Test
                    print '1'
                    try: reload(blind_sql)
                    except: import blind_sql
            
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