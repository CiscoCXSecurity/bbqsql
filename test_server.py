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

datas = ['Strange women lying in ponds distributing swords is no basis for a system of government. Supreme executive power derives from a mandate from the masses, not from some farcical aquatic ceremony.', 'Three rings for the Elven kings under the sky, seven for the Dwarf lords in their halls of stone, nine for the mortal men doomed to die, one for the Dark Lord on his dark throne, in the land of Mordor where the shadows lie. One ring to rule them all, one ring to find them, one ring the bring them all, and in the darkness bind them. In the land of Mordor where the shadows lie.', 'Im sorry, Dave. Im afraid I cant do that.', 'Spock. This child is about to wipe out every living thing on Earth. Now, what do you suggest we do....spank it?', 'With great power there must also come -- great responsibility.', 'If you cant take a little bloody nose, maybe you oughtta go back home and crawl under your bed. Its not safe out here. Its wondrous, with treasures to satiate desires both subtle and gross; but its not for the timid.', 'Five card stud, nothing wild. And the skys the limit', 'If you think that by threatening me you can get me to do what you want... Well, thats where youre right. But -- and I am only saying that because I care -- theres a lot of decaffeinated brands on the market that are just as tasty as the real thing.', 'Were all very different people. Were not Watusi. Were not Spartans. Were Americans, with a capital A, huh? You know what that means? Do ya? That means that our forefathers were kicked out of every decent country in the world. We are the wretched refuse. Were the underdog.', 'If Im not back in five minutes, just wait longer.', 'Im going to give you a little advice. Theres a force in the universe that makes things happen. And all you have to do is get in touch with it, stop thinking, let things happen, and be the ball.', 'WE APOLOGIZE FOR THE INCONVENIENCE', 'Some days, you just cant get rid of a bomb!', 'Bill, strange things are afoot at the Circle K.', 'Invention, my dear friends, is 93% perspiration, 6% electricity, 4% evaporation, and 2% butterscotch ripple.', 'Didja ever look at a dollar bill, man? Theres some spooky shit goin on there. And its green too.', 'Alright, alright alright.', 'Heya, Tom, its Bob from the office down the hall. Good to see you, buddy; howve you been? Things have been alright for me except that Im a zombie now. I really wish youd let us in.', 'Never argue with the data.', 'Oooh right, its actually quite a funny story once you get past all the tragic elements and the over-riding sense of doom.']

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
        sleep_int = float(params['sleep'].pop(0))

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
