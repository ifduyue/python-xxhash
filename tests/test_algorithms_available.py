import xxhash
import unittest


class TestAliases(unittest.TestCase):
    """xxh128 is an alias of xxh3_128; xxh64 is NOT an alias of xxh3_64."""

    def test_xxh128_is_alias_of_xxh3_128(self):
        self.assertIs(xxhash.xxh128, xxhash.xxh3_128)

    def test_xxh128_digest_is_alias(self):
        self.assertIs(xxhash.xxh128_digest, xxhash.xxh3_128_digest)

    def test_xxh128_hexdigest_is_alias(self):
        self.assertIs(xxhash.xxh128_hexdigest, xxhash.xxh3_128_hexdigest)

    def test_xxh128_intdigest_is_alias(self):
        self.assertIs(xxhash.xxh128_intdigest, xxhash.xxh3_128_intdigest)

    def test_xxh64_is_not_alias_of_xxh3_64(self):
        self.assertIsNot(xxhash.xxh64, xxhash.xxh3_64)

    def test_xxh64_digest_is_not_alias(self):
        self.assertIsNot(xxhash.xxh64_digest, xxhash.xxh3_64_digest)

    def test_xxh64_hexdigest_is_not_alias(self):
        self.assertIsNot(xxhash.xxh64_hexdigest, xxhash.xxh3_64_hexdigest)

    def test_xxh64_intdigest_is_not_alias(self):
        self.assertIsNot(xxhash.xxh64_intdigest, xxhash.xxh3_64_intdigest)


class TestAlgorithmExists(unittest.TestCase):
    def test_xxh32(self):
        xxhash.xxh32
        assert "xxh32" in xxhash.algorithms_available

    def test_xxh64(self):
        xxhash.xxh64
        assert "xxh64" in xxhash.algorithms_available

    def test_xxh3_64(self):
        xxhash.xxh3_64
        assert "xxh3_64" in xxhash.algorithms_available

    def test_xxh128(self):
        xxhash.xxh128
        assert "xxh128" in xxhash.algorithms_available

    def test_xxh3_128(self):
        xxhash.xxh3_128
        assert "xxh3_128" in xxhash.algorithms_available


if __name__ == '__main__':
    unittest.main()
