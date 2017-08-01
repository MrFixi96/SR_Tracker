# -*- coding: utf-8 -*-
"""
    sr_tracker Tests
    ~~~~~~~~~~~~

    Tests the sr_tracker application.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from setuptools import setup, find_packages

setup(
    name='sr_tracker',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask', 
        'flask_jsonpify',
        'flask_restful',
        'sqlalchemy',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
