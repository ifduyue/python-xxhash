python-xxhash
=============

xxhash is a Python binding for the `xxHash library <http://code.google.com/p/xxhash/>`_ by Yann Collet.

Installation
------------
::

    $ pip install xxhash

Synopsis
--------

::

    >>> import xxhash
    >>> xxhash.VERSION
    '0.0.1'
    >>> xxhash.XXHASH_VERSION
    'r35'
    >>> xxhash.xxh32('a')
    1426945110
    >>> xxhash.xxh32('a') == xxhash.xxh32('a', 0) == xxhash.xxh32('a', seed=0)
    True
    >>> xxhash.xxh64('a')
    15154266338359012955L
    >>> xxhash.xxh64('a') == xxhash.xxh64('a', 0) == xxhash.xxh64('a', seed=0)
    True

Copyright and License
---------------------

Copyright (c) 2014 Yue Du - https://github.com/ifduyue

Licensed under `BSD 2-Clause License <http://opensource.org/licenses/BSD-2-Clause>`_

