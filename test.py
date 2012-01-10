import unittest
import bbqsql
#We don't need all the output....
bbqsql.QUIET = True

class test_time_blind_technique(bbqsql.time_blind_technique):
    '''
    these aren't the droids you are looking for. this is for unit testing.
    for this to work, you have to have the accompanying test.coffee server running
    '''
    def __init__(self,make_request_func,sleep=.1):
        self.query_greater = bbqsql.query("[{foo:\"${user_query:unimportant'}\",row:${row_index:0},charpos:${char_index:0},charval:${char_val:65},sleep:${sleep:.1},cmp:\"gt\"}]")
        self.query_equal = bbqsql.query("[{foo:\"${user_query:unimportant'}\",row:${row_index:0},charpos:${char_index:0},charval:${char_val:65},sleep:${sleep:.1},cmp:\"eq\"}]")
        super(test_time_blind_technique,self).__init__(make_request_func,sleep=sleep)

class TestTimeTechnique(unittest.TestCase):
    def test_blind(self):
            url = 'http://127.0.0.1'
            port = '1337'
            query_injection_points = ['q']
            requester = bbqsql.get_http_requester(url=url,port=port,query_injection_points=query_injection_points)
            tech = test_time_blind_technique(make_request_func=requester.make_request,sleep=.05)
            results = tech.run('unimportant')
            self.assertEqual(results,['hello','world'])

class TestQuery(unittest.TestCase):
    def test_instantiate_without_options(self):
        query_string = "SELECT ${blah:default_blah}, ${foo:default_foo} from ${asdf:default_asdf}"
        q = bbqsql.query(query_string)
        s = q.render()
        should_be = "SELECT default_blah, default_foo from default_asdf"
        self.assertEqual(s,should_be)

    def test_instantiate_with_options(self):
        query_string = "SELECT ${blah}, ${foo} from ${asdf}"
        options = {'blah':'test_blah','foo':'test_foo','asdf':'test_asdf'}
        q = bbqsql.query(query_string,options)
        s = q.render()
        should_be = "SELECT test_blah, test_foo from test_asdf"
        self.assertEqual(s,should_be)

    def test_change_options(self):
        query_string = "SELECT ${blah:default_blah}, ${foo:default_foo} from ${asdf:default_asdf}"
        options = {'blah':'new_blah','foo':'new_foo','asdf':'new_asdf'}
        q = bbqsql.query(query_string)
        q.set_options(options)
        s = q.render()
        should_be = "SELECT new_blah, new_foo from new_asdf"
        self.assertEqual(s,should_be)



if __name__ == "__main__":
    unittest.main() 
