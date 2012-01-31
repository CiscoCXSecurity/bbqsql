# file: truth.py

from .exceptions import *
from . import debug

from numpy import mean,std
from difflib import get_close_matches

class Truth(object):
    '''fancy object for establishing if an object is "True". This abstracts away some of
    the complicated decisions that can factor into the establishment of truth. its pretty deep'''

    def __init__(self, comparison_attr = None, acceptable_deviation = .6, trues = [], falses = []):
        '''
        :trues                  - a list of known true values
        :falses                 - a list of known false values
        :comparison_attr        - the attribute of the objects we are lookig at that will be used for determiniing truth
        :acceptable_deviation   - the extent to which we can deviate from absolute truth while still being consider true. The meaning of this will varry depending on what methods we are using for testing truth. it has no meaning in the Truth class, but it does in LooseTextTruth and LooseNumericTruth
        '''
        self.trues = trues
        self.falses = falses
        self.comparison_attr = comparison_attr
        self.acceptable_deviation = acceptable_deviation
    
    def add_true(self,obj):
        '''add a value to our list of known true values'''
        self.trues.append(self._get_value(obj))
    
    def add_false(self,obj):
        '''add a value to our list of known false values'''
        self.falses.append(self._get_value(obj))
    
    def test(self,obj):
        '''test if a value is true'''
        value = self._get_value(obj)
        return value in self.trues and value not in self.falses

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

    def test(self,obj):
        '''test a value'''

        value = self._get_value(obj)

        trues_mean  = mean(self.trues)
        falses_mean = mean(self.falses)

        tstd = std(self.trues)
        fstd = std(self.falses)

        #this isn't going to work well if we don't have data built up
        if not self.trues or not self.falses: 
            raise Exception('you need to add some true or false values before you start tying to test truth...')

        if falses_mean < trues_mean:
            if falses_mean + fstd >= trues_mean - tstd:
                raise TrueFalseRangeOverlap("truth and falsity overlap")
            
            middle = ((trues_mean - tstd) - (falses_mean + fstd)) / 2

            rval = value > middle

        else:
            if falses_mean - fstd <= trues_mean + tstd:
                raise TrueFalseRangeOverlap("truth and falsity overlap")
            
            middle = ((falses_mean + fstd) - (trues_mean - tstd)) / 2

            rval = value < middle

        [self.falses,self.trues][rval].append(value)

        #delete old trues / falses so we aren't doing all these heavy function calls on thousands of objects
        if len(self.trues) > 20:
            del(self.trues[0])

        if len(self.falses) > 20:
            del(self.falses[0])
        
        return rval



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
