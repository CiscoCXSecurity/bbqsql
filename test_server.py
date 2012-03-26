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

#datas = ['5425898432159054', '5218507263228505', '5251118723758806', '5247650819191242', '5505704483934507', '5334191025185805', '5430440137532294', '5444125953112503', '5257793181821827', '5431847950669491', '5100592308057300', '5207592993974159', '5459516814673448', '5467415714549701', '5393307490846014', '5380202980380027', '5134275323582755', '5361701645879193', '5506062446970467', '5141500024199463', '5232273269753614', '5261858418311530', '5119620199373327', '5216413265447726', '5287686591945646', '5589961329246244', '5421228423573242', '5387548072039209', '5367248628712714', '5496174236139211', '5134278362168437', '5273449783512203', '5174776768770038', '5257419055937248', '5186976651488518', '5253381200933221', '5380621562741100', '5100132572901246', '5229913059537439', '5403984780502677', '5131228890285941', '5337275304520274', '5497168260881747', '5549882936019791', '5249852937553877', '5422195163770495', '5489388496260413', '5293273202844393', '5587988637232428', '5110906647841216', '4556799157052785', '4716386506065499', '4532478009657120', '4916012134409366', '4486944450114123', '4916449956346914', '4556056101047217', '4977651658694402', '4539208229592556', '4486431185019199', '4716144954882711', '4486283990774678', '4916156826747706', '4539014567823862', '4539352101859293', '4556327707118599', '4916709285133907', '4716456101246818', '4024007165998948', '4716237928442560', '4486826692350542', '4024007116659649', '4024007140991703', '4916208954597831', '4539984586447606', '4929592681391187', '4916847261798820', '4532184228484383', '4486566800809142', '4532068880432667', '4929648995295199', '4532402303141839', '4716959387810009', '4486086083609192', '4539797196980174', '4024007165756114', '4024007141378421', '4532560732276706', '4486755656021726', '4929593063431211', '4024007137035092', '4907527529030338', '4532857296997473', '4929148515349675', '4729697144144099', '4265047950501232', '4539315596051080', '4929843634859881', '4532486978612570', '4486939691046555', '4532594749242', '4539018579618', '4716766155144', '4532513921898', '4532634154437', '4916331840978', '4360424225989', '4532142488517', '4539182348006', '4539931740834', '4486991941557', '4007701797426', '4716931362872', '4916761511123', '4024007122332', '4539655937780', '4716422264702', '4486127075965', '4916033419626', '4916645778526', '4929300407174', '4532549880316', '4556356056538', '4929340879788', '4539057946553', '4929203606948', '4532967190271', '4929777241668', '4716496014645', '4486638206786', '4556528684001', '4024007147016', '4929145056251', '4539158513997', '4532797392121', '4024007105659', '4916533182922', '4486889111891', '4607050426301', '4917344716411', '4532137883474', '4916752586282', '4539804481466', '4539689706896', '4486574397474', '4556999870972', '4532665698252', '4929188644054', '4716653810868', '4024007104553', '345137702154596', '377489901137554', '342806978217070', '377484394700232', '348336638291632', '344300705542750', '343466516666103', '371770003031746', '371397153368387', '375195001716732', '378502545571274', '373130468992189', '344158180574270', '340560403202387', '340526522604043', '377131509882997', '370846352379711', '377423140327908', '348466873637122', '347810175922917', '377603794161642', '374016862859059', '340399443081554', '341774504744556', '377436170459318', '346897096676673', '374021748850207', '342090320636143', '371064288478263', '372442309573438', '346763062693565', '340142676481087', '341390747846189', '377519731793414', '347111515906516', '376110993456402', '378150950486339', '371795869068615', '379373872282011', '377731573711764', '372079465710105', '375394765027499', '371956027591993', '344922497067264', '371160588469505', '371024969690230', '371105215873579', '347784031612022', '344219597594317', '370161818572523']

#datas = ['def fix_location_header(request, response):', '    """', '    Ensures that we always use an absolute URI in any location header in the', '    response. This is required by RFC 2616, section 14.30.', '    Code constructing response objects is free to insert relative paths, as', '    this function converts them to absolute paths.', '    """', "    if 'Location' in response and request.get_host():", "        response['Location'] = request.build_absolute_uri(response['Location'])", '    return response', 'def conditional_content_removal(request, response):', '    """', '    Removes the content of responses for HEAD requests, 1xx, 204 and 304', '    responses. Ensures compliance with RFC 2616, section 4.3.', '    """', '    if 100 <= response.status_code < 200 or response.status_code in (204, 304):', "       response.content = ''", "       response['Content-Length'] = 0", "    if request.method == 'HEAD':", "        response.content = ''", '    return response', 'def fix_IE_for_attach(request, response):', '    """', '    This function will prevent Django from serving a Content-Disposition header', '    while expecting the browser to cache it (only when the browser is IE). This', '    leads to IE not allowing the client to download.', '    """', "    useragent = request.META.get('HTTP_USER_AGENT', '').upper()", "    if 'MSIE' not in useragent and 'CHROMEFRAME' not in useragent:", '        return response', "    offending_headers = ('no-cache', 'no-store')", "    if response.has_header('Content-Disposition'):", '        try:', "            del response['Pragma']", '        except KeyError:', '            pass', "        if response.has_header('Cache-Control'):", '            cache_control_values = [value.strip() for value in', "                    response['Cache-Control'].split(',')", '                    if value.strip().lower() not in offending_headers]', '            if not len(cache_control_values):', "                del response['Cache-Control']", '            else:', "                response['Cache-Control'] = ', '.join(cache_control_values)", '    return response']

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
