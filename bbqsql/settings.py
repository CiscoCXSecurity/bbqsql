#file: settings.py

CHARSET = [chr(x) for x in xrange(32,127)]
#CHARSET = [chr(x) for x in xrange(32,39)] + [chr(x) for x in xrange(40,127)] #everything but '
CHARSET_LEN = len(CHARSET)

#Supress output when possible
QUIET = False

#Debugging settings.
DEBUG_FUNCTION_CALL = False
DEBUG_FUNCTION_RETURN = False
DEBUG_MARKER = "##> "