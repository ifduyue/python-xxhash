import unittest
import random
import xxhash


class TestXXHASH(unittest.TestCase):

    def test_xxh32(self):
        self.assertEqual(xxhash.xxh32('a'), 1426945110)
        self.assertEqual(xxhash.xxh32('a', 0), 1426945110)
        self.assertEqual(xxhash.xxh32('a', 1), 4111757423)

    def test_xxh64(self):
        self.assertEqual(xxhash.xxh64('a'), 15154266338359012955)
        self.assertEqual(xxhash.xxh64('a', 0), 15154266338359012955)
        self.assertEqual(xxhash.xxh64('a', 1), 16051599287423682246)

    def test_XXH32(self):
        x = xxhash.XXH32()
        x.update('a')
        self.assertEqual(xxhash.xxh32('a'), x.digest())
        x.update('b')
        self.assertEqual(xxhash.xxh32('ab'), x.digest())
        x.update('c')
        self.assertEqual(xxhash.xxh32('abc'), x.digest())

        seed = random.randint(0, 2**32)
        x = xxhash.XXH32(seed)
        x.update('a')
        self.assertEqual(xxhash.xxh32('a', seed), x.digest())
        x.update('b')
        self.assertEqual(xxhash.xxh32('ab', seed), x.digest())
        x.update('c')
        self.assertEqual(xxhash.xxh32('abc', seed), x.digest())

    def test_XXH64(self):
        x = xxhash.XXH64()
        x.update('a')
        self.assertEqual(xxhash.xxh64('a'), x.digest())
        x.update('b')
        self.assertEqual(xxhash.xxh64('ab'), x.digest())
        x.update('c')
        self.assertEqual(xxhash.xxh64('abc'), x.digest())

        seed = random.randint(0, 2**32)
        x = xxhash.XXH64(seed)
        x.update('a')
        self.assertEqual(xxhash.xxh64('a', seed), x.digest())
        x.update('b')
        self.assertEqual(xxhash.xxh64('ab', seed), x.digest())
        x.update('c')
        self.assertEqual(xxhash.xxh64('abc', seed), x.digest())


if __name__ == '__main__':
    unittest.main()
