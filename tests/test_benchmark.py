import os
import random

import pytest

import xxhash

DATA_1KB = os.urandom(1000)
DATA_10KB = os.urandom(10000)
DATA_512KB = os.urandom(512000)
DATA_2MB = os.urandom(2 * 1024 * 1024)

SEED_32 = random.randint(0, 0xFFFFFFFF)
SEED_64 = random.randint(0, 0xFFFFFFFFFFFFFFFF)


# -- xxh32 oneshot --


@pytest.mark.benchmark
def test_xxh32_intdigest_1kb():
    xxhash.xxh32_intdigest(DATA_1KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_intdigest_10kb():
    xxhash.xxh32_intdigest(DATA_10KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_intdigest_512kb():
    xxhash.xxh32_intdigest(DATA_512KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_intdigest_2mb():
    xxhash.xxh32_intdigest(DATA_2MB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_hexdigest_1kb():
    xxhash.xxh32_hexdigest(DATA_1KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_hexdigest_10kb():
    xxhash.xxh32_hexdigest(DATA_10KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_hexdigest_512kb():
    xxhash.xxh32_hexdigest(DATA_512KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_hexdigest_2mb():
    xxhash.xxh32_hexdigest(DATA_2MB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_digest_1kb():
    xxhash.xxh32_digest(DATA_1KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_digest_10kb():
    xxhash.xxh32_digest(DATA_10KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_digest_512kb():
    xxhash.xxh32_digest(DATA_512KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_digest_2mb():
    xxhash.xxh32_digest(DATA_2MB, seed=SEED_32)


# -- xxh64 oneshot --


@pytest.mark.benchmark
def test_xxh64_intdigest_1kb():
    xxhash.xxh64_intdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_intdigest_10kb():
    xxhash.xxh64_intdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_intdigest_512kb():
    xxhash.xxh64_intdigest(DATA_512KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_intdigest_2mb():
    xxhash.xxh64_intdigest(DATA_2MB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_hexdigest_1kb():
    xxhash.xxh64_hexdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_hexdigest_10kb():
    xxhash.xxh64_hexdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_hexdigest_512kb():
    xxhash.xxh64_hexdigest(DATA_512KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_hexdigest_2mb():
    xxhash.xxh64_hexdigest(DATA_2MB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_digest_1kb():
    xxhash.xxh64_digest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_digest_10kb():
    xxhash.xxh64_digest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_digest_512kb():
    xxhash.xxh64_digest(DATA_512KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_digest_2mb():
    xxhash.xxh64_digest(DATA_2MB, seed=SEED_64)


# -- xxh3_64 oneshot --


@pytest.mark.benchmark
def test_xxh3_64_intdigest_1kb():
    xxhash.xxh3_64_intdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_10kb():
    xxhash.xxh3_64_intdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_512kb():
    xxhash.xxh3_64_intdigest(DATA_512KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_2mb():
    xxhash.xxh3_64_intdigest(DATA_2MB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_hexdigest_1kb():
    xxhash.xxh3_64_hexdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_hexdigest_10kb():
    xxhash.xxh3_64_hexdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_hexdigest_512kb():
    xxhash.xxh3_64_hexdigest(DATA_512KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_hexdigest_2mb():
    xxhash.xxh3_64_hexdigest(DATA_2MB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_digest_1kb():
    xxhash.xxh3_64_digest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_digest_10kb():
    xxhash.xxh3_64_digest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_digest_512kb():
    xxhash.xxh3_64_digest(DATA_512KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_digest_2mb():
    xxhash.xxh3_64_digest(DATA_2MB, seed=SEED_64)


# -- xxh3_128 oneshot --


@pytest.mark.benchmark
def test_xxh3_128_intdigest_1kb():
    xxhash.xxh3_128_intdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_10kb():
    xxhash.xxh3_128_intdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_512kb():
    xxhash.xxh3_128_intdigest(DATA_512KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_2mb():
    xxhash.xxh3_128_intdigest(DATA_2MB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_hexdigest_1kb():
    xxhash.xxh3_128_hexdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_hexdigest_10kb():
    xxhash.xxh3_128_hexdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_hexdigest_512kb():
    xxhash.xxh3_128_hexdigest(DATA_512KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_hexdigest_2mb():
    xxhash.xxh3_128_hexdigest(DATA_2MB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_digest_1kb():
    xxhash.xxh3_128_digest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_digest_10kb():
    xxhash.xxh3_128_digest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_digest_512kb():
    xxhash.xxh3_128_digest(DATA_512KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_digest_2mb():
    xxhash.xxh3_128_digest(DATA_2MB, seed=SEED_64)


# -- xxh32 streaming intdigest --


@pytest.mark.benchmark
def test_xxh32_streaming_intdigest_1kb():
    h = xxhash.xxh32(seed=SEED_32)
    for _ in range(10):
        h.update(DATA_1KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh32_streaming_intdigest_10kb():
    h = xxhash.xxh32(seed=SEED_32)
    for _ in range(10):
        h.update(DATA_10KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh32_streaming_intdigest_512kb():
    h = xxhash.xxh32(seed=SEED_32)
    for _ in range(10):
        h.update(DATA_512KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh32_streaming_intdigest_2mb():
    h = xxhash.xxh32(seed=SEED_32)
    for _ in range(10):
        h.update(DATA_2MB)
    h.intdigest()


# -- xxh64 streaming intdigest --


@pytest.mark.benchmark
def test_xxh64_streaming_intdigest_1kb():
    h = xxhash.xxh64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_1KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh64_streaming_intdigest_10kb():
    h = xxhash.xxh64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_10KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh64_streaming_intdigest_512kb():
    h = xxhash.xxh64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_512KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh64_streaming_intdigest_2mb():
    h = xxhash.xxh64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_2MB)
    h.intdigest()


# -- xxh3_64 streaming intdigest --


@pytest.mark.benchmark
def test_xxh3_64_streaming_intdigest_1kb():
    h = xxhash.xxh3_64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_1KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh3_64_streaming_intdigest_10kb():
    h = xxhash.xxh3_64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_10KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh3_64_streaming_intdigest_512kb():
    h = xxhash.xxh3_64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_512KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh3_64_streaming_intdigest_2mb():
    h = xxhash.xxh3_64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_2MB)
    h.intdigest()


# -- xxh3_128 streaming intdigest --


@pytest.mark.benchmark
def test_xxh3_128_streaming_intdigest_1kb():
    h = xxhash.xxh3_128(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_1KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh3_128_streaming_intdigest_10kb():
    h = xxhash.xxh3_128(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_10KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh3_128_streaming_intdigest_512kb():
    h = xxhash.xxh3_128(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_512KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh3_128_streaming_intdigest_2mb():
    h = xxhash.xxh3_128(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_2MB)
    h.intdigest()


# -- xxh32 streaming hexdigest --


@pytest.mark.benchmark
def test_xxh32_streaming_hexdigest_1kb():
    h = xxhash.xxh32(seed=SEED_32)
    for _ in range(10):
        h.update(DATA_1KB)
    h.hexdigest()


@pytest.mark.benchmark
def test_xxh32_streaming_hexdigest_10kb():
    h = xxhash.xxh32(seed=SEED_32)
    for _ in range(10):
        h.update(DATA_10KB)
    h.hexdigest()


@pytest.mark.benchmark
def test_xxh32_streaming_hexdigest_512kb():
    h = xxhash.xxh32(seed=SEED_32)
    for _ in range(10):
        h.update(DATA_512KB)
    h.hexdigest()


@pytest.mark.benchmark
def test_xxh32_streaming_hexdigest_2mb():
    h = xxhash.xxh32(seed=SEED_32)
    for _ in range(10):
        h.update(DATA_2MB)
    h.hexdigest()


# -- xxh64 streaming hexdigest --


@pytest.mark.benchmark
def test_xxh64_streaming_hexdigest_1kb():
    h = xxhash.xxh64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_1KB)
    h.hexdigest()


@pytest.mark.benchmark
def test_xxh64_streaming_hexdigest_10kb():
    h = xxhash.xxh64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_10KB)
    h.hexdigest()


@pytest.mark.benchmark
def test_xxh64_streaming_hexdigest_512kb():
    h = xxhash.xxh64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_512KB)
    h.hexdigest()


@pytest.mark.benchmark
def test_xxh64_streaming_hexdigest_2mb():
    h = xxhash.xxh64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_2MB)
    h.hexdigest()


# -- xxh3_64 streaming hexdigest --


@pytest.mark.benchmark
def test_xxh3_64_streaming_hexdigest_1kb():
    h = xxhash.xxh3_64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_1KB)
    h.hexdigest()


@pytest.mark.benchmark
def test_xxh3_64_streaming_hexdigest_10kb():
    h = xxhash.xxh3_64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_10KB)
    h.hexdigest()


@pytest.mark.benchmark
def test_xxh3_64_streaming_hexdigest_512kb():
    h = xxhash.xxh3_64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_512KB)
    h.hexdigest()


@pytest.mark.benchmark
def test_xxh3_64_streaming_hexdigest_2mb():
    h = xxhash.xxh3_64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_2MB)
    h.hexdigest()


# -- xxh3_128 streaming hexdigest --


@pytest.mark.benchmark
def test_xxh3_128_streaming_hexdigest_1kb():
    h = xxhash.xxh3_128(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_1KB)
    h.hexdigest()


@pytest.mark.benchmark
def test_xxh3_128_streaming_hexdigest_10kb():
    h = xxhash.xxh3_128(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_10KB)
    h.hexdigest()


@pytest.mark.benchmark
def test_xxh3_128_streaming_hexdigest_512kb():
    h = xxhash.xxh3_128(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_512KB)
    h.hexdigest()


@pytest.mark.benchmark
def test_xxh3_128_streaming_hexdigest_2mb():
    h = xxhash.xxh3_128(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_2MB)
    h.hexdigest()


# -- xxh32 streaming digest --


@pytest.mark.benchmark
def test_xxh32_streaming_digest_1kb():
    h = xxhash.xxh32(seed=SEED_32)
    for _ in range(10):
        h.update(DATA_1KB)
    h.digest()


@pytest.mark.benchmark
def test_xxh32_streaming_digest_10kb():
    h = xxhash.xxh32(seed=SEED_32)
    for _ in range(10):
        h.update(DATA_10KB)
    h.digest()


@pytest.mark.benchmark
def test_xxh32_streaming_digest_512kb():
    h = xxhash.xxh32(seed=SEED_32)
    for _ in range(10):
        h.update(DATA_512KB)
    h.digest()


@pytest.mark.benchmark
def test_xxh32_streaming_digest_2mb():
    h = xxhash.xxh32(seed=SEED_32)
    for _ in range(10):
        h.update(DATA_2MB)
    h.digest()


# -- xxh64 streaming digest --


@pytest.mark.benchmark
def test_xxh64_streaming_digest_1kb():
    h = xxhash.xxh64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_1KB)
    h.digest()


@pytest.mark.benchmark
def test_xxh64_streaming_digest_10kb():
    h = xxhash.xxh64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_10KB)
    h.digest()


@pytest.mark.benchmark
def test_xxh64_streaming_digest_512kb():
    h = xxhash.xxh64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_512KB)
    h.digest()


@pytest.mark.benchmark
def test_xxh64_streaming_digest_2mb():
    h = xxhash.xxh64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_2MB)
    h.digest()


# -- xxh3_64 streaming digest --


@pytest.mark.benchmark
def test_xxh3_64_streaming_digest_1kb():
    h = xxhash.xxh3_64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_1KB)
    h.digest()


@pytest.mark.benchmark
def test_xxh3_64_streaming_digest_10kb():
    h = xxhash.xxh3_64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_10KB)
    h.digest()


@pytest.mark.benchmark
def test_xxh3_64_streaming_digest_512kb():
    h = xxhash.xxh3_64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_512KB)
    h.digest()


@pytest.mark.benchmark
def test_xxh3_64_streaming_digest_2mb():
    h = xxhash.xxh3_64(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_2MB)
    h.digest()


# -- xxh3_128 streaming digest --


@pytest.mark.benchmark
def test_xxh3_128_streaming_digest_1kb():
    h = xxhash.xxh3_128(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_1KB)
    h.digest()


@pytest.mark.benchmark
def test_xxh3_128_streaming_digest_10kb():
    h = xxhash.xxh3_128(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_10KB)
    h.digest()


@pytest.mark.benchmark
def test_xxh3_128_streaming_digest_512kb():
    h = xxhash.xxh3_128(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_512KB)
    h.digest()


@pytest.mark.benchmark
def test_xxh3_128_streaming_digest_2mb():
    h = xxhash.xxh3_128(seed=SEED_64)
    for _ in range(10):
        h.update(DATA_2MB)
    h.digest()
