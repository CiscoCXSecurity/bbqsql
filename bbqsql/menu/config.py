import bbqsql
from bbqsql import Query

import bbqcore
from bbqcore import bcolors

try:
    import readline
except ImportError:
    pass

from urlparse import urlparse
from urllib import quote
import socket
import os
import text
import re

class ConfigError(Exception):
    '''Throw this exception when a method that hasn't been implemented gets called'''
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "You have a config error: " + self.value

def validate_allow_redirects(thing):
    if type(thing['value']) == str:
        if thing['value'].lower() == 'false':
            thing['value'] = False
        else:
            thing['value'] = True
    
    return True

def validate_ath(thing):
    if not (len(thing['value'])==2 and (type(thing['value'][0])==str or type(thing['value'][0])==Query) and (type(thing['value'][1])==str or type(thing['value'][1])==Query)):
        raise ConfigError("auth should be a tuple of two strings. Eg. ('username','password')")

    return True

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
        if (type(k) != str and type(k) != Query)  or (type(thing['value'][k]) != str and (thing['value'][k]) != Query):
            raise ConfigError("Keys and values for cookies need to be strings.")
    
    return True

def validate_headers(thing):
    if type(thing['value']) == str:
        try:
            parts = thing['value'].split(':')
            headers = {parts[0]:parts[1].strip()}
            thing['value'] = headers
        except:
            raise ConfigError("You provided your headers as a string. Thats okay, but it doesn't look like you formatted them properly")
    for k in thing['value']:
        if (type(k) != str and type(k) != Query)  or (type(thing['value'][k]) != str and (thing['value'][k]) != Query):
            raise ConfigError("Keys and values for headers need to be strings.")
    
    return True

def validate_data(thing):
    if type(thing['value']) == dict:
        for k in thing['value']:
            if (type(k) != str and type(k) != Query) or (type(thing["value"][k]) != str and type(thing["value"][k]) != Query):
                raise ConfigError('You provided your data as a dict. The keys and values need to be strings')
    
    return True

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

def validate_method(thing):
    if thing['value'].lower() not in ['get','options','head','post','put','patch','delete']:
        raise ConfigError("The valid options for method are: ['get','options','head','post','put','patch','delete']")

    return True

def validate_params(thing):
    if type(thing['value']) == dict:
        for k in thing['value']:
            if (type(k) != str and type(k) != Query) or (type(thing['value'][k]) != str and type(thing['value'][k]) != Query):
                raise ConfigError("You provided params as a dict. Keys are values for this dict must be strings.")
    
    return True

def validate_url(thing):

    parsed_url = urlparse(str(thing['value']))
    netloc = parsed_url.netloc.split(':')[0]
    try:
        socket.gethostbyname(netloc)
    except socket.error:
        raise ConfigError('Invalid host name. Cannot resolve.')
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
            'types':[dict,str,Query],\
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
            'value':'http://sqlivuln/index.php?username=user1&password=secret${injection}',\
            'description':'The URL that requests should be sent to.',\
            'types':[str,Query],\
            'required':True,\
            'validator':validate_url}}

    menu_text = "We need to determine what our HTTP request will look like. Bellow are the\navailable HTTP parameters. Please enter the number of the parameter you\nwould like to edit. When you are done setting up the HTTP parameters,\nyou can type 'done' to keep going.\n"

    def convert_to_query(self):
        '''Convert a string or dict to Query if it matches the necessary syntax.'''
        for key in self.config:
            thing = self.config[key]
            if type(thing['value']) == str and re.match(u'.*\$\{.+\}.*',thing['value']):
                thing['value'] = Query(thing['value'],encoder=quote)
            
            elif type(thing['value']) == dict:
                for key in thing['value']:
                    if type(key) == str and re.match(u'\$\{.+\}',key):
                        thing['value'][Query(key,encoder=quote)] = thing['value'][key]
                        del(thing['value'][key])
                    if type(thing['value'][key]) == str and re.match(u'\$\{.+\}',thing['value'][key]):
                        thing['value'][key] = Quote(thing['value'][key],encoder=quote)


    def validate(self,quiet=False):
        ''' Check if all the config parameters are properly set'''
        valid = True
        for key in self.config:
            # if there is not value and a value is required, we have a problem
            if self.config[key]['value'] == None:
                if self.config[key]['required']:
                    valid = False
                    if not quiet: print bcolors.RED + ("You must specify a value for '%s'" % key) + bcolors.ENDC
                
            # if we have an object of the wrong type, we have a problem
            elif type(self.config[key]['value']) not in self.config[key]['types']:
                valid = False
                if not quiet: print bcolors.RED + ("You gave a value of an illeage type for '%s'" % key )+ bcolors.ENDC
            
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
            if self.config[key]['value'] != None and type(self.config[key]['value']) in self.config[key]['types'] and (self.config[key]['validator'] == None or self.config[key]['validator'](self.config[key])):
                kwargs[key] = self.config[key]['value']
        
        return kwargs
    
    def run_config(self):
        '''run a configuration menu'''
        config_keys = self.config.keys()
        choice = ''
        while choice not in ['done','back','quit','exit',99,'99']:
            bbqcore.show_banner()
            http_main_menu = bbqcore.CreateMenu(self.menu_text, [])
            
            for ki in xrange(len(config_keys)):
                key = config_keys[ki]
                print "\t%d) %s" % (ki,key)
                if self[key]['value'] is not None:
                    print "\t   Value: %s" % self[key]['value']
            print "\n\t99) Go back to the main menu"
            print "\n"
            self.validate()

            #get input
            choice = (raw_input(bbqcore.setprompt("1", "")))
            #convert to int
            try:
                choice = int(choice)
            except ValueError:
                pass
            
            if choice in range(len(config_keys)):
                key = config_keys[choice]
                bbqcore.show_banner()
                print "Parameter    : %s" % key
                print "Value        : %s" % repr(self[key]['value'])
                print "Allowed types: %s" % repr([t.__name__ for t in self[key]['types']])
                print "Required     : %s" % repr(self[key]['required'])
                desc = self[key]['description'].split("\n")
                desc = "\n\t\t".join(desc)
                print "Description  : %s" % desc
                self.validate()
                print "\nPlease enter a new value for %s.\n" % key
                try:
                        value = raw_input('value: ')
                        try:
                            value = eval(value)
                        except:
                            pass
                        self[key]['value'] = value 
                except KeyboardInterrupt:
                    pass
            
        if choice in ['exit','quit']:
            bbqcore.ExitBBQ(0)
    
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
        if key not in self.config:
            raise KeyError
        return self.config[key]

    def __setitem__(self,key,val):
        if key not in self.config:
            raise KeyError
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


def validate_concurrency(thing):
    try:
        thing['value'] = int(thing['value'])
    except ValueError:
        raise ConfigError('You need to give a numeric value for concurrency')

    return True

def validate_comparison_attr(thing):
    if thing['value'] not in bbqsql.settings.response_attributes:
        raise ConfigError("You must choose a valid comparison_attr. Valid options include %s" % str(bbqsql.settings.response_attributes.keys()))
    
    return True

def validate_search_type(thing):
    if thing['value'] not in ['binary_search','frequency_search']:
        if 'binary' in thing['value']:
            thing['value'] = 'binary_search'
        elif 'frequency' in thing['value']:
            thing['value'] = 'frequency_search'
        else:
            raise ConfigError('You need to set search_type to either "binary_search" or "frequency_search"')
        
    return True

def validate_query(thing):
    if type(thing['value']) != Query:
        thing['value'] = Query(thing['value'])
    
    return True


class bbqsqlConfig(RequestsConfig):
    config = {\
        'concurrency':\
            {'name':'concurrency',\
            'value':150,\
            'description':'Controls the amount of concurrency to run the attack with. This is useful for throttling the requests',\
            'types':[str,int],\
            'required':True,\
            'validator':validate_concurrency},\
        'comparison_attr':\
            {'name':'comparison_attr',\
            'value':'size',\
            'description':"Which attribute of the http response bbqsql should look at to determine true/false. Valid options include %s" % str(bbqsql.settings.response_attributes.keys()),\
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
            'value':"' and ASCII(SUBSTR((SELECT data FROM data LIMIT 1 OFFSET ${row_index:1}),${char_index:1},1))${comparator:>}${char_val:0} #",\
            'description':text.query_text,\
            'types':[str,Query],\
            'required':True,\
            'validator':validate_query}}

    menu_text = "Please specify the following configuration parameters.\n"

    def _convert_to_query(self,thing):
        pass
