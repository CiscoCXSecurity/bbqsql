from gevent import http,sleep
from urlparse import urlparse,parse_qs


class VulnerableServer:
    def __init__(\
        self,\
        datas = ['Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris malesuada tincidunt volutpat. Vestibulum feugiat faucibus arcu a consequat.',\
                 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ultrices felis vehicula augue ornare facilisis. Integer vel ullamcorper orci. '],\
        messages = ["Doh","Hurray, you have discovered the truth, hence this excessivly long message that doesn't realy say much of any meaning or value."],\
        address = "127.0.0.1",\
        port = 1337):

        self.datas = datas
        self.messages = messages
        self.address = address
        self.port = port

        self.comparators = ['<','=','>','false']
    
        http.HTTPServer((self.address,self.port), self.callback).serve_forever() 

    def callback(self,request):
        ''' http://127.0.0.1:1337/size?row_index=0&char_index=0&test_char=97&cmp=1&sleep=1 '''
        try:
            #parse params from URI
            params = parse_qs(urlparse(request.uri).query)
            print params

            #pull out the values
            row_index = int(params['row_index'][0])
            char_index = int(params['char_index'][0]) - 1
            test_char = int(params['test_char'][0])
            print "test_char: %s" % chr(test_char)
            comparator = self.comparators.index(params['cmp'][0]) - 1
            
            #this is the character they are trying to guess at
            current_character = self.datas[row_index][char_index]
            print "current char: %s" % current_character
            
            #this True if their guess was correct
            truth = (cmp(ord(current_character),test_char) == comparator)
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
            request.send_reply(200, "OK", self.messages[truth])
            print "\n"

        except:
            #if they don't format their message correctly, we tell them so...
            request.add_output_header('Content-Type', 'text/html')
            request.send_reply(500, "Danger Will Robinson", 'you messed up')

    
if __name__ == "__main__":
    vs = VulnerableServer()
