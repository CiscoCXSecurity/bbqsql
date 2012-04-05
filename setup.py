#!/usr/bin/env python

from distutils.core import setup

setup(name='bbqSQL',
      version='1.0',
      description='SQL Injcetion Exploitation Tool',
      author='Ben Toews (mastahyeti)',
      author_email='mastahyeti@gmail.com',
      url='http://github.com/mastahyeti/bbqsql',
      packages=['bbqsql','bbqsql.lib','bbqsql.menu']
     )

      #package_dir={'':'bbqsql'},
