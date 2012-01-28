#file: exceptions.py

class NotImplemented(Exception):
    '''Throw this exception when a method that hasn't been implemented gets called'''
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "This isn't implemented yet: " + self.value