#!/usr/bin/env python
#
# Confidential Information of Forward Networks, Inc.
# Copyright (c) 2015 Forward Networks, Inc.  All rights reserved.
#
# Script to handle single package builds.
from setuptools import setup

__version__ = '0.0.25'

setup(name='fwd_api',
      version=__version__,
      description='Python libraries for Forward Networks API',
      url='http://www.forwardnetworks.com/',
      author='Forward Networks',
      packages=['fwd_api'],
      zip_safe=False)
