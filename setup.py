#!/usr/bin/env python


from setuptools import setup, Extension
import os
import codecs


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
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    python_requires=">=3.7",
    ext_modules=ext_modules,
    package_data={"xxhash": ["py.typed", "**.pyi"]},
    # for compatibility, see https://pypi.org/project/setuptools-scm/7.1.0/#setup-py-usage-deprecated
    use_scm_version={
        "write_to": "xxhash/version.py",
        "local_scheme": "no-local-version",
        "write_to_template": "VERSION = \"{version}\"\nVERSION_TUPLE = {version_tuple}\n",
    },
    setup_requires=["setuptools_scm"],
)
