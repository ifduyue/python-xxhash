CHANGELOG
-----------

v1.4.1 2019-08-27
~~~~~~~~~~~~~~~~~

- Fixed: xxh3.h in missing from source tarball

v1.4.0 2019-08-25
~~~~~~~~~~~~~~~~~

- Upgrade xxHash to v0.7.1

v1.3.0 2018-10-21
~~~~~~~~~~~~~~~~~

- Wheels are now built automatically
- Split CFFI variant into a separate package `ifduyue/python-xxhash-cffi <https://github.com/ifduyue/python-xxhash-cffi>`_

v1.2.0 2018-07-13
~~~~~~~~~~~~~~~~~

- Add oneshot functions xxh{32,64}_{,int,hex}digest

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
