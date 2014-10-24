python-xxhash
=============

.. image:: https://travis-ci.org/ifduyue/python-xxhash.svg?branch=master
    :target: https://travis-ci.org/ifduyue/python-xxhash
    :alt: Build Status

.. image:: https://pypip.in/version/xxhash/badge.svg
    :target: https://warehouse.python.org/project/xxhash/
    :alt: Latest Version

.. image:: https://pypip.in/download/xxhash/badge.svg
    :target: https://warehouse.python.org/project/xxhash/
    :alt: Downloads

.. image:: https://pypip.in/py_versions/xxhash/badge.svg
    :target: https://warehouse.python.org/project/xxhash/
    :alt: Supported Python versions

.. image:: https://pypip.in/license/xxhash/badge.svg
    :target: https://warehouse.python.org/project/xxhash/
    :alt: License


xxhash is a Python binding for the `xxHash library <http://code.google.com/p/xxhash/>`_ by Yann Collet.

Installation
------------
::

    $ pip install xxhash

Usage
--------

Module version and its backend xxHash library version can be retrieved using
the module properties ``VERSION`` AND ``XXHASH_VERSION`` respectively::

    >>> import xxhash
    >>> xxhash.VERSION
    '0.2.0'
    >>> xxhash.XXHASH_VERSION
    'r37'

This module is hashlib-compliant, which means you can use it in the same way as ``hashlib.md5``.

    | update() -- updates the current digest with an additional string
    | digest() -- return the current digest value
    | hexdigest() -- return the current digest as a string of hexadecimal digits
    | intdigest() -- return the current digest as an integer
    | copy() -- return a copy of the current xxhash object

md5 digest returns bytes, but the original xxh32 and xxh64 C APIs return integers.
While this module is made hashlib-compliant, ``intdigest()`` is also provided to
get the integer digest.

Constructors for hash algorithms provided by this module are ``xxh32()`` and ``xxh64()``.

For example, to obtain the digest of the byte string ``b'Nobody inspects the spammish repetition'``::

    >>> import xxhash
    >>> x = xxhash.xxh32()
    >>> x.update(b'Nobody inspects')
    >>> x.update(b' the spammish repetition')
    >>> x.digest()
    '/;)\xe2'
    >>> x.digest_size
    4L
    >>> x.block_size
    16L

More condensed::

    >>> xxhash.xxh32(b'Nobody inspects the spammish repetition').hexdigest()
    '2f3b29e2'
    >>> xxhash.xxh32(b'Nobody inspects the spammish repetition').digest() == x.digest()
    True

An optional seed (default is 0) can be used to alter the result predictably::

    >>> import xxhash
    >>> xxhash.xxh64('xxhash').hexdigest()
    '20c74b2c9538dd32'
    >>> xxhash.xxh64('xxhash', seed=20141025).hexdigest()
    '35064e848db959b5'
    >>> x = xxhash.xxh64(seed=20141025)
    >>> x.update('xxhash')
    >>> x.hexdigest()
    '35064e848db959b5'
    >>> x.intdigest()
    13067679811253438005L


Caveats
-------

Though you can use xxhash as an HMAC hash function, but it's
highly recommend not to. 

xxhash is **NOT** a cryptographic hash function, it is a
non-cryptographic hash algorithm aimed at speed and quality.
Do not put xxhash in any position where cryptographic hash
functions are required.


Copyright and License
---------------------

Copyright (c) 2014 Yue Du - https://github.com/ifduyue

Licensed under `BSD 2-Clause License <http://opensource.org/licenses/BSD-2-Clause>`_

