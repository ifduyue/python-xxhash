#!/usr/bin/env python


from setuptools import setup, find_packages, Extension

VERSION = "0.0.1"
XXHASH_VERSION = "r35"

setup(
    name='xxhash',
    version=VERSION,
    description="xxHash Bindings for Python",
    long_description=open('README.rst', 'r').read(),
    author='Yue Du',
    author_email='ifduyue@gmail.com',
    url='https://github.com/ifduyue/python-xxhash',
    ext_modules=[
        Extension('xxhash', [
            'python-xxhash.c',
            'xxhash/xxhash.c',
        ], extra_compile_args=[
            "-std=c99",
            "-O3",
            "-Wall",
            "-W",
            "-Wundef",
            "-DVERSION=\"%s\"" % VERSION,
            "-DXXHASH_VERSION=\"%s\"" % XXHASH_VERSION,
        ])
    ],
    setup_requires=["nose>=1.3.0"],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
