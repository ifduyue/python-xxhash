#!/usr/bin/env python


from setuptools import setup, Extension
import os

VERSION = "0.6.3"

if os.name == 'posix':
    extra_compile_args = [
        "-std=c99",
        "-O3",
        "-Wall",
        "-W",
        "-Wundef",
        # ref: http://bugs.python.org/issue21121
        "-Wno-error=declaration-after-statement",
    ]
else:
    extra_compile_args = None

define_macros = [
    ('VERSION', VERSION),
]

setup(
    name='xxhash',
    version=VERSION,
    description="Python binding for xxHash",
    long_description=open('README.rst', 'r').read(),
    author='Yue Du',
    author_email='ifduyue@gmail.com',
    url='https://github.com/ifduyue/python-xxhash',
    license='BSD',
    ext_modules=[
        Extension('xxhash', [
            'python-xxhash.c',
            'xxhash/xxhash.c',
        ],
        extra_compile_args=extra_compile_args,
        define_macros=define_macros)
    ],
    setup_requires=["nose>=1.3.0"],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
