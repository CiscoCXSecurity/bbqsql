import bbqsql
import unittest
from urllib import quote


#We don't need all the output....
bbqsql.settings.PRETTY_PRINT = False
bbqsql.settings.QUIET = False
test_data = ['hello','world']

class TestBinaryTechnique(unittest.TestCase):
    def test_binary_technique(self):
        url     = bbqsql.Query('http://127.0.0.1:8090/boolean?${injection}')
        query   = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}",encoder=quote)
        b      = bbqsql.BlindSQLi(url=url,query=query,method='GET',comparison_attr='size',technique='binary_search',concurrency=10)
        results = b.run()
        self.assertEqual(results,test_data)

    def test_frequency_technique(self):
        url     = bbqsql.Query('http://127.0.0.1:8090/boolean?${injection}')
        query   = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}",encoder=quote)
        b      = bbqsql.BlindSQLi(url=url,query=query,method='GET',comparison_attr='size',technique='frequency_search',concurrency=5)
        results = b.run()
        self.assertEqual(results,test_data)

if __name__ == "__main__":
    unittest.main() 
