#!/usr/bin/env python


from setuptools import setup, Extension
import os

with open('xxhash/__init__.py') as f:
    for line in f:
        if line.startswith('VERSION = '):
            VERSION = eval(line.rsplit(None, 1)[-1])

USE_CPYTHON = os.getenv('XXHASH_FORCE_CFFI') in (None, '0')

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

setup_requires = ['nose>=1.3.0']
if USE_CPYTHON:
    install_requires = None
    ext_modules = [
        Extension(
            'cpython',
            ['xxhash/cpython.c', 'c-xxhash/xxhash.c'],
            extra_compile_args=extra_compile_args,
            include_dirs=['c-xxhash']
        )
    ]
    cffi_modules = None
else:
    install_requires = ['cffi']
    setup_requires.append('cffi')
    cffi_modules = ['ffibuild.py:ffi']
    ext_modules = None

setup(
    name='xxhash',
    version=VERSION,
    description="Python binding for xxHash",
    long_description=open('README.rst', 'r').read(),
    author='Yue Du',
    author_email='ifduyue@gmail.com',
    url='https://github.com/ifduyue/python-xxhash',
    license='BSD',
    packages=['xxhash'],
    ext_package='xxhash',
    ext_modules=ext_modules,
    cffi_modules=cffi_modules,
    setup_requires=setup_requires,
    install_requires=install_requires,
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
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
