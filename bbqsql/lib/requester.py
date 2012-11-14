from .query import Query

from bbqsql import utilities
from bbqsql import settings

import requests
import gevent 

from math import sqrt
from copy import copy
from time import time
from difflib import SequenceMatcher

__all__ = ['Requester','LooseNumericRequester','LooseTextRequester']

@utilities.debug 
def requests_pre_hook(request):
    #hooks for the requests module to add some attributes
    request.start_time = time()
    return request

@utilities.debug 
def requests_response_hook(response):
    #hooks for the requests module to add some attributes
    response.time = time() - response.request.start_time
    if hasattr(response.content,'__len__'): 
        response.size = len(response.content)
    else: 
        response.size = 0
    return response

class EasyMath():
    def mean(self,number_list):
        if len(number_list) == 0:
            return float('nan')

        floatNums = [float(x) for x in number_list]
        means = sum(floatNums) / len(number_list)
        return means

    def stdv(self,number_list,means):
        size = len(number_list)
        std = sqrt(sum((x-means)**2 for x in number_list) / size)
        return std

class Requester(object):
    '''
    This is the base requester. Initialize it with request parameters (url,method,cookies,data) and a 
    comparison_attribute (size,text,time) which is used for comparing multiple requests. One of the 
    request parameters should be a Query object. Call the make_request function with a value. That value
    will be compiled/rendered into the query object in the request, the request will be sent, and the response
    will be analyzed to see if the query evaluated as true or not. This base class compares strictly (if we are looking
    at size, sizes between requests must be identical for them to be seen as the same). Override _test to change this
    behavior.
    '''

    def __init__( self,comparison_attr = "size" , acceptable_deviation = .6, *args,**kwargs):
        '''
        :comparison_attr        - the attribute of the objects we are lookig at that will be used for determiniing truth
        :acceptable_deviation   - the extent to which we can deviate from absolute truth while still being consider true. The meaning of this will varry depending on what methods we are using for testing truth. it has no meaning in the Truth class, but it does in LooseTextTruth and LooseNumericTruth
        '''
        #Truth related stuff
        self.cases = {}

        self.comparison_attr = comparison_attr
        self.acceptable_deviation = acceptable_deviation

        # make sure the hooks are lists, not just methods
        kwargs.setdefault('hooks',{})

        for key in ['pre_request','response']:
            kwargs['hooks'].setdefault(key,[])

            if hasattr(kwargs['hooks'][key],'__call__'):
                kwargs['hooks'][key] = [kwargs['hooks'][key]]

        kwargs['hooks']['pre_request'].append(requests_pre_hook)

        kwargs['hooks']['response'].append(requests_response_hook)

        #
        # moving things to a session for performance (reduce dns lookups)
        #

        self.request_kwargs = {}

        #pull out any other Query objects
        self.query_objects = {}
        for elt in [q for q in kwargs if isinstance(kwargs[q],Query)]:
            self.request_kwargs[elt] = kwargs[elt]
            del(kwargs[elt])

        # pull out the url, method and data
        if 'method' in kwargs:
            self.request_kwargs['method'] = kwargs['method']
            del(kwargs['method'])
        if 'url' in kwargs:
            self.request_kwargs['url'] = kwargs['url']
            del(kwargs['url'])
        if 'data' in kwargs:
            self.request_kwargs['data'] = kwargs['data']
            del(kwargs['data'])

        # all the same prep stuff that grequests.patched does
        # self.request_kwargs['return_response'] = False
        self.request_kwargs['prefetch'] = True

        config = kwargs.get('config', {})
        config.update(safe_mode=True)

        kwargs['config'] = config

        self.session = requests.session(*args,**kwargs)
    
    @utilities.debug 
    def make_request(self,value="",case=None,rval=None,debug=False):
        '''
        Make a request. The value specified will be compiled/rendered into all Query objects in the
        request. If case and rval are specified the response will be appended to the list of values 
        for the specified case. if return_case is True then we return the case rather than the rval.
        this is only really used for recursing by _test in the case of an error. Depth keeps track of 
        recursion depth when we make multiple requests after a failure. 
        '''

        new_request_kwargs = copy(self.request_kwargs)

        # keep track of which keys were dynamic so we know which ones to print after we make the request.
        # we do this so hooks can process the requests before we print them for debugging...
        keys_to_debug = []

        #iterate over the request_kwargs and compile any elements that are query objects.
        for k in [e for e in new_request_kwargs if isinstance(new_request_kwargs[e],Query)]:
            opts = new_request_kwargs[k].get_options()
            for opt in opts:
                opts[opt] = value
            new_request_kwargs[k].set_options(opts)
            new_request_kwargs[k] = new_request_kwargs[k].render()

            keys_to_debug.append(k)

        response = self.session.request(**new_request_kwargs)

        if debug:
            for k in keys_to_debug:
                print "Injecting into '%s' parameter" % k
                print "It looks like this: %s" % getattr(response.request,k)

        #glet = grequests.send(new_request)
        #glet.join()
        #if not glet.get() and type(new_request.response.error) is requests.exceptions.ConnectionError:
        #    raise utilities.SendRequestFailed("looks like you have a problem")

        #see if the response was 'true'
        if case is None:
            case = self._test(response)
            rval = self.cases[case]['rval']

        if debug and case:
            print "we will be treating this as a '%s' response" % case
            print "for the sample requests, the response's '%s' were the following :\n\t%s" % (self.comparison_attr,self.cases[case]['values'])
            print "\n"


        self._process_response(case,rval,response)

        return self.cases[case]['rval']

    @utilities.debug 
    def _process_response(self,case,rval,response):
        self.cases.setdefault(case,{'values':[],'rval':rval})

        #get the value from the response
        value = getattr(response,self.comparison_attr)

        #store value
        self.cases[case]['values'].append(value)

        #garbage collection
        if len(self.cases[case]['values']) > 10:
            del(self.cases[case]['values'][0])      

    def _test(self,response):
        '''test if a value is true'''
        value = getattr(response,self.comparison_attr)
        for case in self.cases:
            if value in self.cases[case]['values']:
                return case

class LooseNumericRequester(Requester):
    def _process_response(self,case,rval,response):
        self.cases.setdefault(case,{'values':[],'rval':rval,'case':case})

        #get the value from the response
        value = getattr(response,self.comparison_attr)

        #store value
        self.cases[case]['values'].append(value)

        #garbage collection
        if len(self.cases[case]['values']) > 10:
            del(self.cases[case]['values'][0])

        #statistics :D
        math = EasyMath()
        m = math.mean(self.cases[case]['values'])
        s = math.stdv(self.cases[case]['values'], m)

        self.cases[case]['mean'] = m
        self.cases[case]['stddev'] = s

        self._check_for_overlaps()

    def _check_for_overlaps(self):
        '''make sure that cases with different rvals aren't overlapping'''
        for outer in self.cases:
            for inner in self.cases:
                #if the return vals are the same, it doesn't really matter if they blend together.
                if self.cases[inner]['rval'] != self.cases[outer]['rval']:
                    math = EasyMath()
                    mean_stddev = math.mean([self.cases[inner]['stddev'],self.cases[outer]['stddev']])
                    diff = abs(self.cases[inner]['mean'] - self.cases[outer]['mean'])
                    if diff <= mean_stddev*2: 
                        raise utilities.TrueFalseRangeOverlap("truth and falsity overlap")

    def _test(self,response):
        '''test a value'''
        #make an ordered list of cases
        ordered_cases = []
        for case in self.cases:
            if len(ordered_cases) == 0:
                ordered_cases.append(self.cases[case])
            else:
                broke = False
                for index in xrange(len(ordered_cases)):
                    if self.cases[case]['mean'] <= ordered_cases[index]['mean']:
                        ordered_cases.insert(index,self.cases[case])
                        broke = True
                        break
                if not broke:
                    ordered_cases.append(self.cases[case])

        value = getattr(response,self.comparison_attr)

        #figure out which case best fits our value
        for index in xrange(len(ordered_cases)):
            lower_avg = None
            upper_avg = None
            math = EasyMath()
            if index != 0:
                lower_avg = math.mean([ordered_cases[index-1]['mean'],ordered_cases[index]['mean']])

            if index != len(ordered_cases) - 1:
                upper_avg = math.mean([ordered_cases[index]['mean'],ordered_cases[index+1]['mean']])

            if not lower_avg and value <= upper_avg:
                return ordered_cases[index]['case']

            elif not upper_avg and value >= lower_avg:
                return ordered_cases[index]['case']

            elif value >= lower_avg and value <= upper_avg:
                return ordered_cases[index]['case']

        #should never get here
        raise Exception('this is shit hitting the fan')


class LooseTextRequester(Requester):
    def _test(self,response):
        value = getattr(response,self.comparison_attr)

        max_ratio = (0,None)
        for case in self.cases:
            for case_value in self.cases[case]['values']:
                ratio = SequenceMatcher(a=str(value),b=str(case_value)).quick_ratio()
                if ratio > max_ratio[0]:
                    max_ratio = (ratio,case)

        return max_ratio[1]
