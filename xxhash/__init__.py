try:
    from xxhash.cpython import xxh32, xxh64, XXHASH_VERSION
except ImportError:
    from xxhash.cffi import xxh32, xxh64, XXHASH_VERSION


VERSION = '1.0.1'
__all__ = ['xxh32', 'xxh64', 'VERSION', 'XXHASH_VERSION']
