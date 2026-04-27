import unittest
import xxhash
import array

class TestFastcall(unittest.TestCase):
    """Test all argument passing combinations for METH_FASTCALL module-level functions."""

    data = b'hello world'
    seeds_32 = [0, 1, 42, 2**31 - 1, 2**32 - 1, 2**32, 2**64, 2**65 - 1]
    seeds_64 = [0, 1, 42, 2**63 - 1, 2**64 - 1, 2**64, 2**128]

    def _funcs(self, algo):
        return (
            getattr(xxhash, f'{algo}_digest'),
            getattr(xxhash, f'{algo}_intdigest'),
            getattr(xxhash, f'{algo}_hexdigest'),
        )

    def _check(self, algo, data, seed=None, seed_kw=False):
        obj = getattr(xxhash, algo)(data, seed=seed if seed is not None else 0)
        d, i, h = self._funcs(algo)
        if seed is None:
            self.assertEqual(d(data), obj.digest())
            self.assertEqual(i(data), obj.intdigest())
            self.assertEqual(h(data), obj.hexdigest())
        elif seed_kw:
            self.assertEqual(d(data, seed=seed), obj.digest())
            self.assertEqual(i(data, seed=seed), obj.intdigest())
            self.assertEqual(h(data, seed=seed), obj.hexdigest())
        else:
            self.assertEqual(d(data, seed), obj.digest())
            self.assertEqual(i(data, seed), obj.intdigest())
            self.assertEqual(h(data, seed), obj.hexdigest())

    # ---- bytes / str / buffers ----
    def test_bytes(self):
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            self._check(a, self.data)

    def test_str(self):
        s = self.data.decode()
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            self._check(a, s)

    def test_bytearray(self):
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            self._check(a, bytearray(self.data))

    def test_memoryview(self):
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            self._check(a, memoryview(self.data))

    def test_array(self):
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            self._check(a, array.array('B', self.data))

    def test_empty(self):
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            self._check(a, b'')

    # ---- positional seed ----
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

    # ---- keyword seed ----
    def test_keyword_seed_xxh32(self):
        for s in self.seeds_32:
            self._check('xxh32', self.data, seed=s, seed_kw=True)

    def test_keyword_seed_xxh64(self):
        for s in self.seeds_64:
            self._check('xxh64', self.data, seed=s, seed_kw=True)

    def test_keyword_seed_xxh3_64(self):
        for s in self.seeds_64:
            self._check('xxh3_64', self.data, seed=s, seed_kw=True)

    def test_keyword_seed_xxh3_128(self):
        for s in self.seeds_64:
            self._check('xxh3_128', self.data, seed=s, seed_kw=True)

    # ---- keyword input ----
    def test_keyword_input(self):
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            d, i, h = self._funcs(a)
            obj = getattr(xxhash, a)(self.data)
            self.assertEqual(d(input=self.data), obj.digest())
            self.assertEqual(i(input=self.data), obj.intdigest())
            self.assertEqual(h(input=self.data), obj.hexdigest())

    def test_keyword_input_and_seed(self):
        obj = xxhash.xxh3_64(self.data, seed=42)
        self.assertEqual(xxhash.xxh3_64_digest(input=self.data, seed=42), obj.digest())

    # ---- missing input ----
    def test_missing_input(self):
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            for fn in self._funcs(a):
                with self.assertRaises(TypeError):
                    fn()

    def test_unknown_keyword(self):
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            for fn in self._funcs(a):
                with self.assertRaises(TypeError):
                    fn(self.data, bad=1)

    def test_duplicate_argument(self):
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            for fn in self._funcs(a):
                with self.assertRaises(TypeError):
                    fn(self.data, input=self.data)

    def test_too_many_positional(self):
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            for fn in self._funcs(a):
                with self.assertRaises(TypeError):
                    fn(self.data, 0, 1)

    def test_invalid_seed_type(self):
        for a in ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128'):
            for fn in self._funcs(a):
                with self.assertRaises(TypeError):
                    fn(self.data, seed='bad')
