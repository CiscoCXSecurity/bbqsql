from bbqsql import technique
from gevent import httplib
import gevent

class blind_technique(technique):
    '''
    This is a prototype for a blind sql injection technique. This isn't fully implemented
    because there are various types of blind sql injection. To implement this technique you 
    need to implement _is_greater, _is_equal, _make_base_request. 
    '''
    @debug.func
    def run(self,user_query):
        user_query = user_query
        try:
            self.base_response
        except AttributeError:
            self._make_base_request()
        results = []
        row_index = 0
        row = True
        #we get more rows until the table is over
        while row:
            #if this isnt the first iteration
            if row != True:
                results.append(row)
            row = self._get_next_row(row_index,user_query)
            row_index += 1
        return results

    @debug.func
    def _get_next_row(self,row_index,user_query):
        #finding a row
        row = ""
        char_index = 1
        char = True
        #we get more chars until the row is over
        while char:
            #if this isnt the first iteration
            if char != True:
                row += char
            char = self._get_next_char(char_index,row_index,user_query)
            char_index += 1
        if row != "":
            return row
        else:
            return False

    @debug.func
    def _get_next_char(self,char_index,row_index,user_query):
        #finding a character
        low = 0
        high = CHARSET_LEN
        while low < high:
            mid = (low+high)//2
            update_char(CHARSET[mid])
            if self._is_greater(row_index, char_index, CHARSET[mid],user_query):
                high = mid
            else:
                low = mid
        mid = (low+high)//2
        if low < CHARSET_LEN and self._is_equal(row_index, char_index, CHARSET[mid],user_query):
            update_char()
            return CHARSET[mid]
        else:
            end_line()
            return False


class get_http_requester_evented(requester):
    @debug.func
    def __init__(
        self,
        url,
        port=80,
        uri="/",
        uri_injection_points=[],
        query_string={},
        query_injection_points=[],
        headers={},
        headers_injection_points=[],
        data={},
        data_injection_points=[]):

        self.url = url
        self.port = port
        self.uri = uri
        self.uri_injection_points = uri_injection_points
        self.query_string = query_string
        self.query_injection_points = query_injection_points
        self.headers = headers
        self.headers_injection_points = headers_injection_points
        self.data = data
        self.data_injection_points = data_injection_points

        #make sure our URI starts with a /
        if uri[0] != '/': uri = "/" + uri
        
    @debug.func
    def make_request(self,value=""):
        '''
        This method makes the requests. By the time you are calling this, the class
        should already be set up. The value you provide to this method gets
        included into the part of the request that you set up during 
        instantiation. 
        '''
        #set up some vars
        uri = self.uri
        query_string = self.query_string.copy()
        headers = self.headers.copy()
        data = self.data.copy()
        #parse all of the injection points
        for r in self.uri_injection_points:
            uri.replace(r,urllib.urlencode(value))
        for r in self.query_injection_points:
            query_string[r] = query_string.get(r,"") + value
        for r in self.headers_injection_points:
            headers[r] = headers.get(r,"") + urllib.urlencode(value)
        for r in self.data_injection_points:
            data[r] = data.get(r,"") + value
        #build out a few things
        query_string = urllib.urlencode(query_string)
        data = urllib.urlencode(data)
        #construct out request_url
        request_url = self.url + ":" + str(self.port) + uri + '?' + query_string
        #build a urllib2.Request object
        request = urllib2.Request(request_url,headers=headers,data=data)
        #prepare our variables for our response object
        time_start = time.time()
        raw_res = urllib2.urlopen(request)
        time_stop  = time.time()
        time_delta = time_stop - time_start
        data = raw_res.read()
        #create our response object
        res = http_response(data,time_delta)
        return res