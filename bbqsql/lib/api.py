from .query import Query
from .pretty_print import PrettyTable
from .technique import BooleanBlindTechnique
import settings

from urllib import quote
from traceback import print_exc

__all__ = ['Query','BooleanBlindSQLi']

class BooleanBlindSQLi:
    def __init__(self,\
            query               = Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}&sleep=${sleep:0}&foo=${user_query:unimportant}",encoder=quote),\
            comparison_attr     = "size",*args,**kwargs):

        # Error handling... YAY \0/
        if type(query) != Query:
            print "Query object must be sent to bbqSQL. I received a %s" % str(type(query))
            exit()
        try:
            requester_type = settings.response_attributes[comparison_attr]
        except KeyError:
            print "You tried to use a comparison_attr that isn't supported. Check the docs for a list"
            exit()
        self.query = query

        #build a Requester object. You can pass this any args that you would pass to requests.Request
        self.requester = requester_type(comparison_attr=comparison_attr, *args, **kwargs)

        #the queries default options should evaluate to True in whatever application we are testing. If we flip the comparator it should evauluate to false. 
        #here, we figure out what the opposite comparator is.
        opp_cmp = settings.OPPOSITE_COMPARATORS[query.get_option('comparator')]

        #setup some base values
        #true
        for i in xrange(settings.TRUTH_BASE_REQUESTS):
            self.requester.make_request(value=query.render(),case='true',rval=True)

        #false
        self.query.set_option('comparator',opp_cmp)
        for i in xrange(settings.TRUTH_BASE_REQUESTS):
            self.requester.make_request(value=query.render(),case='false',rval=False)

        #error
        self.query.set_option('char_index','1000')
        for i in xrange(settings.TRUTH_BASE_REQUESTS):
            self.requester.make_request(value=query.render(),case='error',rval=False)

        if not settings.QUIET: print "done setting up BooleanBlindSQLi"

    def run(self,query='SELECT user()',sleep=0,concurrency=50):     
        #build our technique
        tech = BooleanBlindTechnique(requester=self.requester,query=self.query)
        
        if settings.PRETTY_PRINT and not settings.QUIET:
            #setup a PrettyTable for curses like printing
            pretty_table = PrettyTable(get_table_callback=tech.get_results,get_status_callback=tech.get_status,update=settings.PRETTY_PRINT_FREQUENCY)
        
        #run our technique
        techgl = tech.run( user_query = query ,sleep = sleep,concurrency = concurrency,row_len=5)

        if settings.PRETTY_PRINT and not settings.QUIET:
            #start printing the tables
            pretty_table.start()

        #wait for the technique to finish
        techgl.join()

        if settings.PRETTY_PRINT and not settings.QUIET:
            #kill the pretty tables
            pretty_table.die()
        
        results = tech.get_results()

        if not settings.QUIET and not settings.PRETTY_PRINT:
            print results

        return results 