import bbqsql
import unittest



#We don't need all the output....
bbqsql.QUIET = True

class TestBlindRequester(unittest.TestCase):
    def test_exploit(self):
        bh = bbqsql.BlindHTTP()
        results = bh.run(concurrency=10)
        self.assertEqual(results,['hello','world'])


if __name__ == "__main__":
    unittest.main() 
