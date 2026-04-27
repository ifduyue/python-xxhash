"""Comprehensive argument-passing tests for METH_FASTCALL module-level functions.

Covers all four hash algorithms across digest/intdigest/hexdigest variants.
"""
import unittest
import xxhash


class TestFastcallNormal(unittest.TestCase):
    """Valid argument passing: positional, keyword, mixed, buffer types."""

    data = b'hello world'
    seeds_32 = [0, 1, 42, 2**31 - 1, 2**32 - 1, 2**32, 2**64, 2**65 - 1]
    seeds_64 = [0, 1, 42, 2**63 - 1, 2**64 - 1, 2**64, 2**128]
    algorithms = ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128')

    def _funcs(self, algo):
        return (
            getattr(xxhash, f'{algo}_digest'),
            getattr(xxhash, f'{algo}_intdigest'),
            getattr(xxhash, f'{algo}_hexdigest'),
        )

    def _check(self, algo, *args, **kwargs):
        """Assert all three module-level functions match the type method."""
        obj = getattr(xxhash, algo)(*args, **kwargs)
        d, i, h = self._funcs(algo)
        self.assertEqual(d(*args, **kwargs), obj.digest())
        self.assertEqual(i(*args, **kwargs), obj.intdigest())
        self.assertEqual(h(*args, **kwargs), obj.hexdigest())

    # ── positional input ──────────────────────────────────────────

    def test_input_bytes(self):
        for a in self.algorithms:
            self._check(a, self.data)

    def test_input_str(self):
        """hashlib compatibility: str raises TypeError."""
        s = self.data.decode()
        for a in self.algorithms:
            for fn in self._funcs(a):
                with self.assertRaises(TypeError):
                    fn(s)

    def test_input_empty(self):
        for a in self.algorithms:
            self._check(a, b'')

    # ── positional input + positional seed ────────────────────────

    def test_positional_seed_xxh32(self):
        for s in self.seeds_32:
            self._check('xxh32', self.data, seed=s)

    def test_positional_seed_xxh64(self):
        for s in self.seeds_64:
            self._check('xxh64', self.data, seed=s)

    def test_positional_seed_xxh3_64(self):
        for s in self.seeds_64:
            self._check('xxh3_64', self.data, seed=s)

    def test_positional_seed_xxh3_128(self):
        for s in self.seeds_64:
            self._check('xxh3_128', self.data, seed=s)

    # ── keyword input ─────────────────────────────────────────────

    def test_keyword_data(self):
        for a in self.algorithms:
            self._check(a, data=self.data)

    def test_keyword_data_and_seed(self):
        for a in self.algorithms:
            self._check(a, data=self.data, seed=42)

    # ── keyword seed (with positional input) ──────────────────────

    def test_keyword_seed_xxh32(self):
        for s in self.seeds_32:
            self._check('xxh32', self.data, seed=s)

    def test_keyword_seed_xxh64(self):
        for s in self.seeds_64:
            self._check('xxh64', self.data, seed=s)

    def test_keyword_seed_xxh3_64(self):
        for s in self.seeds_64:
            self._check('xxh3_64', self.data, seed=s)

    def test_keyword_seed_xxh3_128(self):
        for s in self.seeds_64:
            self._check('xxh3_128', self.data, seed=s)

    # ── buffer types for input ────────────────────────────────────

    def test_input_bytearray(self):
        for a in self.algorithms:
            self._check(a, bytearray(self.data))

    def test_input_memoryview(self):
        for a in self.algorithms:
            self._check(a, memoryview(self.data))

    def test_input_array(self):
        import array
        for a in self.algorithms:
            self._check(a, array.array('B', self.data))

    def test_input_mmap(self):
        import mmap, tempfile, os
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(self.data)
            f.flush()
        try:
            with open(f.name, 'rb') as f2:
                with mmap.mmap(f2.fileno(), 0, access=mmap.ACCESS_READ) as m:
                    for a in self.algorithms:
                        self._check(a, m)
        finally:
            os.unlink(f.name)

    def test_input_pickle_buffer(self):
        try:
            from pickle import PickleBuffer
        except ImportError:
            raise self.skipTest('PickleBuffer not available')
        for a in self.algorithms:
            self._check(a, PickleBuffer(self.data))

    def test_input_ctypes(self):
        import ctypes
        buf = (ctypes.c_char * len(self.data)).from_buffer_copy(self.data)
        for a in self.algorithms:
            self._check(a, buf)


class TestFastcallErrors(unittest.TestCase):
    """Invalid argument passing: all error cases."""

    data = b'hello world'
    algorithms = ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128')

    def _funcs(self, algo):
        return (
            getattr(xxhash, f'{algo}_digest'),
            getattr(xxhash, f'{algo}_intdigest'),
            getattr(xxhash, f'{algo}_hexdigest'),
        )

    def _assert_all_raise(self, exc_type, *args, **kwargs):
        for a in self.algorithms:
            for fn in self._funcs(a):
                with self.subTest(fn=fn.__name__, args=args, kwargs=kwargs), \
                     self.assertRaises(exc_type):
                    fn(*args, **kwargs)

    # ── missing input ─────────────────────────────────────────────

    def test_missing_input_no_args(self):
        self._assert_all_raise(TypeError)

    def test_missing_input_seed_only_kw(self):
        self._assert_all_raise(TypeError, seed=42)

    # ── too many positional ───────────────────────────────────────

    def test_too_many_positional(self):
        self._assert_all_raise(TypeError, self.data, 0, 1)

    # ── unknown keyword ───────────────────────────────────────────

    def test_unknown_keyword_input(self):
        """Old 'input' keyword is now unknown — was renamed to 'data'."""
        self._assert_all_raise(TypeError, input=self.data)

    def test_unknown_keyword_data_kw(self):
        self._assert_all_raise(TypeError, data=self.data, bad=1)

    # ── duplicate arguments ───────────────────────────────────────

    def test_duplicate_input(self):
        self._assert_all_raise(TypeError, self.data, data=self.data)

    def test_duplicate_seed(self):
        self._assert_all_raise(TypeError, self.data, 0, seed=1)

    # ── invalid seed type ─────────────────────────────────────────

    def test_invalid_seed_positional(self):
        self._assert_all_raise(TypeError, self.data, 'bad')

    def test_invalid_seed_keyword(self):
        self._assert_all_raise(TypeError, self.data, seed='bad')

    def test_invalid_seed_with_input_kw(self):
        self._assert_all_raise(TypeError, data=self.data, seed='bad')

    # ── invalid input type (not str, not buffer) ──────────────────

    def test_input_not_bytes_or_str(self):
        self._assert_all_raise(TypeError, 12345)

    def test_input_not_bytes_or_str_kw(self):
        self._assert_all_raise(TypeError, data=12345)


class TestFastcallSeedOverflow(unittest.TestCase):
    """Seed values wider than the hash type wrap modulo 2^bits."""

    data = b'hello world'

    def _check_wrap(self, algo, seed):
        """Module function with seed matches type constructor with same seed."""
        d = getattr(xxhash, f'{algo}_digest')
        obj = getattr(xxhash, algo)(self.data, seed=seed)
        self.assertEqual(d(self.data, seed), obj.digest())
        self.assertEqual(d(self.data, seed=seed), obj.digest())

    def test_xxh32_wrap(self):
        """2**32 wraps to 0, 2**32+1 wraps to 1, etc."""
        for s in (2**32, 2**32 + 1, 2**64, 2**65 - 1):
            self._check_wrap('xxh32', s)

    def test_xxh64_wrap(self):
        for s in (2**64, 2**64 + 1, 2**128):
            self._check_wrap('xxh64', s)

    def test_xxh3_64_wrap(self):
        for s in (2**64, 2**128):
            self._check_wrap('xxh3_64', s)

    def test_xxh3_128_wrap(self):
        for s in (2**64, 2**128):
            self._check_wrap('xxh3_128', s)
