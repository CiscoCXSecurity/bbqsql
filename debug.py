import functools
DEBUG_FUNCTION_CALL = True
DEBUG_FUNCTION_RETURN = False
debug_markers = "##> "

def func(f):
	'''function debuger'''
	@functools.wraps(f)
	def w(*a, **k):
		if DEBUG_FUNCTION_CALL: _debug_function_calls(f,*a,**k)
		r = f(*a,**k)
		if DEBUG_FUNCTION_RETURN: _debug_function_return(f,r)
		return r
	return w

def _debug_function_calls(f,*a,**k):
	_print("Call to: %s\t" % f.__name__)
	_print("wiith args: %s\t" % str(a))
	_print("and kargs: %s" % str(k))

def _debug_function_return(f,r):
	_print("Returning from: %s\n\tWith rval: %s\n" % (f.__name__,str(r)))

def _print(s):
	print debug_markers + str(s)

@func
def _test(arg1,arg2,k="value"):
	print "foo: %s,%s,%s" % (arg1,arg2,k)
	return "foo: rval"

if __name__ == "__main__":
	'''testing'''
	print _test('myval1','myval2')