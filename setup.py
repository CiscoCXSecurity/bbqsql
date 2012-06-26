#!/usr/bin/env python

from distutils.core import setup
import bbqsql

setup(name=bbqsql.__title__,
      version=bbqsql.__version__,
      license=bbqsql.__license__,
      author='Ben Toews (mastahyeti)',
      author_email='mastahyeti@gmail.com',
      description='SQL Injcetion Exploitation Tool',
      url='http://github.com/mastahyeti/bbqsql',
      packages=['bbqsql','bbqsql.lib','bbqsql.menu'],
      scripts=['scripts/bbqsql'],
      required=['gevent','requests<=0.11.0','numpy']
     )
