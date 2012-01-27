from gevent import http,sleep
from urlparse import urlparse,parse_qs

datas = ['hello','world']
messages = ["Doh","Yay"]
address = "127.0.0.1"
comparators = ['<','=','>','false']
port = 1337

def callback(request):
    ''' http://127.0.0.1:1337/?row_index=0&char_index=0&test_char=97&cmp=1&sleep=1 '''
    try:
        #parse params from URI
        params = parse_qs(urlparse(request.uri).query)
        print params

        #pull out the values
        row_index = int(params['row_index'][0])
        char_index = int(params['char_index'][0]) - 1
        test_char = int(params['test_char'][0])
        print "test_char: %s" % chr(test_char)
        comparator = comparators.index(params['cmp'][0]) - 1
        
        #this is the character they are trying to guess at
        current_character = datas[row_index][char_index]
        print "current char: %s" % current_character
        
        #this True if their guess was correct
        truth = (cmp(test_char,ord(current_character)) == comparator)
        print "truth: %s" % str(truth)
        
        try:
            #if they give us a sleep param, then we sleep the sepcified amount
            sleep_time = float(params['sleep'][0]) * truth
            sleep(sleep_time)

        except KeyError:
            #its okay if they don't give us a sleep param
            pass

        #response with appropriate message based on whether thier guess was correct
        request.add_output_header('Content-Type', 'text/html')
        request.send_reply(200, "OK", messages[truth])
        print "\n"

    except:
        #if they don't format their message correctly, we tell them so...
        request.add_output_header('Content-Type', 'text/html')
        request.send_reply(500, "Danger Will Robinson", 'you messed up')

http.HTTPServer((address,port), callback).serve_forever()