'''Text should be stored here'''

from bbq_core import bcolors

define_version = '1.0'

main_text = " Select from the menu:\n"

main_menu = ['Setup HTTP Parameters',
	     'Setup BBQSQL Options',
         'Export Config',
         'Import Config',
	     'Run Exploit',
	     'Help, Credits, and About']	     


query_text = """
The query input is where you will construct your query used
to exfiltrate information from the database.  The assumption is
that you already have identified SQL injection on a vulnerable
parameter, and have tested a query that is successful.

Below is an example query you can use to construct your query.
In this example, the attacker is looking to select hostname from a table called systems :

""" + bcolors.RED + """
' and ASCII(SUBSTR((SELECT hostname FROM systems LIMIT 1 OFFSET 
${row_index:1}),${char_index:1},1))${comparator:>}${char_val:0} #
""" + bcolors.ENDC + """

You need to provide the following tags 
in order for the attack to work.  The format is ${template_name:default_value}.
The template names you have available are defined below.  Once you 
put these in your 
query, bbqsql will do the rest:

""" + bcolors.BOLD + """${row_index:1}""" + bcolors.ENDC + """= This tells bbqsql to iterate rows here.  Since
we are using LIMIT we can view n number of rows depending on
${row_index} value.  Here we set it to 1, sto start with row 1.  
If your attack fails at row n, you can 
edit this value to resume your attack.  

""" + bcolors.BOLD + """${char_index:1}""" + bcolors.ENDC + """ = This tells bbqsql which character from the 
subselect to query.  Here we start with position 1 of the subselect.  
You should always set this to a value of 1
unless your attack failed at a certain character position.  

""" + bcolors.BOLD + """${comparator:>}""" +  bcolors.ENDC + """This is how you tell BBQSQL to compare the responses 
to determine if the result is true or not.  You should set this to the > symbol.

""" + bcolors.BOLD + """${char_val:0}""" + bcolors.ENDC + """ = This tells bbqsql where to compare the results
from the subselect to validate the result.  Set this to 0 and the search 
algorithm will do the rest.  

""" + bcolors.BOLD + """${sleep}""" + bcolors.ENDC + """ = This is optional but tells bbqsql where to insert
the number of seconds to sleep when performing time based sql 
injection


"""
