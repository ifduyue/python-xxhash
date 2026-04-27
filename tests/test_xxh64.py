import os
import unittest
import random
import xxhash

class TestXXH(unittest.TestCase):
    def test_xxh64(self):
        self.assertEqual(xxhash.xxh64(b'a').intdigest(), 15154266338359012955)
        self.assertEqual(xxhash.xxh64(b'a', 0).intdigest(), 15154266338359012955)
        self.assertEqual(xxhash.xxh64(b'a', 1).intdigest(), 16051599287423682246)
        self.assertEqual(xxhash.xxh64(b'a', 2**64-1).intdigest(), 6972758980737027682)

    def test_xxh64_intdigest(self):
        self.assertEqual(xxhash.xxh64_intdigest(b'a'), 15154266338359012955)
        self.assertEqual(xxhash.xxh64_intdigest(b'a', 0), 15154266338359012955)
        self.assertEqual(xxhash.xxh64_intdigest(b'a', 1), 16051599287423682246)
        self.assertEqual(xxhash.xxh64_intdigest(b'a', 2**64-1), 6972758980737027682)

    def test_xxh64_update(self):
        x = xxhash.xxh64()
        x.update(b'a')
        self.assertEqual(xxhash.xxh64(b'a').digest(), x.digest())
        self.assertEqual(xxhash.xxh64_digest(b'a'), x.digest())
        x.update(b'b')
        self.assertEqual(xxhash.xxh64(b'ab').digest(), x.digest())
        self.assertEqual(xxhash.xxh64_digest(b'ab'), x.digest())
        x.update(b'c')
        self.assertEqual(xxhash.xxh64(b'abc').digest(), x.digest())
        self.assertEqual(xxhash.xxh64_digest(b'abc'), x.digest())

        seed = random.randint(0, 2**64)
        x = xxhash.xxh64(seed=seed)
        x.update(b'a')
        self.assertEqual(xxhash.xxh64(b'a', seed).digest(), x.digest())
        self.assertEqual(xxhash.xxh64_digest(b'a', seed), x.digest())
        x.update(b'b')
        self.assertEqual(xxhash.xxh64(b'ab', seed).digest(), x.digest())
        self.assertEqual(xxhash.xxh64_digest(b'ab', seed), x.digest())
        x.update(b'c')
        self.assertEqual(xxhash.xxh64(b'abc', seed).digest(), x.digest())
        self.assertEqual(xxhash.xxh64_digest(b'abc', seed), x.digest())

    def test_xxh64_reset(self):
        x = xxhash.xxh64()
        h = x.intdigest()

        for i in range(10, 50):
            x.update(os.urandom(i))

        x.reset()

        self.assertEqual(h, x.intdigest())

    def test_xxh64_copy(self):
        a = xxhash.xxh64()
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

    def test_xxh64_overflow(self):
        s = b'I want an unsigned 64-bit seed!'
        a = xxhash.xxh64(s, seed=0)
        b = xxhash.xxh64(s, seed=2**64)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), xxhash.xxh64_intdigest(s, seed=0))
        self.assertEqual(a.intdigest(), xxhash.xxh64_intdigest(s, seed=2**64))
        self.assertEqual(a.digest(), xxhash.xxh64_digest(s, seed=0))
        self.assertEqual(a.digest(), xxhash.xxh64_digest(s, seed=2**64))
        self.assertEqual(a.hexdigest(), xxhash.xxh64_hexdigest(s, seed=0))
        self.assertEqual(a.hexdigest(), xxhash.xxh64_hexdigest(s, seed=2**64))

        a = xxhash.xxh64(s, seed=1)
        b = xxhash.xxh64(s, seed=2**64+1)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), xxhash.xxh64_intdigest(s, seed=1))
        self.assertEqual(a.intdigest(), xxhash.xxh64_intdigest(s, seed=2**64+1))
        self.assertEqual(a.digest(), xxhash.xxh64_digest(s, seed=1))
        self.assertEqual(a.digest(), xxhash.xxh64_digest(s, seed=2**64+1))
        self.assertEqual(a.hexdigest(), xxhash.xxh64_hexdigest(s, seed=1))
        self.assertEqual(a.hexdigest(), xxhash.xxh64_hexdigest(s, seed=2**64+1))

        a = xxhash.xxh64(s, seed=2**65-1)
        b = xxhash.xxh64(s, seed=2**66-1)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), xxhash.xxh64_intdigest(s, seed=2**65-1))
        self.assertEqual(a.intdigest(), xxhash.xxh64_intdigest(s, seed=2**66-1))
        self.assertEqual(a.digest(), xxhash.xxh64_digest(s, seed=2**65-1))
        self.assertEqual(a.digest(), xxhash.xxh64_digest(s, seed=2**66-1))
        self.assertEqual(a.hexdigest(), xxhash.xxh64_hexdigest(s, seed=2**65-1))
        self.assertEqual(a.hexdigest(), xxhash.xxh64_hexdigest(s, seed=2**66-1))


if __name__ == '__main__':
    unittest.main()
