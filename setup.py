#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setuptools module for albt
"""
from setuptools import setup
import os

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'README.rst'))) as f:
    long_description = f.read()

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'VERSION'))) as version_file:
    version = version_file.read().strip()

setup(
    name='albt',
    version=version,
    url='https://github.com/geothird/albt',
    description='AWS Lambda Build tool',
    long_description=long_description,
    author='geothird',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='aws lambda python',
    py_modules=['albt'],
    install_requires=[
        'Click',
        'boto3',
        'pyyaml'
    ],
    entry_points='''
        [console_scripts]
        albt=albt.albt:cli
    ''',
)
