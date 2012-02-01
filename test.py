import bbqsql

import unittest
import requests
from urllib import quote
from time import time


#We don't need all the output....
bbqsql.QUIET = True

def my_sender(request):
    #we need a single function that can send requests
    if request.send():
        return request.response
    else:
        raise 

def pre_hook(request):
    #hooks for the requests module
    request.start_time = time()
    return request

def post_hook(request):
    #hooks for the requests module
    request.response.response_time = time() - request.start_time
    return request


'''class TestBlindRequester(unittest.TestCase):
    def test_exploit(self):
        url = bbqsql.Query('http://127.0.0.1:1337/?${query}')
        query = bbqsql.Query("foo=${user_query:unimportant}&row_index=${row_index:1}&char_index=${char_index:0}&test_char=${char_val:0}&cmp=${comparator:>}&sleep=${sleep:.5}",encoder=quote)
        session = requests.Session()
        request = session.get(url,return_response=False,hooks = {'pre_request':pre_hook,'post_request':post_hook})
        requester = bbqsql.Requester(request = request, send_request_function = my_sender)

        mytruth = bbqsql.LooseNumericTruth(comparison_attr = "response_time")
        for i in xrange(5):
            mytruth.add_true((requester.make_request(query.render())))
        query.set_option('comparator','<')
        for i in xrange(5):
            mytruth.add_false((requester.make_request(query.render())))

        tech = bbqsql.BlindTechnique(make_request_func=requester.make_request,query=query,concurrency=1, truth=mytruth)
        results = tech.run('SELECT data from example',sleep=.5)

        self.assertEqual(results,['hello','world'])


class TestBlindHTTPRequester(unittest.TestCase):
    def test_exploit(self):
        url = bbqsql.Query('http://127.0.0.1:1337/?${query}')
        query = bbqsql.Query("foo=${user_query:unimportant}&row_index=${row_index:0}&char_index=${char_index:0}&test_char=${char_val:0}&cmp=${comparator:>}&sleep=${sleep:.5}",encoder=quote)

        #build a bbqsql.Requester object 
        requester = bbqsql.HTTPRequester(url = url)

        mytruth = bbqsql.LooseNumericTruth(comparison_attr = "response_time")
        for i in xrange(5):
            mytruth.add_true((requester.make_request(query.render())))
        query.set_option('comparator','<')
        for i in xrange(5):
            mytruth.add_false((requester.make_request(query.render())))

        tech = bbqsql.BlindTechnique(make_request_func=requester.make_request,query=query,concurrency=1, truth = mytruth)
        results = tech.run('unimportant',sleep=.5)

        self.assertEqual(results,['hello','world'])'''


class TestHTTPBlind(unittest.TestCase):    
    def test_exploit(self):
        bh = bbqsql.BlindHTTP(\
            method  = 'GET',\
            url     = bbqsql.Query('http://127.0.0.1:1337/?${query}'),\
            query   = bbqsql.Query("foo=${user_query:unimportant}&row_index=${row_index:1}&char_index=${char_index:0}&test_char=${char_val:0}&cmp=${comparator:>}&sleep=${sleep:0}",encoder=quote),\
            comparison_attr     = "size")

        results = bh.run()
        self.assertEqual(results,['hello','world'])


class TestQuery(unittest.TestCase):
    def test_query_without_options(self):
        query_string = "SELECT ${blah:default_blah}, ${foo:default_foo} from ${asdf:default_asdf}"
        q = bbqsql.Query(query_string)
        s = q.render()
        should_be = "SELECT default_blah, default_foo from default_asdf"
        self.assertEqual(s,should_be)

    def test_query_with_options(self):
        query_string = "SELECT ${blah}, ${foo} from ${asdf}"
        options = {'blah':'test_blah','foo':'test_foo','asdf':'test_asdf'}
        q = bbqsql.Query(query_string,options)
        s = q.render()
        should_be = "SELECT test_blah, test_foo from test_asdf"
        self.assertEqual(s,should_be)

    def test_change_options(self):
        query_string = "SELECT ${blah:default_blah}, ${foo:default_foo} from ${asdf:default_asdf}"
        options = {'blah':'new_blah','foo':'new_foo','asdf':'new_asdf'}
        q = bbqsql.Query(query_string)
        q.set_options(options)
        s = q.render()
        should_be = "SELECT new_blah, new_foo from new_asdf"
        self.assertEqual(s,should_be)

if __name__ == "__main__":
    unittest.main() 
