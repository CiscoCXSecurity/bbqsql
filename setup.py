#!/usr/bin/env python

from setuptools import setup

setup(name='BBQSQL',
      version='1.2',
      license='BSD',
      author='Ben Toews (mastahyeti)',
      author_email='mastahyeti@gmail.com',
      description='Rapid Blind SQL Injection Exploitation Tool',
      url='http://github.com/neohapsis/bbqsql',
      packages=['bbqsql','bbqsql.lib','bbqsql.menu'],
      scripts=['scripts/bbqsql'],
      install_requires=['gevent','requests < 1.0','argparse']
     )
