import gevent
from gevent.event import Event

from subprocess import Popen,PIPE,STDOUT
import sys

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

	def start(self):
		self._printer_glet = gevent.spawn(self._table_printer)

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
		return 'linux' in sys.platform
	
	def _table_printer(self):
		'''
		pretty prints a 1-d list.
		'''

		i = 0
		while True:
			gevent.sleep(self.update)
			table = self.get_table_callback()

			table = filter(self.row_filter,table)

			#figure out how many new lines are needed to be printed before the table data
			tlen = len(table)
			new_lines_needed = self.sizey - tlen - reduce(lambda x,row: x + len(row) // self.sizex,table,0) - (not not self.get_status_callback)

			#start building out table,
			str_table = "\n".join(table)
			str_table += "\n"*new_lines_needed

			if self.get_status_callback:
				str_table += "\n" + str(self.get_status_callback())
			
			print str_table