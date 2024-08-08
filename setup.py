#!/usr/bin/env python


from setuptools import setup, Extension
import os
from pathlib import Path


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

d = Path(__file__).parent
long_description = d.joinpath('README.rst').read_text() + '\n' + d.joinpath('CHANGELOG.rst').read_text()

version_dict = {}
exec(d.joinpath("xxhash", "version.py").read_text(), {}, version_dict)
version = version_dict["VERSION"]

setup(
    name='xxhash',
    version=version,
    description="Python binding for xxHash",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author='Yue Du',
    author_email='ifduyue@gmail.com',
    url='https://github.com/ifduyue/python-xxhash',
    license='BSD',
    packages=['xxhash'],
    ext_package='xxhash',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    python_requires=">=3.7",
    ext_modules=ext_modules,
    package_data={"xxhash": ["py.typed", "**.pyi"]},
)
