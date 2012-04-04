#!/usr/bin/env python
# By Scott Behrens(arbit), 2012 

"""This is a simple webserver vulnerable to SQLi injection
make your query string look like this: http://127.0.0.1:8090/time?row_index=1&character_index=1&character_value=95&comparator=>&sleep=1

command line usage:
    python ./test_server.py [--rows=50 --cols=150]
        :rows   -   this controls how many rows of random data to use for the database
        :cols   -   this controls how many rows of random data to use for the database
"""

import eventlet 
from eventlet import wsgi
from eventlet.green import time
from urlparse import parse_qs
from random import random,choice

datas = ['hello','world']

# Different comparators BBsql uses
comparators = ['<','=','>','false']


def parse_response(env, start_response):
    '''Parse out all necessary information and determine if the query resulted in a match'''

    #add in some random delay
    delay = random()
    time.sleep(delay/10)

    try:
        params =  parse_qs(env['QUERY_STRING'])

        # Extract out all of the sqli information
        row_index =  int(params['row_index'][0])
        char_index = int(params['character_index'][0]) - 1
        test_char = int(params['character_value'][0])
        comparator = comparators.index(params['comparator'][0]) - 1
        try:
            sleep_int = float(params['sleep'].pop(0))
        except KeyError:
            sleep_int = 1

        # Determine which character position we are at during the injection
        current_character = datas[row_index][char_index]

        # figure out if it was true
        truth = (cmp(ord(current_character),test_char) == comparator)

        #some debugging
        #print "\n\n"
        #print "%d %s %d == %s" % (ord(current_character),params['comparator'][0],test_char,str(truth))
        #print "char_index       : %d" % char_index
        #print "row_index        : %d" % row_index

        # Call the function for what path was given based on the path provided
        response = types[env['PATH_INFO']](test_char, current_character, comparator, sleep_int, start_response,truth)

        return response
    except:
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])
        return ['error\r\n']


def time_based_blind(test_char, current_character, comparator, sleep_int, start_response,truth):
    # Snage the query string and parse it into a dict
    sleep_time = sleep_int * truth
    time.sleep(sleep_time)
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello!\r\n']


def boolean_based_error(test_char, current_character, comparator, env, start_response,truth):
    # Snage the query string and parse it into a dict
    if truth:
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Hello, im a bigger cheese in this cruel World!\r\n']
    else:
        start_response('404 File Not Found', [('Content-Type', 'text/plain')])
        return ['file not found: error\r\n']


def boolean_based_size(test_char, current_character, comparator, env, start_response,truth):
    # Snage the query string and parse it into a dict
    if truth:
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Hello, you just submitted a query and i found a match\r\n']
    else:
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Hello, no match!\r\n']
        
# Dict of the type's of tests, so pass your /path to execute that type of test
types = {'/time':time_based_blind,'/error':boolean_based_error,'/boolean':boolean_based_size} 

if __name__ == "__main__":
    # Start the server
    print "\n"
    print "bbqsql http server\n\n"
    print "used to unit test boolean, blind, and error based sql injection"
    print "use the following syntax: http://127.0.0.1:8090/time?row_index=1&character_index=1&character_value=95&comparator=>&sleep=1"
    print "path can be set to /time,  /error, or /boolean"
    print "\n"

    from sys import argv    
    import re

    CHARSET = [chr(x) for x in xrange(32,127)]

    rre = re.compile(u'--rows=[0-9]+')
    cre = re.compile(u'--cols=[0-9]+')
    rows = filter(rre.match,argv)
    cols = filter(cre.match,argv)

    if rows and cols:
        rows = rows[0]
        cols = cols[0]

        CHARSET = [chr(x) for x in xrange(32,127)]
        datas = []
        for asdf in range(5):
            datas.append("")
            for fdsa in range(100):
                datas[-1] += choice(CHARSET)

    wsgi.server(eventlet.listen(('', 8090)), parse_response)
