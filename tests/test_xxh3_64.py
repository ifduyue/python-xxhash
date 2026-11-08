from __future__ import print_function
import os
import sys
import unittest
import random
import xxhash


class TestXXH(unittest.TestCase):
    def test_xxh3_64(self):
        self.assertEqual(xxhash.xxh3_64(b'a').intdigest(), 16629034431890738719)
        self.assertEqual(xxhash.xxh3_64(b'a', 0).intdigest(), 16629034431890738719)
        self.assertEqual(xxhash.xxh3_64(b'a', 1).intdigest(), 15201566949650179872)
        self.assertEqual(xxhash.xxh3_64(b'a', 2**64-1).intdigest(), 4875116479388997462)

    def test_xxh3_64_intdigest(self):
        self.assertEqual(xxhash.xxh3_64_intdigest(b'a'), 16629034431890738719)
        self.assertEqual(xxhash.xxh3_64_intdigest(b'a', 0), 16629034431890738719)
        self.assertEqual(xxhash.xxh3_64_intdigest(b'a', 1), 15201566949650179872)
        self.assertEqual(xxhash.xxh3_64_intdigest(b'a', 2**64-1), 4875116479388997462)

    def test_xxh3_64_long(self):
        # Longer than 240 bytes, so this exercises the XXH3 long path.
        cases = [
            (b'a' * 241, 0, 17784696633448601904),
            (b'a' * 241, 1, 10343239347255277306),
            (b'a' * 1024, 0, 5358556820880783900),
            (bytes(range(256)) * 4, 0, 12137474952470826274),
            (b'\x00' * 65536, 0, 3725042947095682218),
        ]
        for data, seed, expected in cases:
            self.assertEqual(xxhash.xxh3_64_intdigest(data, seed), expected)
            h = xxhash.xxh3_64(seed=seed)
            for i in range(0, len(data), 100):
                h.update(data[i:i + 100])
            self.assertEqual(h.intdigest(), expected)

    def test_xxh3_64_update(self):
        x = xxhash.xxh3_64()
        x.update(b'a')
        self.assertEqual(xxhash.xxh3_64(b'a').digest(), x.digest())
        self.assertEqual(xxhash.xxh3_64_digest(b'a'), x.digest())
        x.update(b'b')
        self.assertEqual(xxhash.xxh3_64(b'ab').digest(), x.digest())
        self.assertEqual(xxhash.xxh3_64_digest(b'ab'), x.digest())
        x.update(b'c')
        self.assertEqual(xxhash.xxh3_64(b'abc').digest(), x.digest())
        self.assertEqual(xxhash.xxh3_64_digest(b'abc'), x.digest())

        seed = random.randint(0, 2**64)
        x = xxhash.xxh3_64(seed=seed)
        x.update(b'a')
        self.assertEqual(xxhash.xxh3_64(b'a', seed).digest(), x.digest())
        self.assertEqual(xxhash.xxh3_64_digest(b'a', seed), x.digest())
        x.update(b'b')
        self.assertEqual(xxhash.xxh3_64(b'ab', seed).digest(), x.digest())
        self.assertEqual(xxhash.xxh3_64_digest(b'ab', seed), x.digest())
        x.update(b'c')
        self.assertEqual(xxhash.xxh3_64(b'abc', seed).digest(), x.digest())
        self.assertEqual(xxhash.xxh3_64_digest(b'abc', seed), x.digest())

    def test_xxh3_64_reset(self):
        x = xxhash.xxh3_64()
        h = x.intdigest()

        x.update(b'x' * 10240)
        x.reset()

        self.assertEqual(h, x.intdigest())

    def test_xxh3_64_seed_reset(self):
        seed = random.randint(0, 2**64-1)
        x = xxhash.xxh3_64(seed=seed)
        h = x.intdigest()
        x.update(b'x' * 10240)
        x.reset()
        self.assertEqual(h, x.intdigest())

    def test_xxh3_64_reset_more(self):
        x = xxhash.xxh3_64()
        h = x.intdigest()

        for i in range(random.randint(100, 200)):
            x.reset()

        self.assertEqual(h, x.intdigest())

        for i in range(10, 1000):
            x.update(os.urandom(i))
        x.reset()

        self.assertEqual(h, x.intdigest())

        for i in range(10, 1000):
            x.update(os.urandom(100))
        x.reset()

        self.assertEqual(h, x.intdigest())

    def test_xxh3_64_seed_reset_more(self):
        seed = random.randint(0, 2**64-1)
        x = xxhash.xxh3_64(seed=seed)
        h = x.intdigest()

        for i in range(random.randint(100, 200)):
            x.reset()

        self.assertEqual(h, x.intdigest())

        for i in range(10, 1000):
            x.update(os.urandom(i))
        x.reset()

        self.assertEqual(h, x.intdigest())

        for i in range(10, 1000):
            x.update(os.urandom(100))
        x.reset()

        self.assertEqual(h, x.intdigest())

    def test_xxh3_64_copy(self):
        a = xxhash.xxh3_64()
        a.update(b'xxhash')

        b = a.copy()
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())

        b.update(b'xxhash')
        self.assertNotEqual(a.digest(), b.digest())
        self.assertNotEqual(a.intdigest(), b.intdigest())
        self.assertNotEqual(a.hexdigest(), b.hexdigest())

        a.update(b'xxhash')
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())

    def test_xxh3_64_overflow(self):
        s = b'I want an unsigned 64-bit seed!'
        a = xxhash.xxh3_64(s, seed=0)
        b = xxhash.xxh3_64(s, seed=2**64)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), xxhash.xxh3_64_intdigest(s, seed=0))
        self.assertEqual(a.intdigest(), xxhash.xxh3_64_intdigest(s, seed=2**64))
        self.assertEqual(a.digest(), xxhash.xxh3_64_digest(s, seed=0))
        self.assertEqual(a.digest(), xxhash.xxh3_64_digest(s, seed=2**64))
        self.assertEqual(a.hexdigest(), xxhash.xxh3_64_hexdigest(s, seed=0))
        self.assertEqual(a.hexdigest(), xxhash.xxh3_64_hexdigest(s, seed=2**64))

        a = xxhash.xxh3_64(s, seed=1)
        b = xxhash.xxh3_64(s, seed=2**64+1)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), xxhash.xxh3_64_intdigest(s, seed=1))
        self.assertEqual(a.intdigest(), xxhash.xxh3_64_intdigest(s, seed=2**64+1))
        self.assertEqual(a.digest(), xxhash.xxh3_64_digest(s, seed=1))
        self.assertEqual(a.digest(), xxhash.xxh3_64_digest(s, seed=2**64+1))
        self.assertEqual(a.hexdigest(), xxhash.xxh3_64_hexdigest(s, seed=1))
        self.assertEqual(a.hexdigest(), xxhash.xxh3_64_hexdigest(s, seed=2**64+1))

        a = xxhash.xxh3_64(s, seed=2**65-1)
        b = xxhash.xxh3_64(s, seed=2**66-1)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), xxhash.xxh3_64_intdigest(s, seed=2**65-1))
        self.assertEqual(a.intdigest(), xxhash.xxh3_64_intdigest(s, seed=2**66-1))
        self.assertEqual(a.digest(), xxhash.xxh3_64_digest(s, seed=2**65-1))
        self.assertEqual(a.digest(), xxhash.xxh3_64_digest(s, seed=2**66-1))
        self.assertEqual(a.hexdigest(), xxhash.xxh3_64_hexdigest(s, seed=2**65-1))
        self.assertEqual(a.hexdigest(), xxhash.xxh3_64_hexdigest(s, seed=2**66-1))


if __name__ == '__main__':
    unittest.main()
