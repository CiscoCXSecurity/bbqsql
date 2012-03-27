from bbqsql import Query
from utils import validate_url

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
            'validator':lambda a:\
                len(a)==2 \
                and \
                    (type(a[0])==str\
                    or type(a[0])==Query)\
                and \
                    (type(a[1])==str\
                    or type(a[1])==Query)},\
        'cookies':\
            {'name':'cookies',\
            'value':None,\
            'description':'',\
            'types':[dict],\
            'required':False,\
            'validator': lambda c:not len(filter(lambda k:type(c[k]) != str and type(c[k]) != Query,c.keys()))},\
        'data':\
            {'name':'data',\
            'value':None,\
            'description':'',\
            'types':[dict,str,Query],\
            'required':False,\
            'validator': lambda d:\
                type(d) == str\
                or type(d) == Query\
                or type(d) == dict\
                    and not len(filter(lambda k:type(d[k]) != str and type(d[k]) != Query,d.keys()))},\
        'files':\
            {'name':'files',\
            'value':None,\
            'description':'',\
            'types':[dict],\
            'required':False,\
            'validator': lambda f:not len(filter(lambda k:type(f[k]) != file,f.keys()))},\
        'headers':\
            {'name':'headers',\
            'value':None,\
            'description':'',\
            'types':[dict],\
            'required':False,\
            'validator': lambda d:\
                type(d) == Query\
                or type(d) == dict\
                    and not len(filter(lambda k:type(d[k]) != str and type(d[k]) != Query,d.keys()))},\
        'method':\
            {'name':'method',\
            'value':None,\
            'description':'',\
            'types':[str],\
            'required':True,\
            'validator':lambda m: m.lower() in ['get','options','head','post','put','patch','delete']},\
        'params':\
            {'name':'params',\
            'value':None,\
            'description':'',\
            'types':[dict],\
            'required':False,\
            'validator': lambda d:\
                type(d) == Query\
                or type(d) == dict\
                    and not len(filter(lambda k:type(d[k]) != str and type(d[k]) != Query,d.keys()))},\
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
            elif self.config[key]['validator'] and not self.config[key]['validator'](self.config[key]['value']):
                valid = False
                if not quiet: print "You gave an invalid value for '%s'" % key
        
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