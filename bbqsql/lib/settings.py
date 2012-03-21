#file: settings.py

#######################
# General Stuff
#######################

CHARSET = [chr(x) for x in xrange(32,127)]
#CHARSET = [chr(x) for x in xrange(32,39)] + [chr(x) for x in xrange(40,127)] #everything but '
CHARSET_LEN = len(CHARSET)

#Supress output when possible
QUIET = False

#Do fancy pretty printing of results as they come in?
PRETTY_PRINT = True
#How often to refresh the screen while pretty printing (lower looks better but is processor intensive)
PRETTY_PRINT_FREQUENCY = .2

COLORS = {\
    'success':'\033[0m',\
    'working':'\033[93m',\
    'error':'\033[101m',\
    'unknown':'\033[101m',\
    'endc':'\033[0m'}

#######################
# Blind Technique Stuff
#######################

#mappings from response attributes to Requester subclasses
from .requester import *
response_attributes = {\
    'status_code':Requester,\
    'url':Requester,\
    'time':LooseNumericRequester,\
    'size':LooseNumericRequester,\
    'text':LooseTextRequester,\
    'content':LooseTextRequester,\
    'encoding':LooseTextRequester,\
    'cookies':LooseTextRequester,\
    'headers':LooseTextRequester,\
    'history':LooseTextRequester
}

#How many base requests to make to setup Truth() objects
TRUTH_BASE_REQUESTS = 5

# These are the available comparison operators as well as their oposites.
OPPOSITE_COMPARATORS = {"<":">",">":"<","=":"!=","!=":"="}
