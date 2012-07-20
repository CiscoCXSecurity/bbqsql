#
# Centralized classes, work in progress
# 

import re
import os

# used to grab the true path for current working directory
class bcolors:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERL = '\033[4m'
    ENDC = '\033[0m'
    backBlack = '\033[40m'
    backRed = '\033[41m'
    backGreen = '\033[42m'
    backYellow = '\033[43m'
    backBlue = '\033[44m'
    backMagenta = '\033[45m'
    backCyan = '\033[46m'
    backWhite = '\033[47m'

    def disable(self):
        self.PURPLE = ''
        self.CYAN = ''
        self.BLUE = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.RED = ''
        self.ENDC = ''
        self.BOLD = ''
        self.UNDERL = ''
        self.backBlack = ''
        self.backRed = ''
        self.backGreen = ''
        self.backYellow = ''
        self.backBlue = ''
        self.backMagenta = ''
        self.backCyan = ''
        self.backWhite = ''
        self.DARKCYAN = ''


#
# Class for colors
#
def ExitBBQ(exitcode=0):
    print "\n"*100
    print "\n\nGoodbye " + bcolors.RED + os.getlogin() + bcolors.ENDC+", and enjoy a hot plate of ribs on the house.\n"
    quit()

def show_graphics():
    print bcolors.YELLOW + r"""
    _______   _______    ______    ______    ______   __       
   |       \ |       \  /      \  /      \  /      \ |  \      
   | $$$$$$$\| $$$$$$$\|  $$$$$$\|  $$$$$$\|  $$$$$$\| $$      
   | $$__/ $$| $$__/ $$| $$  | $$| $$___\$$| $$  | $$| $$      
   | $$    $$| $$    $$| $$  | $$ \$$    \ | $$  | $$| $$      
   | $$$$$$$\| $$$$$$$\| $$ _| $$ _\$$$$$$\| $$ _| $$| $$      
   | $$__/ $$| $$__/ $$| $$/ \ $$|  \__| $$| $$/ \ $$| $$_____ 
   | $$    $$| $$    $$ \$$ $$ $$ \$$    $$ \$$ $$ $$| $$     \
    \$$$$$$$  \$$$$$$$   \$$$$$$\  \$$$$$$   \$$$$$$\ \$$$$$$$$
                     \$$$                \$$$ """ + bcolors.ENDC           

    print bcolors.RED + r"""
                   _.(-)._
                .'         '.
               / 'or '1'='1  \
               |'-...___...-'|
                \    '='    /
                 `'._____.'` 
                  /   |   \
                 /.--'|'--.\
              []/'-.__|__.-'\[]
                      |
                     [] """ + bcolors.ENDC
    return

def show_banner():
    print "\n"*100
    show_graphics()
    print bcolors.BLUE + """
    BBQSQL injection toolkit ("""+bcolors.YELLOW+"""bbqsql"""+bcolors.BLUE+""")         
    Lead Development: """ + bcolors.RED+"""Ben Toews"""+bcolors.BLUE+"""("""+bcolors.YELLOW+"""mastahyeti"""+bcolors.BLUE+""")         
    Development: """ + bcolors.RED+"""Scott Behrens"""+bcolors.BLUE+"""("""+bcolors.YELLOW+"""arbit"""+bcolors.BLUE+""")         
    Menu modified from code for Social Engineering Toolkit (SET) by: """ + bcolors.RED+"""David Kennedy """+bcolors.BLUE+"""("""+bcolors.YELLOW+"""ReL1K"""+bcolors.BLUE+""")    
    SET is located at: """ + bcolors.RED+"""http://www.secmaniac.com"""+bcolors.BLUE+"""("""+bcolors.YELLOW+"""SET"""+bcolors.BLUE+""")    
    Version: """+bcolors.RED+"""%s""" % ('1.0') +bcolors.BLUE+"""               
    
  """ + bcolors.GREEN+"""  The 5 S's of BBQ: 
    Sauce, Spice, Smoke, Sizzle, and """ + bcolors.RED+"""SQLi
    """
    print  bcolors.ENDC + '\n'

def setprompt(category=None, text=None):
    '''helper function for creating prompt text'''
    #base of prompt
    prompt =  bcolors.UNDERL + bcolors.DARKCYAN + "bbqsql"
    #if they provide a category
    if category:
            prompt += ":"+category
    prompt += ">"
    #if they provide aditional text
    if text:
        prompt += " "+ text + ":"
    prompt += bcolors.ENDC + " "
    return prompt

def about():
    '''define help, credits, and about'''
    print "\n"*100
    show_graphics()
    print "\n"*5
    print bcolors.BOLD + """    Help\n""" + bcolors.ENDC + """
    For help, please view the Readme.MD file for usage examples
    and detailed information on how the tool works

    If you are still running into issues, have ideas for improvements,
    or just feature requests you can submit here:
    """ + bcolors.BOLD + """https://github.com/Neohapsis/bbqsql/issues\n\n""" + bcolors.ENDC 

    print bcolors.BOLD + """    Credits\n""" + bcolors.ENDC + """
    Special thanks to David Kennedy, Kenneth Reitz, Neohapsis, Wikipedia, and
    everyone who has helped file bug fixes.  Oh, and ribs.  Mmmm ribs! \n\n""" 

    print bcolors.BOLD + """    About\n""" + bcolors.ENDC + """
    BBQSQL version 1.0
    https://github.com/Neohapsis/bbqsql
    \n\n""" 

    raw_input("Press any key to continue")

class CreateMenu:
    def __init__(self, text, menu):
        self.text = text
        self.menu = menu

        print text
        #print "\nType 'help' for information on this module\n"

        for i, option in enumerate(menu):

            menunum = i + 1

            # Check to see if this line has the 'return to main menu' code
            match = re.search("0D", option)

            # If it's not the return to menu line:
            if not match:
                if menunum < 10:
                    print('   %s) %s' % (menunum,option))
                else:
                    print('  %s) %s' % (menunum,option))
            else:
                print '\n  99) Return to Main Menu\n'
        return
