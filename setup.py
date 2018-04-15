#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     Valerio Cosentino <valcos@bitergia.com>
#

from setuptools import setup

setup(name="ghubby",
      description="Fetch user events from GitHub",
      long_description="Ghubby collects the activities within the past 90 "
                       "days of a user on GitHub by querying the API, which "
                       "is accessed via a token. In case the token rate "
                       "limit is reached, Ghubby sleeps until the rate limit "
                       "is reset. Ghubby is built on top of the GitHub "
                       "backend of chaoss/grimoirelab-perceval",
      url="https://github.com/valeriocos/ghubby",
      version="0.1.0",
      author="Valerio Cosentino",
      author_email="valcos@bitergia.com",
      license="GPLv3",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'License :: OSI Approved :: '
          'GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python :: 3'
      ],
      keywords="development analytics github user activity",
      packages=[
          'ghubby'
      ],
      install_requires=[
          'perceval>=0.10.0'
      ],
      zip_safe=False)
