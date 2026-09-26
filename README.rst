python-xxhash
=============

.. image:: https://github.com/ifduyue/python-xxhash/actions/workflows/test.yml/badge.svg
    :target: https://github.com/ifduyue/python-xxhash/actions/workflows/test.yml
    :alt: Github Actions Status

.. image:: https://img.shields.io/pypi/v/xxhash.svg
    :target: https://pypi.org/project/xxhash/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/pyversions/xxhash.svg
    :target: https://pypi.org/project/xxhash/
    :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/l/xxhash.svg
    :target: https://pypi.org/project/xxhash/
    :alt: License

.. image:: https://img.shields.io/endpoint?url=https://codspeed.io/badge.json
    :target: https://codspeed.io/ifduyue/python-xxhash?utm_source=badge
    :alt: CodSpeed


.. _HMAC: http://en.wikipedia.org/wiki/Hash-based_message_authentication_code
.. _xxHash: https://github.com/Cyan4973/xxHash
.. _Cyan4973: https://github.com/Cyan4973


xxhash is a Python binding for the xxHash_ library by `Yann Collet`__.

__ Cyan4973_

Installation
------------

.. code-block:: bash

   $ pip install xxhash
   
You can also install using conda:

.. code-block:: bash

   $ conda install -c conda-forge python-xxhash


Installing From Source
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   $ pip install --no-binary xxhash xxhash

Prerequisites
++++++++++++++

On Debian/Ubuntu:

.. code-block:: bash

   $ apt-get install python-dev gcc

On CentOS/Fedora:

.. code-block:: bash

   $ yum install python-devel gcc redhat-rpm-config

Linking to libxxhash.so
~~~~~~~~~~~~~~~~~~~~~~~~

By default python-xxhash will use bundled xxHash,
we can change this by specifying ENV var ``XXHASH_LINK_SO``:

.. code-block:: bash

   $ XXHASH_LINK_SO=1 pip install --no-binary xxhash xxhash

Usage
--------

Module version and its backend xxHash library version can be retrieved using
the module properties ``VERSION`` AND ``XXHASH_VERSION`` respectively.

.. code-block:: python

    >>> import xxhash
    >>> xxhash.VERSION
    '4.0.2'
    >>> xxhash.XXHASH_VERSION
    '0.8.4'

This module is hashlib-compliant, which means you can use it in the same way as ``hashlib.md5``.

    | update() -- update the current digest with additional data
    | digest() -- return the current digest value
    | hexdigest() -- return the current digest as a string of hexadecimal digits
    | intdigest() -- return the current digest as an integer
    | copy() -- return a clone of the current hash object
    | reset() -- reset state

To allow other Python threads to run, the GIL is released while hashing
more than 64 KiB of data at once in constructors (``xxh32(data)``),
``update()``, ``__init__``, and one-shot functions. Other code that can
reach the input buffer in that window is concurrent access. A
constructor does not publish the hasher until it returns, so only the
buffer can race during that call; ``update()``, ``__init__``, and
one-shot functions already have a visible hasher. Repeated ``update()``
calls are equivalent to concatenating the chunks:
``h.update(a); h.update(b)`` is ``h.update(a+b)``.

md5 digest returns bytes, but the original xxh32 and xxh64 C APIs return integers.
While this module is made hashlib-compliant, ``intdigest()`` is also provided to
get the integer digest.

Constructors for hash algorithms provided by this module include
``xxh32()`` and ``xxh64()``.

For example, to obtain the digest of the byte string ``b'Nobody inspects the spammish repetition'``:

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

More condensed:

.. code-block:: python

    >>> xxhash.xxh32(b'Nobody inspects the spammish repetition').hexdigest()
    'e2293b2f'
    >>> xxhash.xxh32(b'Nobody inspects the spammish repetition').digest() == x.digest()
    True

An optional seed (default is 0) can be used to alter the result predictably:

.. code-block:: python

    >>> import xxhash
    >>> xxhash.xxh64(b'xxhash').hexdigest()
    '32dd38952c4bc720'
    >>> xxhash.xxh64(b'xxhash', seed=20141025).hexdigest()
    'b559b98d844e0635'
    >>> x = xxhash.xxh64(seed=20141025)
    >>> x.update(b'xxhash')
    >>> x.hexdigest()
    'b559b98d844e0635'
    >>> x.intdigest()
    13067679811253438005

Be careful that xxh32 takes an unsigned 32-bit integer as seed, while xxh64
takes an unsigned 64-bit integer. Although unsigned integer overflow is
defined behavior, it's better not to make it happen:

.. code-block:: python

    >>> xxhash.xxh32(b'I want an unsigned 32-bit seed!', seed=0).hexdigest()
    'f7a35af8'
    >>> xxhash.xxh32(b'I want an unsigned 32-bit seed!', seed=2**32).hexdigest()
    'f7a35af8'
    >>> xxhash.xxh32(b'I want an unsigned 32-bit seed!', seed=1).hexdigest()
    'd8d4b4ba'
    >>> xxhash.xxh32(b'I want an unsigned 32-bit seed!', seed=2**32+1).hexdigest()
    'd8d4b4ba'
    >>>
    >>> xxhash.xxh64(b'I want an unsigned 64-bit seed!', seed=0).hexdigest()
    'd4cb0a70a2b8c7c1'
    >>> xxhash.xxh64(b'I want an unsigned 64-bit seed!', seed=2**64).hexdigest()
    'd4cb0a70a2b8c7c1'
    >>> xxhash.xxh64(b'I want an unsigned 64-bit seed!', seed=1).hexdigest()
    'ce5087f12470d961'
    >>> xxhash.xxh64(b'I want an unsigned 64-bit seed!', seed=2**64+1).hexdigest()
    'ce5087f12470d961'


``digest()`` returns bytes of the **big-endian** representation of the integer
digest:

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

Besides xxh32/xxh64 mentioned above, oneshot functions are also provided,
so we can avoid allocating XXH32/64 state on heap:

    | xxh32_digest(bytes, seed=0)
    | xxh32_intdigest(bytes, seed=0)
    | xxh32_hexdigest(bytes, seed=0)
    | xxh64_digest(bytes, seed=0)
    | xxh64_intdigest(bytes, seed=0)
    | xxh64_hexdigest(bytes, seed=0)

.. code-block:: python

    >>> import xxhash
    >>> xxhash.xxh64(b'a').digest() == xxhash.xxh64_digest(b'a')
    True
    >>> xxhash.xxh64(b'a').intdigest() == xxhash.xxh64_intdigest(b'a')
    True
    >>> xxhash.xxh64(b'a').hexdigest() == xxhash.xxh64_hexdigest(b'a')
    True
    >>> xxhash.xxh64_hexdigest(b'xxhash', seed=20141025)
    'b559b98d844e0635'
    >>> xxhash.xxh64_intdigest(b'xxhash', seed=20141025)
    13067679811253438005
    >>> xxhash.xxh64_digest(b'xxhash', seed=20141025)
    b'\xb5Y\xb9\x8d\x84N\x065'

.. code-block:: python

    In [1]: import xxhash

    In [2]: %timeit xxhash.xxh64_hexdigest(b'xxhash')
    268 ns ± 24.1 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

    In [3]: %timeit xxhash.xxh64(b'xxhash').hexdigest()
    416 ns ± 17.3 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)


XXH3 hashes are available since v2.0.0 (xxHash v0.8.0), they are:

Streaming classes:

    | xxh3_64
    | xxh3_128

Oneshot functions:

    | xxh3_64_digest(bytes, seed=0)
    | xxh3_64_intdigest(bytes, seed=0)
    | xxh3_64_hexdigest(bytes, seed=0)
    | xxh3_128_digest(bytes, seed=0)
    | xxh3_128_intdigest(bytes, seed=0)
    | xxh3_128_hexdigest(bytes, seed=0)

And aliases:

    | xxh128 = xxh3_128
    | xxh128_digest = xxh3_128_digest
    | xxh128_intdigest = xxh3_128_intdigest
    | xxh128_hexdigest = xxh3_128_hexdigest

Thread safety
-------------

Concurrent access is any other code that can reach the hasher's state or
the input buffer while a call is in progress, or that can interleave
between ``update()`` calls you meant to be sequential. OS threads,
``asyncio`` tasks (``await`` / ``asyncio.to_thread``), subinterpreters,
a ``ThreadPoolExecutor`` or GUI callback, and a ``__buffer__`` /
``__del__`` / weakref callback can re-enter the hasher. Buffer-protocol
callbacks run with the GIL held, before the object lock is taken.
Another process writing ``mmap`` / ``shared_memory`` can race the
buffer only. While a call is in progress, that other code must not
touch whichever of the hasher or the buffer it can reach. Between
calls, an ``await`` is enough for another task to sneak in.

One-shot functions (``xxh32_digest``, ``xxh64_hexdigest``,
``xxh3_128_digest``, and so on) are stateless: overlapping calls are
safe. They still release the GIL for more than 64 KiB, so a shared
mutable buffer is a data race, same as a large ``update()``.

Streaming objects in the default ``xxhash`` module are **safe on a shared
object**: each carries a per-object lock that serializes ``update()``,
``digest()``, ``hexdigest()``, ``intdigest()``, ``copy()``, ``reset()``,
and ``__init__``, so overlapping calls on the same object never corrupt
state or crash. The lock serializes those methods; it does not pin the
input buffer, and it does not cover attribute getters such as ``seed``.
The hash itself releases the GIL only for more than 64 KiB, and an
uncontended acquire keeps the GIL. On Python 3.9-3.12, once the lock
exists, a contended ``PyThread_acquire_lock`` releases the GIL while
waiting. That includes inputs of 64 KiB or less: ``update()`` and
``__init__`` have already exported the buffer, and ``digest()``,
``copy()``, and ``reset()`` take the same acquire. A ``bytearray`` or
memoryview mutated in that window, or while a large constructor,
``update()``, ``__init__``, or one-shot is hashing, is still a data
race. Python 3.13+ ``PyMutex`` waits do not release the GIL.

On Python 3.13+ the lock is always active. On Python 3.9-3.12 it is
allocated on the first ``update()`` or ``__init__`` of more than 64 KiB
— a large constructor (``xxh32(data)``) does not create it. Constructors
release the GIL for more than 64 KiB while the object is not yet
visible. Re-calling ``__init__`` on an existing object is reset plus
optional update: same lock and GIL rules as ``update()``.

Sharing one streaming object is still the wrong default. Concurrent
``update()`` calls have no defined concatenation order, so the digest is
nondeterministic even with the lock. Prefer a one-shot function, or one
hash object per task. ``copy()`` clones the current state so you can
hash data that shares a common prefix without repeating work.

``xxhash.nolock``
~~~~~~~~~~~~~~~~~

``xxhash.nolock`` is the same API without a per-object lock. Streaming
methods are faster, especially on Python 3.13+ and free-threaded builds.
It is only **safe on distinct objects**: exclusively own each streaming
hasher for its whole lifetime, including between method calls. Do not
let any other task, thread, callback, or interpreter reach it.

.. code-block:: python

    >>> from xxhash import nolock
    >>> h = nolock.xxh64()
    >>> h.update(b'xxhash')
    >>> h.hexdigest()
    '32dd38952c4bc720'

One hasher per thread, per task, or per request. A process-wide
singleton that "you will be careful with" is not a fit; use the default
module.

The caller must guarantee all of the following:

- **Exclusive access to the object.** Do not let any other code call
  ``update()``, ``digest()``, ``hexdigest()``, ``intdigest()``,
  ``copy()``, ``reset()``, or the constructor-style ``__init__`` on the
  same object, including between calls: an ``await`` between updates is
  enough for another task to sneak in. Do not drop the last reference
  while other code is still in a method. On free-threaded (no-GIL)
  Python a race is undefined behavior — a crash or silent corruption —
  not merely a wrong digest. ``xxh3_64`` / ``xxh128`` are the most
  crash-prone: their C state holds internal pointers, so an overlapping
  ``update()`` + ``reset()``/``copy()`` can segfault.
- **The input buffer must stay valid and unchanged until the call
  returns.** That is more than "do not write to it": do not resize it, do
  not ``memoryview.release()``, do not let the exporter be freed. This
  applies to constructors, ``update()``, ``__init__``, and one-shot
  functions. While
  the GIL is released (or absent), any scheduled code that can reach
  that memory is a C-level data race. The default module has the same
  GIL-release caveat for large inputs; ``nolock`` does not protect the
  buffer either. Prefer immutable ``bytes``, or copy a mutable buffer
  first.
- **You own the update order.** With no lock there is no serialization.
  Two overlapping ``update()`` calls do not concatenate in any defined
  order. Even the default locked module does not define a canonical
  interleaving: if you need ``a+b``, keep the updates on one sequential
  path, or take your own lock around the whole sequence.

Other notes:

- ``copy()`` clones the current state (a hashlib-style copy). The clone
  is also unlocked. After ``copy()`` returns, the two objects are
  independent and may be used on different tasks — but the ``copy()``
  call itself must not overlap ``update()`` / ``reset()`` on the source.
- ``xxhash.xxh64`` and ``xxhash.nolock.xxh64`` (and the other algorithms)
  are different types. ``isinstance`` across the two is false; APIs that
  type-check against the default classes will reject ``nolock`` objects.
- On regular GIL Python, a small ``update()`` holds the GIL, which can
  hide races in testing. Free-threaded builds, inputs of more than
  64 KiB, and any yield/callback that lets other code run will not.
  "It worked on 3.12 with 4 KiB chunks" is not proof the object is safe
  to share.
- If you take your own ``threading.Lock``, it must cover the whole
  sequence you care about (every ``update()`` plus the final
  ``digest()``), and the buffer rule still applies inside the locked
  section. At that point the default module is usually simpler.
- One-shot functions on ``xxhash.nolock`` (``xxh64_digest``, and so on)
  are still stateless and safe to call concurrently. A shared mutable
  buffer is still a data race when the GIL is released. If the data is
  already in one buffer, prefer a one-shot function over a streaming
  object.

The same two-module split is provided on free-threaded builds: the default
module stays locked, and ``xxhash.nolock`` is the unlocked opt-in.

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

Copyright (c) 2014-2026 Yue Du - https://github.com/ifduyue

Licensed under `BSD 2-Clause License <http://opensource.org/licenses/BSD-2-Clause>`_
