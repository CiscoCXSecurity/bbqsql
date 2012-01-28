#file: response.py

from . import debug

class Response(object):
    '''
    This object wraps the requests type of your choosing, altering the
    comparison methods to better suite your needs.
    '''
    @debug.func
    def __init__( self , response , cmp_function = cmp ):
        self.response = response
        self.cmp_function = cmp_function
    def __gt__( self , y ):
        return self.cmp_function(self.response,y.response) > 0
    def __lt__( self , y ):
        return self.cmp_function(self.response,y.response) < 0
    def __eq__( self , y ):
        return self.cmp_function(self.response,y.response) == 0
    def __ne__( self , y ):
        return self.cmp_function(self.response,y.response) != 0