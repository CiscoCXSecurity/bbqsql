#file: exceptions.py

class NotImplemented(Exception):
    '''Throw this exception when a method that hasn't been implemented gets called'''
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "This isn't implemented yet: " + self.value

class TrueFalseRangeOverlap	(Exception):
    '''Throw this exception when the nature of truth comes into question'''
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "The nature of truth is no longer self-evident: " + self.value

class ValueDoesntMatchCase (Exception):
    '''Thrown by requester when a value we are testing for doesnt match any of our established cases'''
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "We have an outlier.... The value doesn't match any known case. Dunno what to do \0/: " + self.value

class SendRequestFailed (Exception):
    '''Throw this exception when a sending a request fails'''
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "Sending the request failed. Dunno why." + self.value

