import os
import random

import pytest

import xxhash

DATA_1KB = os.urandom(1000)
DATA_10KB = os.urandom(10000)

SEED_32 = random.randint(0, 0xFFFFFFFF)
SEED_64 = random.randint(0, 0xFFFFFFFFFFFFFFFF)


# -- xxh32 oneshot --


@pytest.mark.benchmark
def test_xxh32_intdigest_1kb():
    xxhash.xxh32_intdigest(DATA_1KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_intdigest_10kb():
    xxhash.xxh32_intdigest(DATA_10KB, seed=SEED_32)


# -- xxh64 oneshot --


@pytest.mark.benchmark
def test_xxh64_intdigest_1kb():
    xxhash.xxh64_intdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_intdigest_10kb():
    xxhash.xxh64_intdigest(DATA_10KB, seed=SEED_64)


# -- xxh3_64 oneshot --


@pytest.mark.benchmark
def test_xxh3_64_intdigest_1kb():
    xxhash.xxh3_64_intdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_10kb():
    xxhash.xxh3_64_intdigest(DATA_10KB, seed=SEED_64)


# -- xxh3_128 oneshot --


@pytest.mark.benchmark
def test_xxh3_128_intdigest_1kb():
    xxhash.xxh3_128_intdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_10kb():
    xxhash.xxh3_128_intdigest(DATA_10KB, seed=SEED_64)


# -- xxh32 streaming --


@pytest.mark.benchmark
def test_xxh32_streaming_1kb():
    h = xxhash.xxh32(seed=SEED_32)
    h.update(DATA_1KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh32_streaming_10kb():
    h = xxhash.xxh32(seed=SEED_32)
    h.update(DATA_10KB)
    h.intdigest()


# -- xxh64 streaming --


@pytest.mark.benchmark
def test_xxh64_streaming_1kb():
    h = xxhash.xxh64(seed=SEED_64)
    h.update(DATA_1KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh64_streaming_10kb():
    h = xxhash.xxh64(seed=SEED_64)
    h.update(DATA_10KB)
    h.intdigest()


# -- xxh3_64 streaming --


@pytest.mark.benchmark
def test_xxh3_64_streaming_1kb():
    h = xxhash.xxh3_64(seed=SEED_64)
    h.update(DATA_1KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh3_64_streaming_10kb():
    h = xxhash.xxh3_64(seed=SEED_64)
    h.update(DATA_10KB)
    h.intdigest()


# -- xxh3_128 streaming --


@pytest.mark.benchmark
def test_xxh3_128_streaming_1kb():
    h = xxhash.xxh3_128(seed=SEED_64)
    h.update(DATA_1KB)
    h.intdigest()


@pytest.mark.benchmark
def test_xxh3_128_streaming_10kb():
    h = xxhash.xxh3_128(seed=SEED_64)
    h.update(DATA_10KB)
    h.intdigest()
