#!/usr/bin/env python

from distutils.core import setup

classifiers = [    
    'Development Status :: 2 - Pre-Alpha',    
    'Intended Audience :: Developers',    
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX',    
    'Programming Language :: Python',    
    'Topic :: System :: Systems Administration :: Authentication/Directory']


setup(name='django-aadhaar',
      version='0.1.0',
      description='Django package for aadhaar authentication',
      author='Venkata Pingali',
      author_email='pingali@gmail.com',
      url='http://www.github.com/pingali/django-aadhaar',
      packages=['django_aadhaar'],
      scripts=[],
      license='LICENSE.txt',
      long_description=open('README.md').read(),
      classifiers=classifiers, 
      requires=['lxml', 'config', 'M2Crypto', 'requests', 'config',
                'pyxmlsec' ]
     )

