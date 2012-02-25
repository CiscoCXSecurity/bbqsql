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
PRETTY_PRINT_FREQUENCY = .5


#######################
# Blind Technique Stuff
#######################

#How many base requests to make to setup Truth() objects
TRUTH_BASE_REQUESTS = 5

# this specifies the available comparison attributes, what Truth class to use for the and what standard deviation is acceptable in that Truth class
import truth
COMPARISON_ATTRS = {\
        "content"       :{'truth':truth.LooseTextTruth,'std':.6},\
        "text"          :{'truth':truth.LooseTextTruth,'std':.6},\
        "size"          :{'truth':truth.LooseNumericTruth,'std':1},\
        "response_time" :{'truth':truth.LooseNumericTruth,'std':4},\
        "status_code"   :{'truth':truth.Truth,'std':1}\
}

# These are the available comparison operators as well as their oposites.
OPPOSITE_COMPARATORS = {"<":">",">":"<","=":"!=","!=":"="}