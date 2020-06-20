#!/usr/bin/env python


from setuptools import setup, Extension
import os
import codecs


with open('xxhash/__init__.py') as f:
    for line in f:
        if line.startswith('VERSION = '):
            VERSION = eval(line.rsplit(None, 1)[-1])
            break

if os.getenv('XXHASH_LINK_SO'):
    libraries = ['xxhash']
    source = ['src/_xxhash.c']
    include_dirs = []
else:
    libraries = []
    source = ['src/_xxhash.c', 'deps/xxhash/xxhash.c']
    include_dirs = ['deps/xxhash']

ext_modules = [
    Extension(
        '_xxhash',
        source,
        include_dirs=include_dirs,
        libraries=libraries,
    )
]

def readfile(filename):
    with codecs.open(filename, encoding='utf-8', mode='r') as f:
        return f.read()

long_description = readfile('README.rst') + '\n' + readfile('CHANGELOG.rst')

setup(
    name='xxhash',
    version=VERSION,
    description="Python binding for xxHash",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author='Yue Du',
    author_email='ifduyue@gmail.com',
    url='https://github.com/ifduyue/python-xxhash',
    license='BSD',
    packages=['xxhash'],
    ext_package='xxhash',
    test_suite='tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    python_requires=">=2.6, !=3.0.*, !=3.1.*, !=3.2.*",
    ext_modules=ext_modules,
)
