#!/usr/bin/env python
# -*- coding: utf-8 -*

from __future__ import absolute_import

from codecs import open
import os

from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()


setup(
    name='wikiapi',
    version='2.0.7',
    packages=find_packages('src', exclude=('tests',)),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    description=(
        "A basic python library enabling access to Wikipedia.org's "
        'search results and article content.'
    ),
    author="Richard O'Dwyer",
    author_email='richard@richard.do',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description='https://github.com/richardARPANET/wiki-api',
    install_requires=install_requires,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
