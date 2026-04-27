"""Tests for hashlib compatibility."""
import unittest
import xxhash


class TestHashlibCompat(unittest.TestCase):
    """Verify hashlib-compatible interface."""

    data = b'hello world'

    def test_algorithms_available(self):
        self.assertIsInstance(xxhash.algorithms_available, set)
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128', 'xxh128'):
            self.assertIn(a, xxhash.algorithms_available)

    def test_algorithms_guaranteed(self):
        self.assertEqual(xxhash.algorithms_guaranteed, xxhash.algorithms_available)

    # ── str rejection ──────────────────────────────────────────────

    def test_str_rejected(self):
        for algo in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            for fn in (getattr(xxhash, f'{algo}_digest'),
                       getattr(xxhash, f'{algo}_intdigest'),
                       getattr(xxhash, f'{algo}_hexdigest')):
                # positional str
                with self.assertRaisesRegex(TypeError,
                        'Strings must be encoded before hashing'):
                    fn('hello')
                # keyword str
                with self.assertRaisesRegex(TypeError,
                        'Strings must be encoded before hashing'):
                    fn(data='hello')
                # None
                with self.assertRaisesRegex(TypeError,
                        'object supporting the buffer API required'):
                    fn(None)

    def test_str_rejected_constructor(self):
        for algo in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            cls = getattr(xxhash, algo)
            # positional str
            with self.assertRaisesRegex(TypeError,
                    'Strings must be encoded before hashing'):
                cls('hello')
            # keyword str
            with self.assertRaisesRegex(TypeError,
                    'Strings must be encoded before hashing'):
                cls(data='hello')
            # None
            with self.assertRaisesRegex(TypeError,
                    'object supporting the buffer API required'):
                cls(None)
            with self.assertRaisesRegex(TypeError,
                    'object supporting the buffer API required'):
                cls(data=None)

    def test_str_rejected_update(self):
        for algo in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            obj = getattr(xxhash, algo)()
            with self.assertRaisesRegex(TypeError,
                    'Strings must be encoded before hashing'):
                obj.update('hello')
            # also test that bytes work after
            obj.update(b'hello')
            self.assertIsInstance(obj.intdigest(), int)
            # None
            with self.assertRaisesRegex(TypeError,
                    'object supporting the buffer API required'):
                obj.update(None)
            with self.assertRaisesRegex(TypeError,
                    'object supporting the buffer API required'):
                obj.update(data=None)

    # ── unknown keyword ───────────────────────────────────────────

    def test_unknown_keyword(self):
        for algo in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            cls = getattr(xxhash, algo)
            with self.assertRaises(TypeError):
                cls(b'hello', bad=1)
            with self.assertRaises(TypeError):
                cls(data=b'hello', bad=1)
            obj = cls()
            with self.assertRaises(TypeError):
                obj.update(b'hello', bad=1)
            with self.assertRaises(TypeError):
                obj.update(data=b'hello', bad=1)

    # ── data keyword ───────────────────────────────────────────────

    def test_data_keyword(self):
        for algo in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            obj = getattr(xxhash, algo)(self.data)
            d_fn = getattr(xxhash, f'{algo}_digest')
            i_fn = getattr(xxhash, f'{algo}_intdigest')
            h_fn = getattr(xxhash, f'{algo}_hexdigest')
            self.assertEqual(d_fn(data=self.data), obj.digest())
            self.assertEqual(i_fn(data=self.data), obj.intdigest())
            self.assertEqual(h_fn(data=self.data), obj.hexdigest())

    def test_data_keyword_constructor(self):
        for algo in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            cls = getattr(xxhash, algo)
            obj = cls(data=self.data)
            self.assertEqual(obj.intdigest(),
                             getattr(xxhash, f'{algo}_intdigest')(self.data))

    # ── digest_size / block_size / name ────────────────────────────

    def test_digest_size(self):
        self.assertEqual(xxhash.xxh32().digest_size, 4)
        self.assertEqual(xxhash.xxh64().digest_size, 8)
        self.assertEqual(xxhash.xxh3_64().digest_size, 8)
        self.assertEqual(xxhash.xxh3_128().digest_size, 16)

    def test_block_size(self):
        self.assertEqual(xxhash.xxh32().block_size, 16)
        self.assertEqual(xxhash.xxh64().block_size, 32)
        self.assertEqual(xxhash.xxh3_64().block_size, 32)
        self.assertEqual(xxhash.xxh3_128().block_size, 64)

    def test_name(self):
        self.assertEqual(xxhash.xxh32().name, 'XXH32')
        self.assertEqual(xxhash.xxh64().name, 'XXH64')
        self.assertEqual(xxhash.xxh3_64().name, 'XXH3_64')
        self.assertEqual(xxhash.xxh3_128().name, 'XXH3_128')

    # ── digest / hexdigest ─────────────────────────────────────────

    def test_digest(self):
        for algo in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            obj = getattr(xxhash, algo)(self.data)
            d_fn = getattr(xxhash, f'{algo}_digest')
            self.assertEqual(obj.digest(), d_fn(self.data))
            self.assertIsInstance(obj.digest(), bytes)
            self.assertEqual(len(obj.digest()), obj.digest_size)

    def test_hexdigest(self):
        for algo in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            obj = getattr(xxhash, algo)(self.data)
            h_fn = getattr(xxhash, f'{algo}_hexdigest')
            self.assertEqual(obj.hexdigest(), h_fn(self.data))
            self.assertIsInstance(obj.hexdigest(), str)
            self.assertEqual(len(obj.hexdigest()), obj.digest_size * 2)

    # ── update ─────────────────────────────────────────────────────

    def test_update(self):
        for algo in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            a = getattr(xxhash, algo)()
            a.update(self.data)
            b = getattr(xxhash, algo)(self.data)
            self.assertEqual(a.digest(), b.digest())

    # ── copy ───────────────────────────────────────────────────────

    def test_copy(self):
        for algo in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            a = getattr(xxhash, algo)(self.data)
            b = a.copy()
            self.assertEqual(a.digest(), b.digest())
            b.update(b'more')
            self.assertNotEqual(a.digest(), b.digest())
