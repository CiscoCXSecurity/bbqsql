import bbqsql
import unittest
import requests
from urllib import quote
from time import time
#We don't need all the output....
bbqsql.QUIET = True

def loose_time_cmp(x,y):
    #times will never match up exactly, so we fudge it a bit
    x = x.response_time
    y = y.response_time
    if abs(x - y) / ((float(x)+y)/2) < 1:
        return 0
    if x > y:
        return 1
    return -1

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


class TestTimeBlindTechniqueRequester(unittest.TestCase):
    def test_blind(self):
        url = bbqsql.Query('http://127.0.0.1:1337/?${query}')
        query = bbqsql.Query("foo=${user_query:unimportant}&row_index=${row_index:0}&char_index=${char_index:0}&test_char=${char_val:65}&cmp=${comparator:false}&sleep=${sleep:1}",encoder=quote)

        #build a requests.Session object to hold settings
        session = requests.Session()
        #build a request object (but don't send it)
        request = session.get(url,return_response=False,hooks = {'pre_request':pre_hook,'post_request':post_hook})
        #build a bbqsql.Requester object 
        requester = bbqsql.Requester(request = request, send_request_function = my_sender, response_cmp_function = loose_time_cmp)

        tech = bbqsql.BlindTechnique(make_request_func=requester.make_request,query=query,concurrency=1)
        results = tech.run('unimportant',sleep=.1)

        self.assertEqual(results,['hello','world'])


class TestTimeBlindTechniqueHTTPRequester(unittest.TestCase):
    def test_content_based(self):
        url = bbqsql.Query('http://127.0.0.1:1337/?${query}')
        query = bbqsql.Query("foo=${user_query:unimportant}&row_index=${row_index:0}&char_index=${char_index:0}&test_char=${char_val:65}&cmp=${comparator:false}&sleep=${sleep:1}",encoder=quote)

        #build a bbqsql.Requester object 
        requester = bbqsql.HTTPRequester(url = url , response_cmp_attribute = "content")

        tech = bbqsql.BlindTechnique(make_request_func=requester.make_request,query=query,concurrency=1)
        results = tech.run('unimportant',sleep=.1)

        self.assertEqual(results,['hello','world'])

    def test_time_based(self):
        url = bbqsql.Query('http://127.0.0.1:1337/?${query}')
        query = bbqsql.Query("foo=${user_query:unimportant}&row_index=${row_index:0}&char_index=${char_index:0}&test_char=${char_val:65}&cmp=${comparator:false}&sleep=${sleep:1}",encoder=quote)

        #build a bbqsql.Requester object 
        requester = bbqsql.HTTPRequester(url = url , response_cmp_attribute = "response_time")

        tech = bbqsql.BlindTechnique(make_request_func=requester.make_request,query=query,concurrency=1)
        results = tech.run('unimportant',sleep=.1)

        self.assertEqual(results,['hello','world'])


class TestQuery(unittest.TestCase):
    def test_instantiate_without_options(self):
        query_string = "SELECT ${blah:default_blah}, ${foo:default_foo} from ${asdf:default_asdf}"
        q = bbqsql.Query(query_string)
        s = q.render()
        should_be = "SELECT default_blah, default_foo from default_asdf"
        self.assertEqual(s,should_be)

    def test_instantiate_with_options(self):
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
