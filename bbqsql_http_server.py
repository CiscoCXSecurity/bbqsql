#!/usr/bin/env python
# By Scott Behrens(arbit), 2012 

"""This is a simple webserver vulnerable to SQLi injection
make your query string look like this: http://127.0.0.1:8090/time?row=1&character_index=1&character_value=95&comparator=>&sleep=1
"""

import eventlet 
from eventlet import wsgi
from eventlet.green import time
from urlparse import parse_qs
import urllib2

# Database constants
datas = ['hello','world']

# Different comparators BBsql uses
comparators = ['>','=','<','false']


def parse_response(env, start_response):
    '''Parse out all necessary information and determine if the query resulted in a match'''
    try:
        params =  parse_qs(urllib2.unquote(env['QUERY_STRING']))

        # Extract out all of the sqli information
        row_index =  int(params['row_index'].pop(0))
        char_index = int(params['character_index'].pop(0)) - 1
        test_char = int(params['character_value'].pop(0)) 
        comparator = comparators.index(params['comparator'].pop(0)) - 1
        sleep_int = int(params['sleep'].pop(0))

        # Determine which character position we are at during the injection
        current_character = datas[row_index][char_index]

        # Call the function for what path was given based on the path provided
        response = types[env['PATH_INFO']](test_char, current_character, comparator, sleep_int, start_response)

        return response
    except:
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])
        return ['ereror\r\n']


def time_based_blind(test_char, current_character, comparator, sleep_int, start_response):
    try:
        truth = (cmp(test_char,ord(current_character)) == comparator)
        # Snage the query string and parse it into a dict
        sleep_time = float(sleep_int) * truth
        time.sleep(sleep_time)
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Hello!\r\n']
    except:
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])
        return ['error\r\n']

def boolean_based_error(test_char, current_character, comparator, env, start_response):
    try:
        truth = (cmp(test_char,ord(current_character)) == comparator)
        # Snage the query string and parse it into a dict
        if truth:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return ['Hello, im a bigger cheese in this cruel World!\r\n']
        else:
            start_response('404 File Not Found', [('Content-Type', 'text/plain')])
            return ['file not found: error\r\n']
            
    except:
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])
        return ['error\r\n']

def boolean_based_size(test_char, current_character, comparator, env, start_response):
    try:
        truth = (cmp(test_char,ord(current_character)) == comparator)
        # Snage the query string and parse it into a dict
        if truth:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return ['Hello, you just submitted a query and i found a match\r\n']
        else:
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return ['Hello, no match!\r\n']
    except:
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])
        return ['eerrrrrrrror\r\n']
        
# Dict of the type's of tests, so pass your /path to execute that type of test
types = {'/time':time_based_blind,'/error':boolean_based_error,'/boolean':boolean_based_size} 

# Start the server
print "\n"
print "bbqsql http server\n\n"
print "used to unit test boolean, blind, and error based sql injection"
print "use the following syntax: http://127.0.0.1:8090/time?row=1&character_index=1&character_value=95&comparator=>&sleep=1"
print "path can be set to /time,  /error, or /boolean"
print "\n"

wsgi.server(eventlet.listen(('', 8090)), parse_response)
