# file: text.py

'''Text should be stored here'''

from bbqcore import bcolors

define_version = '1.0'

main_text = " Select from the menu:\n"

blind_text = """Blind SQL Injection is used when a web application is vulnerable to an SQL injection but the results 
of the injection are not visible to the attacker. The page with the vulnerability may not be one that displays data 
but will display differently depending on the results of a logical statement injected into the legitimate SQL statement 
called for that page.

If this is the first time using this tool, the menu system will help generate a config you can use for your attack

when setting up the attack make sure you specifiy the following macro where you want the injection """ + bcolors.BOLD + """${injection}""" + bcolors.ENDC + """ 

This tells bbqsql where to insrt your injection string.  You can put the ${injection} tag wherever you identified 
the vulnerality (exp. post parameter, cookie value, get parameter)

""" + bcolors.BOLD + """GET Paramter Example""" + bcolors.ENDC + """

If you identified the parameter 'guid' is vulnerable during a GET request, your URL may look like the following:

http://www.my-bad-site.com/?foo=bar&guid=${injection}

""" + bcolors.BOLD + """Cookie Value Example""" + bcolors.ENDC + """

If you identified the parameter 'cart' is vulnerable during a GET request, your cookie string may look like the following:

bob=foo; jsessionid=someidhere; cart=${injection}

""" + bcolors.BOLD + """You must specifcy the ${injection} tag or the tool will not run!""" + bcolors.ENDC + """
\n"""

main_menu = ['Setup HTTP Parameters',
	     'Setup BBQSQL Options',
         'Export Config (not implemented)',
         'Import Config (not implemented)',
	     'Run Exploit (not implemented)',
	     'Help, Credits, and About (not implemented)']	     

blind_main = ['Setup Attack',
        'Load Config']

comparison_menu = ['Response Code',
                'Response Size',
                'Response Time\n']

method_menu = ['GET', 'POST\n']

cookie_text = """
Does your request require cookies?:"""

cookie_menu = ['yes', 'no\n']

method_text = """
Select which method your attack will use:"""

comparison_text = """
Below is a list of blind techniques you can use to exfiltrate data

Select one of the below:
"""

query_menu = ""

query_text = ("""
The query input is where you will construct your query used to exfiltrate informaiton from the database.  The assumption is
that you already have identified SQL injeciton on a vulnerable parameter, and have tested a query that is sucessful.

Below is an example query you can use to construct your query.  In this example, the attacker is lookinn to select the database version:

""" + bcolors.RED + """vulnerable_parameter'; if(ASCII(SUBSTRING((SELECT @@version LIMIT 1 OFFSET ${row_index}) , ${char_index} ,1))) > ASCII(${charval}) WAITFOR DELAY '0:0:0${sleep}'; --""" + bcolors.ENDC + """

You need to provide the following placeholders of informationo in order for the attack to work.  Once you put these in your query, bbqsql will do the rest:

""" + bcolors.BOLD + """${row_index}""" + bcolors.ENDC + """ = This tells bbqsql to iterate rows here.  Since we are using LIMIT we can view n number of rows depeding on ${row_index} value

""" + bcolors.BOLD + """${char_index}""" + bcolors.ENDC + """ = This tells bbqsql which character from the subselect to query.  

""" + bcolors.BOLD + """${charval}""" + bcolors.ENDC + """ = This tells bbqsql where to compare the results from the subselect to validate the result


""" + bcolors.BOLD + """${sleep}""" + bcolors.ENDC + """ = This is optional but tells bbqsql where to insert the number of seconds to sleep when perofrming time basd sql injection

\n
""")
