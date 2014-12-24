#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'requests',
    'Mako'
]

test_requirements = [
    'flake8',
    'coverage',
    'responses',
]

setup(
    name='pyzeef',
    version='0.1.0',
    description='Python ZEEF API handler',
    long_description=readme + '\n\n' + history,
    author='Ellison Leão',
    author_email='ellisonleao@gmail.com',
    url='https://github.com/ellisonleao/pyzeef',
    scripts=[
        'bin/zeef'
    ],
    packages=[
        'pyzeef',
    ],
    package_dir={'pyzeef':
                 'pyzeef'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='pyzeef',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
