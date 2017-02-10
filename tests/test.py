import os
import unittest
import random
import xxhash


class TestXXHASH(unittest.TestCase):
    def test_version(self):
        self.assertTrue(xxhash.VERSION)
        self.assertTrue(xxhash.XXHASH_VERSION)

    def test_xxh32(self):
        self.assertEqual(xxhash.xxh32('a').intdigest(), 1426945110)
        self.assertEqual(xxhash.xxh32('a', 0).intdigest(), 1426945110)
        self.assertEqual(xxhash.xxh32('a', 1).intdigest(), 4111757423)

    def test_xxh64(self):
        self.assertEqual(xxhash.xxh64('a').intdigest(), 15154266338359012955)
        self.assertEqual(xxhash.xxh64('a', 0).intdigest(), 15154266338359012955)
        self.assertEqual(xxhash.xxh64('a', 1).intdigest(), 16051599287423682246)

    def test_xxh32_update(self):
        x = xxhash.xxh32()
        x.update('a')
        self.assertEqual(xxhash.xxh32('a').digest(), x.digest())
        x.update('b')
        self.assertEqual(xxhash.xxh32('ab').digest(), x.digest())
        x.update('c')
        self.assertEqual(xxhash.xxh32('abc').digest(), x.digest())

        seed = random.randint(0, 2**32)
        x = xxhash.xxh32(seed=seed)
        x.update('a')
        self.assertEqual(xxhash.xxh32('a', seed).digest(), x.digest())
        x.update('b')
        self.assertEqual(xxhash.xxh32('ab', seed).digest(), x.digest())
        x.update('c')
        self.assertEqual(xxhash.xxh32('abc', seed).digest(), x.digest())

    def test_xxh64_update(self):
        x = xxhash.xxh64()
        x.update('a')
        self.assertEqual(xxhash.xxh64('a').digest(), x.digest())
        x.update('b')
        self.assertEqual(xxhash.xxh64('ab').digest(), x.digest())
        x.update('c')
        self.assertEqual(xxhash.xxh64('abc').digest(), x.digest())
        seed = random.randint(0, 2**64)
        x = xxhash.xxh64(seed=seed)
        x.update('a')
        self.assertEqual(xxhash.xxh64('a', seed).digest(), x.digest())
        x.update('b')
        self.assertEqual(xxhash.xxh64('ab', seed).digest(), x.digest())
        x.update('c')
        self.assertEqual(xxhash.xxh64('abc', seed).digest(), x.digest())

    def test_xxh32_reset(self):
        x = xxhash.xxh32()
        h = x.intdigest()

        for i in range(10, 50):
            x.update(os.urandom(i))

        x.reset()

        self.assertEqual(h, x.intdigest())

    def test_xxh64_reset(self):
        x = xxhash.xxh64()
        h = x.intdigest()

        for i in range(10, 50):
            x.update(os.urandom(i))

        x.reset()

        self.assertEqual(h, x.intdigest())

    def test_xxh32_copy(self):
        a = xxhash.xxh32()
        a.update('xxhash')

        b = a.copy()
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())

        b.update('xxhash')
        self.assertNotEqual(a.digest(), b.digest())
        self.assertNotEqual(a.intdigest(), b.intdigest())
        self.assertNotEqual(a.hexdigest(), b.hexdigest())

        a.update('xxhash')
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())

    def test_xxh64_copy(self):
        a = xxhash.xxh64()
        a.update('xxhash')

        b = a.copy()
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())

        b.update('xxhash')
        self.assertNotEqual(a.digest(), b.digest())
        self.assertNotEqual(a.intdigest(), b.intdigest())
        self.assertNotEqual(a.hexdigest(), b.hexdigest())

        a.update('xxhash')
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())

if __name__ == '__main__':
    unittest.main()
