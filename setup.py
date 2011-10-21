#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='django-natourpress',
    version='0.0.1',
    description='Natourpress',
    author='Nando Quintana',
    author_email='email@nandoquintana.com',
    url='http://www.natouring.net/',
    packages=[
    'natourpress',
        ],
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Operating System :: OS Independent',
                'Programming Language :: Python',
                 'Topic :: Utilities'],
    )
