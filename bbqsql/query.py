# file: query.py

from . import debug

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
    def __init__(self,q_string,options=None,encoder=None):
        '''
        q_string syntax is "SELECT ${blah:default_blah}, ${foo:default_foo} from ${asdf:default_asdf}". 
        The options are specified in ${}, with the value before the ':' being the option name
        and the value after the ':' being the default value. 

        There is an optional options parameter that allows you to set the option values manually rather than
        having them be parsed.
        '''
        self.encoder = encoder
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
                if self.encoder != None:
                    val = self.encoder(val)
                output += val
                output += right
        return output