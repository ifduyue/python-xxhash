python-xxhash
=============

.. image:: https://travis-ci.org/ifduyue/python-xxhash.svg?branch=master
    :target: https://travis-ci.org/ifduyue/python-xxhash
    :alt: Build Status

.. image:: https://img.shields.io/pypi/v/xxhash.svg
    :target: https://warehouse.python.org/project/xxhash/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/xxhash.svg
    :target: https://warehouse.python.org/project/xxhash/
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/l/xxhash.svg
    :target: https://warehouse.python.org/project/xxhash/
    :alt: License


.. _HMAC: http://en.wikipedia.org/wiki/Hash-based_message_authentication_code
.. _xxHash: https://github.com/Cyan4973/xxHash
.. _Cyan4973: https://github.com/Cyan4973


xxhash is a Python binding for the xxHash_ library by `Yann Collet`__.

__ Cyan4973_

Installation
------------

.. code-block:: bash

   $ pip install xxhash

As of version 1.0.0, xxhash provides two variants: the original CPython variant,
and the new CFFI variant. By default the installation is the CPython variant,
setting env variable ``XXHASH_FORCE_CFFI=1`` to install the CFFI variant:

.. code-block:: bash

   $ export XXHASH_FORCE_CFFI=1
   $ pip install xxhash

Installation Prerequisites
~~~~~~~~~~~~~~~~~~~~~~~~~~~

CPython variant
^^^^^^^^^^^^^^^^

On Debian/Ubuntu:

.. code-block:: bash

   $ apt-get install python-dev gcc

On CentOS/Fedora:

.. code-block:: bash

   $ yum install python-devel gcc

CFFI variant
^^^^^^^^^^^^^

On Debian/Ubuntu:

.. code-block:: bash

   $ apt-get install libcffi-dev python-dev gcc

On CentOS/Fedora:

.. code-block:: bash

   $ yum install libcffi-devel python-devel gcc


Usage
--------

Module version and its backend xxHash library version can be retrieved using
the module properties ``VERSION`` AND ``XXHASH_VERSION`` respectively.

.. code-block:: python

    >>> import xxhash
    >>> xxhash.VERSION
    '1.0.0'
    >>> xxhash.XXHASH_VERSION
    '0.6.2'

This module is hashlib-compliant, which means you can use it in the same way as ``hashlib.md5``.

    | update() -- update the current digest with an additional string
    | digest() -- return the current digest value
    | hexdigest() -- return the current digest as a string of hexadecimal digits
    | intdigest() -- return the current digest as an integer
    | copy() -- return a copy of the current xxhash object
    | reset() -- reset state

md5 digest returns bytes, but the original xxh32 and xxh64 C APIs return integers.
While this module is made hashlib-compliant, ``intdigest()`` is also provided to
get the integer digest.

Constructors for hash algorithms provided by this module are ``xxh32()`` and ``xxh64()``.

For example, to obtain the digest of the byte string ``b'Nobody inspects the spammish repetition'``.

.. code-block:: python

    >>> import xxhash
    >>> x = xxhash.xxh32()
    >>> x.update(b'Nobody inspects')
    >>> x.update(b' the spammish repetition')
    >>> x.digest()
    b'\xe2);/'
    >>> x.digest_size
    4
    >>> x.block_size
    16

More condensed.

.. code-block:: python

    >>> xxhash.xxh32(b'Nobody inspects the spammish repetition').hexdigest()
    'e2293b2f'
    >>> xxhash.xxh32(b'Nobody inspects the spammish repetition').digest() == x.digest()
    True

An optional seed (default is 0) can be used to alter the result predictably.

.. code-block:: python

    >>> import xxhash
    >>> xxhash.xxh64('xxhash').hexdigest()
    '32dd38952c4bc720'
    >>> xxhash.xxh64('xxhash', seed=20141025).hexdigest()
    'b559b98d844e0635'
    >>> x = xxhash.xxh64(seed=20141025)
    >>> x.update('xxhash')
    >>> x.hexdigest()
    'b559b98d844e0635'
    >>> x.intdigest()
    13067679811253438005

Be careful that xxh32 takes an unsigned 32-bit integer as seed, while xxh64
takes an unsigned 64-bit integer. Although unsigned integer overflow is
defined behavior, it's better to not to let it happen.

.. code-block:: python

    >>> xxhash.xxh32('I want an unsigned 32-bit seed!', seed=0).hexdigest()
    'f7a35af8'
    >>> xxhash.xxh32('I want an unsigned 32-bit seed!', seed=2**32).hexdigest()
    'f7a35af8'
    >>> xxhash.xxh32('I want an unsigned 32-bit seed!', seed=-1).hexdigest()
    'eb9e6f02'
    >>> xxhash.xxh32('I want an unsigned 32-bit seed!', seed=2**32-1).hexdigest()
    'eb9e6f02'
    >>>
    >>> xxhash.xxh64('I want an unsigned 64-bit seed!', seed=0).hexdigest()
    'd4cb0a70a2b8c7c1'
    >>> xxhash.xxh64('I want an unsigned 64-bit seed!', seed=2**64).hexdigest()
    'd4cb0a70a2b8c7c1'
    >>> xxhash.xxh64('I want an unsigned 64-bit seed!', seed=-1).hexdigest()
    '5d714af8fd50e4af'
    >>> xxhash.xxh64('I want an unsigned 64-bit seed!', seed=2**64-1).hexdigest()
    '5d714af8fd50e4af'


``digest()`` returns bytes of the **big-endian** representation of the integer
digest.

.. code-block:: python

    >>> import xxhash
    >>> h = xxhash.xxh64()
    >>> h.digest()
    b'\xefF\xdb7Q\xd8\xe9\x99'
    >>> h.intdigest().to_bytes(8, 'big')
    b'\xefF\xdb7Q\xd8\xe9\x99'
    >>> h.hexdigest()
    'ef46db3751d8e999'
    >>> format(h.intdigest(), '016x')
    'ef46db3751d8e999'
    >>> h.intdigest()
    17241709254077376921
    >>> int(h.hexdigest(), 16)
    17241709254077376921


Caveats
-------

ENDIANNESS
~~~~~~~~~~~

As of python-xxhash 0.3.0, ``digest()`` returns bytes of the
**big-endian** representation of the integer digest. It used
to be little-endian.

DONT USE XXHASH IN HMAC
~~~~~~~~~~~~~~~~~~~~~~~
Though you can use xxhash as an HMAC_ hash function, but it's
highly recommended not to.

xxhash is **NOT** a cryptographic hash function, it is a
non-cryptographic hash algorithm aimed at speed and quality.
Do not put xxhash in any position where cryptographic hash
functions are required.


Copyright and License
---------------------

Copyright (c) 2014-2017 Yue Du - https://github.com/ifduyue

Licensed under `BSD 2-Clause License <http://opensource.org/licenses/BSD-2-Clause>`_

