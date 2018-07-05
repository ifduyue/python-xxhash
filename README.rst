python-xxhash
=============

.. image:: https://travis-ci.org/ifduyue/python-xxhash.svg?branch=master
    :target: https://travis-ci.org/ifduyue/python-xxhash
    :alt: Travis CI Build Status

.. image:: https://ci.appveyor.com/api/projects/status/f9wv1dhgnoiyuhtd/branch/master?svg=true
    :target: https://ci.appveyor.com/project/duyue/python-xxhash
    :alt: Appveyor Build Status

.. image:: https://img.shields.io/pypi/v/xxhash.svg
    :target: https://pypi.org/project/xxhash/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/xxhash.svg
    :target: https://pypi.org/project/xxhash/
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/l/xxhash.svg
    :target: https://pypi.org/project/xxhash/
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

CPython Variant
^^^^^^^^^^^^^^^^

On Debian/Ubuntu:

.. code-block:: bash

   $ apt-get install python-dev gcc

On CentOS/Fedora:

.. code-block:: bash

   $ yum install python-devel gcc redhat-rpm-config

CFFI Variant
^^^^^^^^^^^^^

On Debian/Ubuntu:

.. code-block:: bash

   $ apt-get install libcffi-dev python-dev gcc

On CentOS/Fedora:

.. code-block:: bash

   $ yum install libcffi-devel python-devel gcc redhat-rpm-config


Usage
--------

Module version and its backend xxHash library version can be retrieved using
the module properties ``VERSION`` AND ``XXHASH_VERSION`` respectively.

.. code-block:: python

    >>> import xxhash
    >>> xxhash.VERSION
    '1.0.1'
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
    >>> xxhash.xxh32('I want an unsigned 32-bit seed!', seed=1).hexdigest()
    'd8d4b4ba'
    >>> xxhash.xxh32('I want an unsigned 32-bit seed!', seed=2**32+1).hexdigest()
    'd8d4b4ba'
    >>>
    >>> xxhash.xxh64('I want an unsigned 64-bit seed!', seed=0).hexdigest()
    'd4cb0a70a2b8c7c1'
    >>> xxhash.xxh64('I want an unsigned 64-bit seed!', seed=2**64).hexdigest()
    'd4cb0a70a2b8c7c1'
    >>> xxhash.xxh64('I want an unsigned 64-bit seed!', seed=1).hexdigest()
    'ce5087f12470d961'
    >>> xxhash.xxh64('I want an unsigned 64-bit seed!', seed=2**64+1).hexdigest()
    'ce5087f12470d961'


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

SEED OVERFLOW
~~~~~~~~~~~~~~

xxh32 takes an unsigned 32-bit integer as seed, and xxh64 takes
an unsigned 64-bit integer as seed. Make sure that the seed is greater than
or equal to ``0``.

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

Copyright (c) 2014-2018 Yue Du - https://github.com/ifduyue

Licensed under `BSD 2-Clause License <http://opensource.org/licenses/BSD-2-Clause>`_


CHANGELOG
-----------

v1.1.0 2018-07-05
~~~~~~~~~~~~~~~~~

- Allow input larger than 2GB
- Release the GIL on sufficiently large input
- Drop support for Python 3.2

v1.0.1 2017-03-02
~~~~~~~~~~~~~~~~~~

- Free state actively, instead of delegating it to ffi.gc

v1.0.0 2017-02-10
~~~~~~~~~~~~~~~~~~

- Fixed copy() segfault
- Added CFFI variant

v0.6.3 2017-02-10
~~~~~~~~~~~~~~~~~~

- Fixed copy() segfault

v0.6.2 2017-02-10
~~~~~~~~~~~~~~~~~~

- Upgrade xxHash to v0.6.2

v0.6.1 2016-06-26
~~~~~~~~~~~~~~~~~~

- Upgrade xxHash to v0.6.1


v0.5.0 2016-03-02
~~~~~~~~~~~~~~~~~~

- Upgrade xxHash to v0.5.0

v0.4.3 2015-08-21
~~~~~~~~~~~~~~~~~~

- Upgrade xxHash to r42

v0.4.1 2015-08-16
~~~~~~~~~~~~~~~~~~

- Upgrade xxHash to r41

v0.4.0 2015-08-05
~~~~~~~~~~~~~~~~~~

- Added method reset
- Upgrade xxHash to r40

v0.3.2 2015-01-27
~~~~~~~~~~~~~~~~~~

- Fixed some typos in docstrings

v0.3.1 2015-01-24
~~~~~~~~~~~~~~~~~~

- Upgrade xxHash to r39

v0.3.0 2014-11-11
~~~~~~~~~~~~~~~~~~

- Change digest() from little-endian representation to big-endian representation of the integer digest.
  This change breaks compatibility (digest() results are different).

v0.2.0 2014-10-25
~~~~~~~~~~~~~~~~~~

- Make this package hashlib-compliant

v0.1.3 2014-10-23
~~~~~~~~~~~~~~~~~~

- Update xxHash to r37

v0.1.2 2014-10-19
~~~~~~~~~~~~~~~~~~


- Improve: Check XXHnn_init() return value.
- Update xxHash to r36

v0.1.1 2014-08-07
~~~~~~~~~~~~~~~~~~

- Improve: Can now be built with Visual C++ Compiler.

v0.1.0 2014-08-05
~~~~~~~~~~~~~~~~~~


- New: XXH32 and XXH64 type, which support partially update.
- Fix: build under Python 3.4

v0.0.2 2014-08-03
~~~~~~~~~~~~~~~~~~

- NEW: Support Python 3

v0.0.1 2014-07-30
~~~~~~~~~~~~~~~~~~

- NEW: xxh32 and xxh64
