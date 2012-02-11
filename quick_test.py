from bbqsql.exploits import BlindHTTP
from time import time,sleep
from numpy import mean

times = {}


def mi():
	m = False
	for c in times:
		if (not m) or times[c] < m:
			m = times[c]
	return c

bh = BlindHTTP()

for i in range(1,200):
	start = time()
	results = bh.run(concurrency=i)
	print results
	t = time() - start
	times[i] = t

	print "concurrency	: %d" % i
	print "time 		: %f" % t
	print "min			: %d\n" % mi()



print "min		: %d" % mi()
print "time 	: %f" % times[mi()]




