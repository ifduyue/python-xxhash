import unittest
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


if __name__ == '__main__':
    unittest.main()
