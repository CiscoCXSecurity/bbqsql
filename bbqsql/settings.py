#file: settings.py

CHARSET = [chr(x) for x in xrange(32,127)]
#CHARSET = [chr(x) for x in xrange(32,39)] + [chr(x) for x in xrange(40,127)] #everything but '
CHARSET_LEN = len(CHARSET)

#Supress output when possible
QUIET = False

#Do fancy pretty printing of results as they come in?
PRETTY_PRINT = True
#How often to refresh the screen while pretty printing (lower looks better but is processor intensive)
PRETTY_PRINT_FREQUENCY = .5

#How many base requests to make to setup Truth() objects
TRUTH_BASE_REQUESTS = 5

#Acceptable amounts of standard deviation for various types of 
ACCEPTABLE_DEVIATION_RESPONSE_TIME  = 4
ACCEPTABLE_DEVIATION_SIZE           = 1
ACCEPTABLE_DEVIATION_TEXT           = .6  # for difflib.get_close_matches