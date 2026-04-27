import hashlib
import os
import random

import pytest

import xxhash

SEED_32 = random.randint(0, 0xFFFFFFFF)
SEED_64 = random.randint(0, 0xFFFFFFFFFFFFFFFF)

DATA_5B = os.urandom(5)
DATA_1KB = os.urandom(1000)
DATA_10KB = os.urandom(10000)


# ── macro bench: larger inputs where hashing dominates ───────────────


@pytest.mark.benchmark
def test_xxh32_intdigest_1kb():
    xxhash.xxh32_intdigest(DATA_1KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_1kb():
    xxhash.xxh3_64_intdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_10kb():
    xxhash.xxh3_64_intdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_1kb():
    xxhash.xxh3_128_intdigest(DATA_1KB, seed=SEED_64)


# ── micro bench: tiny inputs where call overhead dominates ───────────


@pytest.mark.benchmark
def test_xxh32_intdigest_5b():
    xxhash.xxh32_intdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh32_intdigest_5b_seed():
    xxhash.xxh32_intdigest(DATA_5B, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_intdigest_5b_seed_kw():
    xxhash.xxh32_intdigest(DATA_5B, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh64_intdigest_5b():
    xxhash.xxh64_intdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh64_intdigest_5b_seed_kw():
    xxhash.xxh64_intdigest(DATA_5B, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_5b():
    xxhash.xxh3_64_intdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_5b_seed_kw():
    xxhash.xxh3_64_intdigest(DATA_5B, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_5b():
    xxhash.xxh3_128_intdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh32_hexdigest_5b():
    xxhash.xxh32_hexdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh64_hexdigest_5b():
    xxhash.xxh64_hexdigest(DATA_5B)


# ── str input (tests _get_buffer_or_str UTF-8 encoding path) ────────

DATA_STR = "hello world"


@pytest.mark.benchmark
def test_xxh32_intdigest_str():
    xxhash.xxh32_intdigest(DATA_STR)


@pytest.mark.benchmark
def test_xxh64_intdigest_str():
    xxhash.xxh64_intdigest(DATA_STR)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_str():
    xxhash.xxh3_64_intdigest(DATA_STR)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_str():
    xxhash.xxh3_128_intdigest(DATA_STR)


# ── type constructor (tests tp_vectorcall) ──────────────────────────


@pytest.mark.benchmark
def test_xxh32_ctor():
    xxhash.xxh32(DATA_STR)


@pytest.mark.benchmark
def test_xxh32_ctor_seed():
    xxhash.xxh32(DATA_STR, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_ctor_empty():
    xxhash.xxh32()


@pytest.mark.benchmark
def test_xxh64_ctor():
    xxhash.xxh64(DATA_STR, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_ctor():
    xxhash.xxh3_64(DATA_STR, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_ctor():
    xxhash.xxh3_128(DATA_STR, seed=SEED_64)
