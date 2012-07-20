# file: pretty_print.py

from bbqsql import utilities

import sys
import re
import gevent
from gevent.event import Event
from subprocess import Popen,PIPE,STDOUT

@utilities.debug 
def len_less_color(line):
	'''return the length of a string with the color characters stripped out'''
	return len(re.sub(u'\033\[[0-9]+m','',line))

class PrettyTable:
	def __init__(self,get_table_callback=None,get_status_callback=None,update=.2,row_filter=None):
		self.update = update

		#function to call to get new tables
		self.get_table_callback = get_table_callback

		#function to call to get technique status
		self.get_status_callback = get_status_callback

		# find the terminal size
		self._find_screen_size()

		self.row_filter = row_filter

	@utilities.debug 
	def start(self):
		self._printer_glet = gevent.spawn(self._table_printer)

	@utilities.debug 
	def die(self):
		self._printer_glet.kill()

	def _find_screen_size(self):
		if self._is_linux():
			self.sizey,self.sizex = Popen(['stty','size'],stdout=PIPE,stderr=STDOUT,stdin=None).stdout.read().replace('\n','').split(' ')
			self.sizex = int(self.sizex)
			self.sizey = int(self.sizey)
		else:
			self.sizey,self.sizex = 40,150

	def _is_linux(self):
		return 'linux' in sys.platform or 'darwin' in sys.platform
	
	def _table_printer(self):
		'''
		pretty prints a 1-d list.
		'''

		i = 0
		while True:
			table = self.get_table_callback(color=True)
			#table = self.get_table_callback()

			# keep it short
			if len(table)>100: table = table[-100:]

			table = filter(self.row_filter,table)

			#figure out how many new lines are needed to be printed before the table data
			tlen = len(table)
			new_lines_needed = self.sizey - tlen - reduce(lambda x,row: x + len_less_color(row) // self.sizex,table,0) - 3

			#start building out table,
			str_table = "\n"
			str_table += "\n".join(table)
			str_table += "\n"*new_lines_needed

			if self.get_status_callback:
				str_table += "\n" + str(self.get_status_callback())
			
			str_table += "\n"
			
			sys.stdout.write(str_table)

			# sleep for a bit
			gevent.sleep(self.update)