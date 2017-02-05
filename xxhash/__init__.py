from __future__ import absolute_import

try:
    from xxhash.xxhash_cpython import xxh32, xxh64, XXHASH_VERSION
except ImportError:
    from xxhash.cffi import xxh32, xxh64, XXHASH_VERSION


VERSION = '1.0.dev0'
__all__ = ['xxh32', 'xxh64', 'VERSION', 'XXHASH_VERSION']
