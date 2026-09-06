"""
Basic API tests for the ``xxhash.nolock`` module.

Verifies that:
  * the ``xxhash.nolock`` submodule is importable
  * all 4 hash types (xxh32, xxh64, xxh3_64, xxh128/xxh3_128) work
  * streaming methods (update, digest, hexdigest, intdigest, copy, reset) work
  * results match the default ``xxhash`` module exactly
  * ``repr()`` and ``type.__module__`` reflect the public module name
  * nolock types are distinct from the default (locked) types
"""

import os
import unittest
import xxhash
from xxhash import nolock


# Known good values from the default xxhash module.
XXH32_A = (b'a', 1426945110)
XXH64_A = (b'a', 15154266338359012955)
XXH3_64_A = (b'a', 16629034431890738719)
XXH3_128_A = (b'a', 225219434562328483135862406050043285023)


class TestNolockTypes(unittest.TestCase):
    """Verify that all 4 hash types exist and produce correct results."""

    def test_xxh32_object(self):
        h = nolock.xxh32(b'a')
        self.assertEqual(h.intdigest(), XXH32_A[1])

    def test_xxh32_seed(self):
        h = nolock.xxh32(b'a', seed=42)
        self.assertEqual(h.intdigest(), nolock.xxh32(b'a', 42).intdigest())

    def test_xxh32_matches_default(self):
        default = xxhash.xxh32(b'hello world', 123)
        unlocked = nolock.xxh32(b'hello world', 123)
        self.assertEqual(default.digest(), unlocked.digest())
        self.assertEqual(default.hexdigest(), unlocked.hexdigest())
        self.assertEqual(default.intdigest(), unlocked.intdigest())

    def test_xxh64_object(self):
        h = nolock.xxh64(b'a')
        self.assertEqual(h.intdigest(), XXH64_A[1])

    def test_xxh64_matches_default(self):
        default = xxhash.xxh64(b'hello world', 123)
        unlocked = nolock.xxh64(b'hello world', 123)
        self.assertEqual(default.digest(), unlocked.digest())
        self.assertEqual(default.hexdigest(), unlocked.hexdigest())
        self.assertEqual(default.intdigest(), unlocked.intdigest())

    def test_xxh3_64_object(self):
        h = nolock.xxh3_64(b'a')
        self.assertEqual(h.intdigest(), XXH3_64_A[1])

    def test_xxh3_64_matches_default(self):
        default = xxhash.xxh3_64(b'hello world', 123)
        unlocked = nolock.xxh3_64(b'hello world', 123)
        self.assertEqual(default.digest(), unlocked.digest())
        self.assertEqual(default.hexdigest(), unlocked.hexdigest())
        self.assertEqual(default.intdigest(), unlocked.intdigest())

    def test_xxh128_object(self):
        h = nolock.xxh128(b'a')
        self.assertEqual(h.intdigest(), XXH3_128_A[1])

    def test_xxh128_matches_default(self):
        default = xxhash.xxh128(b'hello world', 123)
        unlocked = nolock.xxh128(b'hello world', 123)
        self.assertEqual(default.digest(), unlocked.digest())
        self.assertEqual(default.hexdigest(), unlocked.hexdigest())
        self.assertEqual(default.intdigest(), unlocked.intdigest())


class TestNolockStreaming(unittest.TestCase):
    """Verify that streaming operations work correctly."""

    def test_update(self):
        h = nolock.xxh32()
        h.update(b'a')
        self.assertEqual(h.digest(), nolock.xxh32(b'a').digest())
        h.update(b'b')
        self.assertEqual(h.digest(), nolock.xxh32(b'ab').digest())
        h.update(b'c')
        self.assertEqual(h.digest(), nolock.xxh32(b'abc').digest())

    def test_update_chain(self):
        for typ, data in [
            (nolock.xxh32, b'x' * 100000),
            (nolock.xxh64, b'x' * 100000),
            (nolock.xxh3_64, b'x' * 100000),
            (nolock.xxh128, b'x' * 100000),
        ]:
            with self.subTest(typ=typ):
                h = typ()
                h.update(data)
                self.assertEqual(h.digest(), typ(data).digest())

    def test_reset(self):
        for typ in [nolock.xxh32, nolock.xxh64,
                    nolock.xxh3_64, nolock.xxh128]:
            with self.subTest(typ=typ):
                h = typ()
                initial = h.intdigest()
                for _ in range(10):
                    h.update(os.urandom(64))
                h.reset()
                self.assertEqual(initial, h.intdigest())

    def test_copy(self):
        for typ in [nolock.xxh32, nolock.xxh64,
                    nolock.xxh3_64, nolock.xxh128]:
            with self.subTest(typ=typ):
                a = typ()
                a.update(b'hello world')
                b = a.copy()
                self.assertIs(type(b), typ)
                self.assertEqual(a.digest(), b.digest())
                self.assertEqual(a.intdigest(), b.intdigest())
                self.assertEqual(a.hexdigest(), b.hexdigest())
                b.update(b'more data')
                self.assertNotEqual(a.digest(), b.digest())

    def test_digest_hexdigest_intdigest(self):
        for typ, known in [
            (nolock.xxh32, XXH32_A),
            (nolock.xxh64, XXH64_A),
            (nolock.xxh3_64, XXH3_64_A),
            (nolock.xxh128, XXH3_128_A),
        ]:
            data, expected = known
            with self.subTest(typ=typ):
                h = typ(data)
                self.assertEqual(h.intdigest(), expected)
                self.assertIsInstance(h.digest(), bytes)
                self.assertIsInstance(h.hexdigest(), str)
                self.assertIsInstance(h.intdigest(), int)


class TestNolockTopLevelFunctions(unittest.TestCase):
    """Verify that top-level convenience functions work."""

    def test_xxh32_digest(self):
        self.assertEqual(
            nolock.xxh32_digest(b'a'),
            xxhash.xxh32_digest(b'a'),
        )

    def test_xxh32_hexdigest(self):
        self.assertEqual(
            nolock.xxh32_hexdigest(b'a'),
            xxhash.xxh32_hexdigest(b'a'),
        )

    def test_xxh32_intdigest(self):
        self.assertEqual(
            nolock.xxh32_intdigest(b'a'),
            xxhash.xxh32_intdigest(b'a'),
        )

    def test_xxh64_digest(self):
        self.assertEqual(
            nolock.xxh64_digest(b'a'),
            xxhash.xxh64_digest(b'a'),
        )

    def test_xxh64_hexdigest(self):
        self.assertEqual(
            nolock.xxh64_hexdigest(b'a'),
            xxhash.xxh64_hexdigest(b'a'),
        )

    def test_xxh64_intdigest(self):
        self.assertEqual(
            nolock.xxh64_intdigest(b'a'),
            xxhash.xxh64_intdigest(b'a'),
        )

    def test_xxh3_64_digest(self):
        self.assertEqual(
            nolock.xxh3_64_digest(b'a'),
            xxhash.xxh3_64_digest(b'a'),
        )

    def test_xxh3_64_hexdigest(self):
        self.assertEqual(
            nolock.xxh3_64_hexdigest(b'a'),
            xxhash.xxh3_64_hexdigest(b'a'),
        )

    def test_xxh3_64_intdigest(self):
        self.assertEqual(
            nolock.xxh3_64_intdigest(b'a'),
            xxhash.xxh3_64_intdigest(b'a'),
        )

    def test_xxh128_digest(self):
        self.assertEqual(
            nolock.xxh128_digest(b'a'),
            xxhash.xxh128_digest(b'a'),
        )

    def test_xxh128_hexdigest(self):
        self.assertEqual(
            nolock.xxh128_hexdigest(b'a'),
            xxhash.xxh128_hexdigest(b'a'),
        )

    def test_xxh128_intdigest(self):
        self.assertEqual(
            nolock.xxh128_intdigest(b'a'),
            xxhash.xxh128_intdigest(b'a'),
        )


class TestNolockRepr(unittest.TestCase):
    """Verify that repr() and __module__ use the public module name."""

    def test_repr_xxh32(self):
        h = nolock.xxh32()
        self.assertIn("xxhash.nolock", repr(h))
        self.assertEqual(type(h).__module__, "xxhash.nolock")

    def test_repr_xxh64(self):
        h = nolock.xxh64()
        self.assertIn("xxhash.nolock", repr(h))
        self.assertEqual(type(h).__module__, "xxhash.nolock")

    def test_repr_xxh3_64(self):
        h = nolock.xxh3_64()
        self.assertIn("xxhash.nolock", repr(h))
        self.assertEqual(type(h).__module__, "xxhash.nolock")

    def test_repr_xxh128(self):
        h = nolock.xxh128()
        self.assertIn("xxhash.nolock", repr(h))
        self.assertEqual(type(h).__module__, "xxhash.nolock")


class TestNolockLargeData(unittest.TestCase):
    """Large inputs strictly above ``_GIL_MINSIZE`` (GIL released, no lock)."""

    # C uses ``buf->len > XXHASH_GIL_MINSIZE``, so equality does not release.
    SIZE = xxhash._xxhash._GIL_MINSIZE + 1

    def test_xxh32_large(self):
        data = b'x' * self.SIZE
        self.assertEqual(
            nolock.xxh32(data).digest(),
            xxhash.xxh32(data).digest(),
        )

    def test_xxh64_large(self):
        data = b'x' * self.SIZE
        self.assertEqual(
            nolock.xxh64(data).digest(),
            xxhash.xxh64(data).digest(),
        )

    def test_xxh3_64_large(self):
        data = b'x' * self.SIZE
        self.assertEqual(
            nolock.xxh3_64(data).digest(),
            xxhash.xxh3_64(data).digest(),
        )

    def test_xxh128_large(self):
        data = b'x' * self.SIZE
        self.assertEqual(
            nolock.xxh128(data).digest(),
            xxhash.xxh128(data).digest(),
        )

    def test_streaming_update_large_chunks(self):
        """Streaming chunks that take the GIL-release / no-lock path."""
        h = nolock.xxh64()
        for _ in range(5):
            h.update(b'x' * self.SIZE)
        expected = xxhash.xxh64(b'x' * (5 * self.SIZE)).digest()
        self.assertEqual(h.digest(), expected)


class TestNolockAttributes(unittest.TestCase):
    """Verify that nolock types have the expected attributes."""

    def test_name(self):
        self.assertEqual(nolock.xxh32().name, "XXH32")
        self.assertEqual(nolock.xxh64().name, "XXH64")
        self.assertEqual(nolock.xxh3_64().name, "XXH3_64")
        self.assertEqual(nolock.xxh128().name, "XXH3_128")

    def test_seed_attribute(self):
        h = nolock.xxh32(b'test', 42)
        self.assertEqual(h.seed, 42)

    def test_digest_size(self):
        self.assertEqual(nolock.xxh32().digest_size, 4)
        self.assertEqual(nolock.xxh64().digest_size, 8)
        self.assertEqual(nolock.xxh3_64().digest_size, 8)
        self.assertEqual(nolock.xxh128().digest_size, 16)

    def test_block_size(self):
        self.assertEqual(nolock.xxh32().block_size, 16)
        self.assertEqual(nolock.xxh64().block_size, 32)
        self.assertEqual(nolock.xxh3_64().block_size, 32)
        self.assertEqual(nolock.xxh128().block_size, 64)

    def test_algorithms_available(self):
        self.assertEqual(nolock.algorithms_available, xxhash.algorithms_available)
        self.assertEqual(nolock.algorithms_guaranteed, nolock.algorithms_available)

    def test_version(self):
        self.assertEqual(nolock.VERSION, xxhash.VERSION)
        self.assertEqual(nolock.XXHASH_VERSION, xxhash.XXHASH_VERSION)


class TestNolockTypesAreDistinct(unittest.TestCase):
    """Verify that nolock types are distinct from the default types.

    A regression here (e.g. both modules accidentally pointing at the same
    type object) would silently mix locked and unlocked objects.
    """

    def test_types_are_distinct(self):
        for name in ('xxh32', 'xxh64', 'xxh3_64', 'xxh128'):
            with self.subTest(name=name):
                default_type = getattr(xxhash, name)
                unlocked_type = getattr(nolock, name)
                self.assertIsNot(default_type, unlocked_type)
                self.assertIsNot(type(default_type()), type(unlocked_type()))

    def test_instances_are_not_instances_of_each_other(self):
        for name in ('xxh32', 'xxh64', 'xxh3_64', 'xxh128'):
            with self.subTest(name=name):
                default_type = getattr(xxhash, name)
                unlocked_type = getattr(nolock, name)
                self.assertFalse(isinstance(default_type(), unlocked_type))
                self.assertFalse(isinstance(unlocked_type(), default_type))


ALGOS = ('xxh32', 'xxh64', 'xxh3_64', 'xxh3_128')
ONESHOT_SUFFIXES = ('digest', 'intdigest', 'hexdigest')


class TestNolockPublicSurface(unittest.TestCase):
    """Every public type and function on xxhash.nolock is exercised by name."""

    data = b'hello world'
    seed = 123

    def test_all_exports_exist(self):
        for name in nolock.__all__:
            with self.subTest(name=name):
                self.assertTrue(hasattr(nolock, name))

    def test_xxh128_aliases(self):
        self.assertIs(nolock.xxh128, nolock.xxh3_128)
        self.assertIs(nolock.xxh128_digest, nolock.xxh3_128_digest)
        self.assertIs(nolock.xxh128_intdigest, nolock.xxh3_128_intdigest)
        self.assertIs(nolock.xxh128_hexdigest, nolock.xxh3_128_hexdigest)

    def test_every_type_streaming(self):
        for name in ALGOS:
            with self.subTest(name=name):
                cls = getattr(nolock, name)
                default_cls = getattr(xxhash, name)
                expected = default_cls(self.data, seed=self.seed)

                h = cls(self.data, seed=self.seed)
                self.assertEqual(h.digest(), expected.digest())
                self.assertEqual(h.hexdigest(), expected.hexdigest())
                self.assertEqual(h.intdigest(), expected.intdigest())
                self.assertEqual(h.seed, self.seed)
                self.assertEqual(h.digest_size, h.digestsize)
                self.assertIsInstance(h.block_size, int)
                self.assertIsInstance(h.name, str)

                streamed = cls(seed=self.seed)
                streamed.update(self.data)
                self.assertEqual(streamed.digest(), h.digest())
                streamed.update(data=b'more')
                self.assertNotEqual(streamed.digest(), h.digest())

                copied = h.copy()
                self.assertIs(type(copied), cls)
                self.assertEqual(copied.digest(), h.digest())
                copied.update(b'more')
                self.assertNotEqual(copied.digest(), h.digest())

                streamed.reset()
                self.assertEqual(streamed.intdigest(), cls(seed=self.seed).intdigest())

    def test_every_oneshot_matches_default(self):
        names = [
            f'{algo}_{suffix}'
            for algo in ALGOS
            for suffix in ONESHOT_SUFFIXES
        ]
        names += ['xxh128_digest', 'xxh128_intdigest', 'xxh128_hexdigest']
        for name in names:
            with self.subTest(name=name):
                nfn = getattr(nolock, name)
                dfn = getattr(xxhash, name)
                self.assertEqual(nfn(self.data), dfn(self.data))
                self.assertEqual(nfn(self.data, self.seed), dfn(self.data, self.seed))
                self.assertEqual(
                    nfn(data=self.data, seed=self.seed),
                    dfn(data=self.data, seed=self.seed),
                )

    def test_every_type_repr_and_distinct(self):
        for name in ALGOS:
            with self.subTest(name=name):
                cls = getattr(nolock, name)
                default_cls = getattr(xxhash, name)
                h = cls()
                self.assertIn('xxhash.nolock', repr(h))
                self.assertEqual(type(h).__module__, 'xxhash.nolock')
                self.assertIsNot(cls, default_cls)
                self.assertFalse(isinstance(h, default_cls))
                self.assertFalse(isinstance(default_cls(), cls))

    def test_every_type_large_update(self):
        data = b'x' * (xxhash._xxhash._GIL_MINSIZE + 1)
        for name in ALGOS:
            with self.subTest(name=name):
                cls = getattr(nolock, name)
                h = cls()
                h.update(data)
                self.assertEqual(h.digest(), getattr(xxhash, name)(data).digest())


if __name__ == '__main__':
    unittest.main()
