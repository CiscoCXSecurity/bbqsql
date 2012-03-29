# file: text.py

'''Text should be stored here'''

from bbqcore import bcolors

define_version = '1.0'

main_text = " Select from the menu:\n"

main_menu = ['Setup HTTP Parameters',
	     'Setup BBQSQL Options',
         'Export Config (not implemented)',
         'Import Config (not implemented)',
	     'Run Exploit (not implemented)',
	     'Help, Credits, and About (not implemented)']	     


query_text = """
The query input is where you will construct your query used
to exfiltrate information from the database.  The assumption is
that you already have identified SQL injection on a vulnerable
parameter, and have tested a query that is successful.

Below is an example query you can use to construct your query.
In this example, the attacker is looking to select the database
version:
""" + bcolors.RED + """
vulnerable_parameter'; if(ASCII(SUBSTRING((SELECT @@version LIMIT
1 OFFSET ${row_index}) , ${char_index} ,1))) > ASCII(${charval})
WAITFOR DELAY '0:0:0${sleep}'; --
""" + bcolors.ENDC + """
You need to provide the following placeholders of information 
in order for the attack to work.  Once you put these in your 
query, bbqsql will do the rest:

""" + bcolors.BOLD + """${row_index}""" + bcolors.ENDC + """= This tells bbqsql to iterate rows here.  Since
we are using LIMIT we can view n number of rows depending on
${row_index} value

""" + bcolors.BOLD + """${char_index}""" + bcolors.ENDC + """ = This tells bbqsql which character from the 
subselect to query.  

""" + bcolors.BOLD + """${charval}""" + bcolors.ENDC + """ = This tells bbqsql where to compare the results
from the subselect to validate the result

""" + bcolors.BOLD + """${sleep}""" + bcolors.ENDC + """ = This is optional but tells bbqsql where to insert
 the number of seconds to sleep when performing time based sql 
 injection



"""
