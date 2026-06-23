"""
Basic API tests for the ``xxhash.threadsafe`` module.

Verifies that:
  * the ``xxhash.threadsafe`` submodule is importable
  * all 4 hash types (xxh32, xxh64, xxh3_64, xxh128/xxh3_128) work
  * streaming methods (update, digest, hexdigest, intdigest, copy, reset) work
  * results match the default ``xxhash`` module exactly
  * ``repr()`` and ``type.__module__`` reflect the public module name
"""

import os
import unittest
import xxhash
from xxhash import threadsafe


# Known good values from the default xxhash module.
XXH32_A = (b'a', 1426945110)
XXH64_A = (b'a', 15154266338359012955)
XXH3_64_A = (b'a', 16629034431890738719)
XXH3_128_A = (b'a', 225219434562328483135862406050043285023)

class TestThreadsafeTypes(unittest.TestCase):
    """Verify that all 4 hash types exist and produce correct results."""

    def test_xxh32_object(self):
        h = threadsafe.xxh32(b'a')
        self.assertEqual(h.intdigest(), XXH32_A[1])

    def test_xxh32_seed(self):
        h = threadsafe.xxh32(b'a', seed=42)
        self.assertEqual(h.intdigest(), threadsafe.xxh32(b'a', 42).intdigest())

    def test_xxh32_matches_default(self):
        default = xxhash.xxh32(b'hello world', 123)
        safe = threadsafe.xxh32(b'hello world', 123)
        self.assertEqual(default.digest(), safe.digest())
        self.assertEqual(default.hexdigest(), safe.hexdigest())
        self.assertEqual(default.intdigest(), safe.intdigest())

    def test_xxh64_object(self):
        h = threadsafe.xxh64(b'a')
        self.assertEqual(h.intdigest(), XXH64_A[1])

    def test_xxh64_matches_default(self):
        default = xxhash.xxh64(b'hello world', 123)
        safe = threadsafe.xxh64(b'hello world', 123)
        self.assertEqual(default.digest(), safe.digest())
        self.assertEqual(default.hexdigest(), safe.hexdigest())
        self.assertEqual(default.intdigest(), safe.intdigest())

    def test_xxh3_64_object(self):
        h = threadsafe.xxh3_64(b'a')
        self.assertEqual(h.intdigest(), XXH3_64_A[1])

    def test_xxh3_64_matches_default(self):
        default = xxhash.xxh3_64(b'hello world', 123)
        safe = threadsafe.xxh3_64(b'hello world', 123)
        self.assertEqual(default.digest(), safe.digest())
        self.assertEqual(default.hexdigest(), safe.hexdigest())
        self.assertEqual(default.intdigest(), safe.intdigest())

    def test_xxh128_object(self):
        h = threadsafe.xxh128(b'a')
        self.assertEqual(h.intdigest(), XXH3_128_A[1])

    def test_xxh128_matches_default(self):
        default = xxhash.xxh128(b'hello world', 123)
        safe = threadsafe.xxh128(b'hello world', 123)
        self.assertEqual(default.digest(), safe.digest())
        self.assertEqual(default.hexdigest(), safe.hexdigest())
        self.assertEqual(default.intdigest(), safe.intdigest())


class TestThreadsafeStreaming(unittest.TestCase):
    """Verify that streaming operations work correctly."""

    def test_update(self):
        h = threadsafe.xxh32()
        h.update(b'a')
        self.assertEqual(h.digest(), threadsafe.xxh32(b'a').digest())
        h.update(b'b')
        self.assertEqual(h.digest(), threadsafe.xxh32(b'ab').digest())
        h.update(b'c')
        self.assertEqual(h.digest(), threadsafe.xxh32(b'abc').digest())

    def test_update_chain(self):
        for typ, data in [
            (threadsafe.xxh32, b'x' * 100000),
            (threadsafe.xxh64, b'x' * 100000),
            (threadsafe.xxh3_64, b'x' * 100000),
            (threadsafe.xxh128, b'x' * 100000),
        ]:
            with self.subTest(typ=typ):
                h = typ()
                h.update(data)
                self.assertEqual(h.digest(), typ(data).digest())

    def test_reset(self):
        for typ in [threadsafe.xxh32, threadsafe.xxh64,
                    threadsafe.xxh3_64, threadsafe.xxh128]:
            with self.subTest(typ=typ):
                h = typ()
                initial = h.intdigest()
                for _ in range(10):
                    h.update(os.urandom(64))
                h.reset()
                self.assertEqual(initial, h.intdigest())

    def test_copy(self):
        for typ in [threadsafe.xxh32, threadsafe.xxh64,
                    threadsafe.xxh3_64, threadsafe.xxh128]:
            with self.subTest(typ=typ):
                a = typ()
                a.update(b'hello world')
                b = a.copy()
                self.assertEqual(a.digest(), b.digest())
                self.assertEqual(a.intdigest(), b.intdigest())
                self.assertEqual(a.hexdigest(), b.hexdigest())
                b.update(b'more data')
                self.assertNotEqual(a.digest(), b.digest())

    def test_digest_hexdigest_intdigest(self):
        for typ, known in [
            (threadsafe.xxh32, XXH32_A),
            (threadsafe.xxh64, XXH64_A),
            (threadsafe.xxh3_64, XXH3_64_A),
            (threadsafe.xxh128, XXH3_128_A),
        ]:
            data, expected = known
            with self.subTest(typ=typ):
                h = typ(data)
                self.assertEqual(h.intdigest(), expected)
                self.assertIsInstance(h.digest(), bytes)
                self.assertIsInstance(h.hexdigest(), str)
                self.assertIsInstance(h.intdigest(), int)


class TestThreadsafeTopLevelFunctions(unittest.TestCase):
    """Verify that top-level convenience functions work."""

    def test_xxh32_digest(self):
        self.assertEqual(
            threadsafe.xxh32_digest(b'a'),
            xxhash.xxh32_digest(b'a'),
        )

    def test_xxh32_hexdigest(self):
        self.assertEqual(
            threadsafe.xxh32_hexdigest(b'a'),
            xxhash.xxh32_hexdigest(b'a'),
        )

    def test_xxh32_intdigest(self):
        self.assertEqual(
            threadsafe.xxh32_intdigest(b'a'),
            xxhash.xxh32_intdigest(b'a'),
        )

    def test_xxh64_digest(self):
        self.assertEqual(
            threadsafe.xxh64_digest(b'a'),
            xxhash.xxh64_digest(b'a'),
        )

    def test_xxh64_hexdigest(self):
        self.assertEqual(
            threadsafe.xxh64_hexdigest(b'a'),
            xxhash.xxh64_hexdigest(b'a'),
        )

    def test_xxh64_intdigest(self):
        self.assertEqual(
            threadsafe.xxh64_intdigest(b'a'),
            xxhash.xxh64_intdigest(b'a'),
        )

    def test_xxh3_64_digest(self):
        self.assertEqual(
            threadsafe.xxh3_64_digest(b'a'),
            xxhash.xxh3_64_digest(b'a'),
        )

    def test_xxh3_64_hexdigest(self):
        self.assertEqual(
            threadsafe.xxh3_64_hexdigest(b'a'),
            xxhash.xxh3_64_hexdigest(b'a'),
        )

    def test_xxh3_64_intdigest(self):
        self.assertEqual(
            threadsafe.xxh3_64_intdigest(b'a'),
            xxhash.xxh3_64_intdigest(b'a'),
        )

    def test_xxh128_digest(self):
        self.assertEqual(
            threadsafe.xxh128_digest(b'a'),
            xxhash.xxh128_digest(b'a'),
        )

    def test_xxh128_hexdigest(self):
        self.assertEqual(
            threadsafe.xxh128_hexdigest(b'a'),
            xxhash.xxh128_hexdigest(b'a'),
        )

    def test_xxh128_intdigest(self):
        self.assertEqual(
            threadsafe.xxh128_intdigest(b'a'),
            xxhash.xxh128_intdigest(b'a'),
        )


class TestThreadsafeRepr(unittest.TestCase):
    """Verify that repr() and __module__ use the public module name."""

    def test_repr_xxh32(self):
        h = threadsafe.xxh32()
        self.assertIn("xxhash.threadsafe", repr(h))
        self.assertEqual(type(h).__module__, "xxhash.threadsafe")

    def test_repr_xxh64(self):
        h = threadsafe.xxh64()
        self.assertIn("xxhash.threadsafe", repr(h))
        self.assertEqual(type(h).__module__, "xxhash.threadsafe")

    def test_repr_xxh3_64(self):
        h = threadsafe.xxh3_64()
        self.assertIn("xxhash.threadsafe", repr(h))
        self.assertEqual(type(h).__module__, "xxhash.threadsafe")

    def test_repr_xxh128(self):
        h = threadsafe.xxh128()
        self.assertIn("xxhash.threadsafe", repr(h))
        self.assertEqual(type(h).__module__, "xxhash.threadsafe")


class TestThreadsafeLargeData(unittest.TestCase):
    """Verify that large data paths (≥64KB GIL release threshold) work."""

    SIZE = 64 * 1024  # exactly the GIL release threshold

    def test_xxh32_large(self):
        data = b'x' * self.SIZE
        self.assertEqual(
            threadsafe.xxh32(data).digest(),
            xxhash.xxh32(data).digest(),
        )

    def test_xxh64_large(self):
        data = b'x' * self.SIZE
        self.assertEqual(
            threadsafe.xxh64(data).digest(),
            xxhash.xxh64(data).digest(),
        )

    def test_xxh3_64_large(self):
        data = b'x' * self.SIZE
        self.assertEqual(
            threadsafe.xxh3_64(data).digest(),
            xxhash.xxh3_64(data).digest(),
        )

    def test_xxh128_large(self):
        data = b'x' * self.SIZE
        self.assertEqual(
            threadsafe.xxh128(data).digest(),
            xxhash.xxh128(data).digest(),
        )

    def test_streaming_update_large_chunks(self):
        """Verify that streaming with large chunks works."""
        h = threadsafe.xxh64()
        for _ in range(5):
            h.update(b'x' * self.SIZE)
        expected = xxhash.xxh64(b'x' * (5 * self.SIZE)).digest()
        self.assertEqual(h.digest(), expected)


class TestThreadsafeAttributes(unittest.TestCase):
    """Verify that threadsafe types have the expected attributes."""

    def test_name(self):
        self.assertEqual(threadsafe.xxh32().name, "XXH32")
        self.assertEqual(threadsafe.xxh64().name, "XXH64")
        self.assertEqual(threadsafe.xxh3_64().name, "XXH3_64")
        self.assertEqual(threadsafe.xxh128().name, "XXH3_128")

    def test_seed_attribute(self):
        h = threadsafe.xxh32(b'test', 42)
        self.assertEqual(h.seed, 42)

    def test_digest_size(self):
        self.assertEqual(threadsafe.xxh32().digest_size, 4)
        self.assertEqual(threadsafe.xxh64().digest_size, 8)
        self.assertEqual(threadsafe.xxh3_64().digest_size, 8)
        self.assertEqual(threadsafe.xxh128().digest_size, 16)

    def test_block_size(self):
        self.assertEqual(threadsafe.xxh32().block_size, 16)
        self.assertEqual(threadsafe.xxh64().block_size, 32)
        self.assertEqual(threadsafe.xxh3_64().block_size, 32)
        self.assertEqual(threadsafe.xxh128().block_size, 64)


class TestThreadsafeTypesAreDistinct(unittest.TestCase):
    """Verify that threadsafe types are distinct from the default types.

    A regression here (e.g. both modules accidentally pointing at the same
    type object) would silently break thread safety with no other test
    catching it.
    """

    def test_types_are_distinct(self):
        for name in ('xxh32', 'xxh64', 'xxh3_64', 'xxh128'):
            with self.subTest(name=name):
                default_type = getattr(xxhash, name)
                safe_type = getattr(threadsafe, name)
                self.assertIsNot(default_type, safe_type)
                self.assertIsNot(type(default_type()), type(safe_type()))

    def test_instances_are_not_instances_of_each_other(self):
        for name in ('xxh32', 'xxh64', 'xxh3_64', 'xxh128'):
            with self.subTest(name=name):
                default_type = getattr(xxhash, name)
                safe_type = getattr(threadsafe, name)
                self.assertFalse(isinstance(default_type(), safe_type))
                self.assertFalse(isinstance(safe_type(), default_type))


if __name__ == '__main__':
    unittest.main()
