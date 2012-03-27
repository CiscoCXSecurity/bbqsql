from bbqsql import Query
from urlparse import urlparse
import socket
import os

class ConfigError(Exception):
    '''Throw this exception when a method that hasn't been implemented gets called'''
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "You have a config error: " + self.value

def validate_ath(thing):
    if not (len(thing['value'])==2 and (type(thing['value'][0])==str or type(thing['value'][0])==Query) and (type(thing['value'][1])==str or type(thing['value'][1])==Query)):
        raise ConfigError("auth should be a tuple of two strings. Eg. ('username','password')")

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

def validate_data(thing):
    if type(thing['value']) == dict:
        for k in thing['value']:
            if (type(k) != str and type(k) != Query) or (type(thing["value"][k]) != str and type(thing["value"][k]) != Query):
                raise ConfigError('You provided your data as a dict. The keys and values need to be strings')

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

def validate_method(thing):
    if thing['value'].lower() not in ['get','options','head','post','put','patch','delete']:
        raise ConfigError("The valid options for method are: ['get','options','head','post','put','patch','delete']")

def validate_params(thing):
    if type(thing['value']) == dict:
        for k in thing['value']:
            if (type(k) != str and type(k) != Query) or (type(thing['value'][k]) != str and type(thing['value'][k]) != Query):
                raise ConfigError("You provided params as a dict. Keys are values for this dict must be strings.")

def validate_url(thing):
    parsed_url = urlparse(thing['value'])
    try:
        socket.gethostbyname(parsed_url.netloc)
    except socket.error:
        raise ConfigError('Invalid host name. Cannot resolve.')
    if parsed_url.scheme.lower() not in ['http','https']:
        raise ConfigError('Invalid url scheme. Only http and https')
    return thing

class RequestsConfig:
    config = {\
        'allow_redirects':\
            {'name':'allow_redirects',\
            'value':None,\
            'description':'',\
            'types':[bool],\
            'required':False,\
            'validator':None},\
        'auth':\
            {'name':'auth',\
            'value':None,\
            'description':'',\
            'types':[tuple],
            'required':False,\
            'validator':validate_ath},\
        'cookies':\
            {'name':'cookies',\
            'value':None,\
            'description':'',\
            'types':[dict,str],\
            'required':False,\
            'validator': validate_cookies},\
        'data':\
            {'name':'data',\
            'value':None,\
            'description':'',\
            'types':[dict,str,Query],\
            'required':False,\
            'validator': validate_data},\
        'files':\
            {'name':'files',\
            'value':None,\
            'description':'',\
            'types':[dict,str],\
            'required':False,\
            'validator': validate_files},\
        'headers':\
            {'name':'headers',\
            'value':None,\
            'description':'',\
            'types':[dict,str],\
            'required':False,\
            'validator': validate_headers},\
        'method':\
            {'name':'method',\
            'value':None,\
            'description':'',\
            'types':[str],\
            'required':True,\
            'validator':validate_method},\
        'params':\
            {'name':'params',\
            'value':None,\
            'description':'',\
            'types':[dict,str,Query],\
            'required':False,\
            'validator': validate_params},\
        'proxies':\
            {'name':'proxies',\
            'value':None,\
            'description':'',\
            'types':[dict],\
            'required':False,\
            'validator':None},\
        'url':\
            {'name':'url',\
            'value':None,\
            'description':'',\
            'types':[str,Query],\
            'required':True,\
            'validator':validate_url}}

    def validate(self,quiet=False):
        valid = True
        for key in self.config:
            if self.config[key]['value'] == None:
                if self.config[key]['required']:
                    valid = False
                    if not quiet: print "You must specify a value for '%s'" % key
            elif type(self.config[key]['value']) not in self.config[key]['types']:
                valid = False
                if not quiet: print "You gave a value of an illeage type for '%s'" % key
            elif self.config[key]['validator']:
                try:
                    self.config[key]['validator'](self.config[key])
                except ConfigError, err:
                    if not quiet: print err
                    valid = False
        
        return valid
    
    def get_config(self):
        # make sure we're on the up and up
        if not self.validate(): return False

        kwargs = {}
        for key in self.config:
            if self.config[key]['value'] != None and type(self.config[key]['value']) in self.config[key]['types'] and (self.config[key]['validator'] == None or self.config[key]['validator'](self.config[key]['value'])):
                kwargs[key] = self.config[key]['value']
        
        return kwargs
    
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