import unittest
import bbqsql
import requests
#We don't need all the output....
bbqsql.QUIET = True

class TestTimeTechnique(unittest.TestCase):
    def test_blind(self):
            url = bbqsql.Query('http://127.0.0.1:1337/q=${}')
            query = bbqsql.Query("[{foo:\"${user_query:unimportant'}\",row:${row_index:0},charpos:${char_index:0},charval:${char_val:65},sleep:${sleep:.1},comparator:\"=\"}]")

            #build a requests.Session object to hold settings
            session = requests.Session(return_response=False)
            #build a request object (but don't send it)
            request = session.get(url)
            #build a bbqsql.Requester object 
            requester = bbqsql.Requester(request,)

            tech = BlindTechnique(make_request_func=requester.make_request,sleep=.05)
            results = tech.run('unimportant')
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
