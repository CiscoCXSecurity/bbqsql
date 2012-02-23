# file: truth.py

from .exceptions import *

from numpy import mean,std
from difflib import get_close_matches

class Truth(object):
    '''
    When doing a blind sql injection attack, you are generally doing a binary search. This involves sending queries to the 
    server that will either evaluate as being true or false. You then need to be able to determine in an automated fashion based
    on the response from the server wheather the request evaluated as true or false. This class helps with that. You can feed known
    true and false responses to this class, telling it what to look at when making its decision about truth (response size,
     response content...). Then when you send a real query to the server you are able to pass the response to your Truth object
     to determine if the response evaluated as true or false. 
    '''

    def __init__(self, comparison_attr = None, acceptable_deviation = .6):
        '''
        :comparison_attr        - the attribute of the objects we are lookig at that will be used for determiniing truth
        :acceptable_deviation   - the extent to which we can deviate from absolute truth while still being consider true. The meaning of this will varry depending on what methods we are using for testing truth. it has no meaning in the Truth class, but it does in LooseTextTruth and LooseNumericTruth
        '''
        self.cases = {\
            'true':{'return':True,'values':[]},\
            'false':{'return':False,'values':[]},\
            'error':{'return':False,'values':[]}}

        self.comparison_attr = comparison_attr
        self.acceptable_deviation = acceptable_deviation
    
    def add_case(self,name,return_value):
        '''
        to test truth, we need to establish what a true/false response looks like. A case is a set of responses associated 
        with the value we should return when we later see a response lik that. For example, we normally might have a true 
        case, a false case, and an error case. If we encounter the true case, we will return True, if false then False, if 
        error then False. It is also possible to add other cases. For example, there might be multiple types of responses that
        we want to return True for. If so, you would want to call add_case to add another case that returns True.
        '''                
        self.cases[name] = {'return':return_value,values:[]}

    def add_value(self,case,obj):
        '''
        In testing truth, we need something to compare a test value against. With this method you add a value of a known type 
        to a case. For example the use would probably want to add some known true and known false values to the true and false 
        cases before attempting a blind sql injection attack
        '''
        self.cases[case]['values'].append(self._get_value(obj))

        # don't want to fill up memory. clean up after ourselves.
        if len(self.cases[case]['values']) > 10:
            del(self.cases[case]['values'][0])
        
    def add_true(self,obj):
        '''
        This is a helper function for adding to the true case. It just called self.add_value('true',obj)
        '''
        self.add_value('true',obj)

    def add_false(self,obj):
        '''
        This is a helper function for adding to the true case. It just called self.add_value('false',obj)
        '''
        self.add_value('false',obj)

    def add_error(self,obj):
        '''
        This is a helper function for adding to the true case. It just called self.add_value('error',obj)
        '''
        self.add_value('error',obj)
    
    def test(self,obj):
        '''test if a value is true'''
        value = self._get_value(obj)
        for case in self.cases:
            if value in self.cases[case]['values']:
                return self.cases[case]['return']

    def _get_value(self,obj):
        '''extract the value from the object as specified by comparison_attr'''
        if self.comparison_attr:
            return getattr(obj,self.comparison_attr)
        else:
            return obj


class LooseNumericTruth(Truth):
    '''test a numeric variable matches our preconceived notions of truth. 
    this will allow for some flexibility in determiniing this as determined by 
    acceptable_deviation'''

    def add_value(self,case,obj):
        '''overwrite the parent and keep track of mean and standard deviation'''
        #call the parent class
        super(LooseNumericTruth,self).add_value(case,obj)

        m = mean(self.cases[case]['values'])
        s = std(self.cases[case]['values']) * self.acceptable_deviation
        self.cases[case]['stddev'] = s

        self.cases[case]['low'] = m - s
        self.cases[case]['middle'] = m
        self.cases[case]['high'] = m + s

        #print "case: %s\t %d,%d,%d" % (case,self.cases[case]['low'],self.cases[case]['middle'],self.cases[case]['high'])

        self.__check_for_overlaps__()

    def __check_for_overlaps__(self):
        '''make sure that cases aren't overlapping'''
        for outer in self.cases:
            # if middle isn't set that means that the case doesn't have any values and we cant check it really for overlaps...
            if 'middle' in self.cases[outer]:
                for inner in self.cases:
                    #if the return vals are the same, it doesn't really matter if they blend together.
                    if 'middle' in self.cases[inner] and self.cases[inner]['return'] != self.cases[outer]['return']:
                        if self.cases[outer]['middle'] >= self.cases[inner]['middle'] and self.cases[outer]['low'] < self.cases[inner]['high']:
                            raise TrueFalseRangeOverlap("truth and falsity overlap")
                        elif self.cases[outer]['middle'] <= self.cases[inner]['middle'] and self.cases[outer]['high'] > self.cases[inner]['low']:
                            raise TrueFalseRangeOverlap("truth and falsity overlap")

    def get_standard_dev(self,case):
        if 'stddev' in self.cases[case]:
            return self.cases[case]['stddev']
        else: return None

    def test(self,obj):
        '''test a value'''
        value = self._get_value(obj)

        for k in self.cases:
            if value >= self.cases[k]['low'] and value <= self.cases[k]['high']:
                self.add_value(k,obj)
                return self.cases[k]['return']


class LooseTextTruth(Truth):
    '''test a string variable matches our preconceived notions of truth. 
    this will allow for some flexibility in determiniing this as determined by 
    acceptable_deviation'''

    def __init__(self,close_matches_function = get_close_matches, *args, **kwargs):
        '''
        :close_matches_function     - this is a callback that establishes if the first arg is similar to any elements from the list in the second arg.
        '''
        
        self.close_matches_function = close_matches_function
        super(LooseTextTruth,self).__init__(*args,**kwargs)

    def test(self,obj):
        '''test a value'''

        t = False

        value = self._get_value(obj) 
        
        #this isn't going to work well if we don't have data built up
        if not self.trues and not self.falses: 
            raise Exception('you need to add some true or false values before you start tying to test truth...')

        #if our value matches somethings from our list of true values, we go with True
        if self.trues and self.close_matches_function(value,self.trues,n=1,cutoff=self.acceptable_deviation): 
            t = True 

        #if our value matches something from our list of false values, we stick with False
        #if we already selected True, then we probably have a problem and should freak out.
        if self.falses and self.close_matches_function(value,self.falses,n=1,cutoff=self.acceptable_deviation) and t: 
            raise TrueFalseRangeOverlap('the value matches both true and false cases... truth is meaningless')
        
        #keep out history to improve our accuracy
        if t: 
            self.trues.append(value)
        else: 
            self.falses.append(value)
        
        #delete old trues / falses so we aren't doing all these heavy function calls on thousands of objects
        if len(self.trues) > 20:
            del(self.trues[0])

        if len(self.falses) > 20:
            del(self.falses[0])

        return t       
