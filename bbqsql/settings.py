#file: settings.py

#######################
# General Stuff
#######################

CHARSET = [chr(x) for x in xrange(32,127)]
#CHARSET = [chr(x) for x in xrange(32,39)] + [chr(x) for x in xrange(40,127)] #everything but '
CHARSET_LEN = len(CHARSET)

# Supress output when possible
QUIET = False

# Debugging
DEBUG_FUNCTION_CALLS = False
DEBUG_FUNCTION_ARGUMENTS = False
DEBUG_FUNCTION_RETURNS = False
DEBUG_FUNCTION_RETURN_VALUES = False

#Do fancy pretty printing of results as they come in?
PRETTY_PRINT = True
#How often to refresh the screen while pretty printing (lower looks better but is processor intensive)
PRETTY_PRINT_FREQUENCY = .2

COLORS = {\
    'success':'\033[0m',\
    'working':'\033[92m',\
    'error':'\033[101m',\
    'unknown':'\033[101m',\
    'endc':'\033[0m'}

#######################
# Blind Technique Stuff
#######################

#How many base requests to make to setup Truth() objects
TRUTH_BASE_REQUESTS = 5

# These are the available comparison operators as well as their oposites.
OPPOSITE_COMPARATORS = {"<":">",">":"<","=":"!=","!=":"="}
