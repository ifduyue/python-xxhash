import os
import random

import pytest

import xxhash

SEED_32 = random.randint(0, 0xFFFFFFFF)
SEED_64 = random.randint(0, 0xFFFFFFFFFFFFFFFF)

DATA_5B = os.urandom(5)
DATA_1KB = os.urandom(1000)
DATA_10KB = os.urandom(10000)
DATA_64KB = os.urandom(65536)
DATA_2MB = os.urandom(2 * 1024 * 1024)

# Hash types to bench.
# xxh128 is an alias for xxh3_128 — we skip it to avoid duplicating work.
HASH_TYPES = ["xxh32", "xxh64", "xxh3_64", "xxh3_128"]


def _doc(name):
    """Return a readable test docstring from the function name."""
    return name.replace("test_", "").replace("_", " ").strip()


# ---------------------------------------------------------------------------
#  Oneshot _intdigest  —  xxh32_intdigest(bytes, seed=…)
# ---------------------------------------------------------------------------

@pytest.mark.benchmark
def test_xxh32_intdigest_5b():
    xxhash.xxh32_intdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh32_intdigest_5b_seed_kw():
    xxhash.xxh32_intdigest(DATA_5B, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_intdigest_1kb():
    xxhash.xxh32_intdigest(DATA_1KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_intdigest_10kb():
    xxhash.xxh32_intdigest(DATA_10KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_intdigest_64kb():
    xxhash.xxh32_intdigest(DATA_64KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_intdigest_2mb():
    xxhash.xxh32_intdigest(DATA_2MB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh64_intdigest_5b():
    xxhash.xxh64_intdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh64_intdigest_5b_seed_kw():
    xxhash.xxh64_intdigest(DATA_5B, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_intdigest_1kb():
    xxhash.xxh64_intdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_intdigest_10kb():
    xxhash.xxh64_intdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_intdigest_64kb():
    xxhash.xxh64_intdigest(DATA_64KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_intdigest_2mb():
    xxhash.xxh64_intdigest(DATA_2MB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_5b():
    xxhash.xxh3_64_intdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_5b_seed_kw():
    xxhash.xxh3_64_intdigest(DATA_5B, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_1kb():
    xxhash.xxh3_64_intdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_10kb():
    xxhash.xxh3_64_intdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_64kb():
    xxhash.xxh3_64_intdigest(DATA_64KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_intdigest_2mb():
    xxhash.xxh3_64_intdigest(DATA_2MB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_5b():
    xxhash.xxh3_128_intdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_5b_seed_kw():
    xxhash.xxh3_128_intdigest(DATA_5B, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_1kb():
    xxhash.xxh3_128_intdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_10kb():
    xxhash.xxh3_128_intdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_64kb():
    xxhash.xxh3_128_intdigest(DATA_64KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_intdigest_2mb():
    xxhash.xxh3_128_intdigest(DATA_2MB, seed=SEED_64)


# ---------------------------------------------------------------------------
#  Oneshot _digest  —  xxh32_digest(bytes, seed=…)  → bytes
# ---------------------------------------------------------------------------

@pytest.mark.benchmark
def test_xxh32_digest_5b():
    xxhash.xxh32_digest(DATA_5B)


@pytest.mark.benchmark
def test_xxh32_digest_1kb():
    xxhash.xxh32_digest(DATA_1KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_digest_10kb():
    xxhash.xxh32_digest(DATA_10KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_digest_64kb():
    xxhash.xxh32_digest(DATA_64KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_digest_2mb():
    xxhash.xxh32_digest(DATA_2MB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh64_digest_5b():
    xxhash.xxh64_digest(DATA_5B)


@pytest.mark.benchmark
def test_xxh64_digest_1kb():
    xxhash.xxh64_digest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_digest_10kb():
    xxhash.xxh64_digest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_digest_64kb():
    xxhash.xxh64_digest(DATA_64KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_digest_2mb():
    xxhash.xxh64_digest(DATA_2MB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_digest_5b():
    xxhash.xxh3_64_digest(DATA_5B)


@pytest.mark.benchmark
def test_xxh3_64_digest_1kb():
    xxhash.xxh3_64_digest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_digest_10kb():
    xxhash.xxh3_64_digest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_digest_64kb():
    xxhash.xxh3_64_digest(DATA_64KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_digest_2mb():
    xxhash.xxh3_64_digest(DATA_2MB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_digest_5b():
    xxhash.xxh3_128_digest(DATA_5B)


@pytest.mark.benchmark
def test_xxh3_128_digest_1kb():
    xxhash.xxh3_128_digest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_digest_10kb():
    xxhash.xxh3_128_digest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_digest_64kb():
    xxhash.xxh3_128_digest(DATA_64KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_digest_2mb():
    xxhash.xxh3_128_digest(DATA_2MB, seed=SEED_64)


# ---------------------------------------------------------------------------
#  Oneshot _hexdigest  —  xxh32_hexdigest(bytes, seed=…)  → str
# ---------------------------------------------------------------------------

@pytest.mark.benchmark
def test_xxh32_hexdigest_5b():
    xxhash.xxh32_hexdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh32_hexdigest_1kb():
    xxhash.xxh32_hexdigest(DATA_1KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_hexdigest_10kb():
    xxhash.xxh32_hexdigest(DATA_10KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_hexdigest_64kb():
    xxhash.xxh32_hexdigest(DATA_64KB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh32_hexdigest_2mb():
    xxhash.xxh32_hexdigest(DATA_2MB, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh64_hexdigest_5b():
    xxhash.xxh64_hexdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh64_hexdigest_1kb():
    xxhash.xxh64_hexdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_hexdigest_10kb():
    xxhash.xxh64_hexdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_hexdigest_64kb():
    xxhash.xxh64_hexdigest(DATA_64KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_hexdigest_2mb():
    xxhash.xxh64_hexdigest(DATA_2MB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_hexdigest_5b():
    xxhash.xxh3_64_hexdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh3_64_hexdigest_1kb():
    xxhash.xxh3_64_hexdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_hexdigest_10kb():
    xxhash.xxh3_64_hexdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_hexdigest_64kb():
    xxhash.xxh3_64_hexdigest(DATA_64KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_hexdigest_2mb():
    xxhash.xxh3_64_hexdigest(DATA_2MB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_hexdigest_5b():
    xxhash.xxh3_128_hexdigest(DATA_5B)


@pytest.mark.benchmark
def test_xxh3_128_hexdigest_1kb():
    xxhash.xxh3_128_hexdigest(DATA_1KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_hexdigest_10kb():
    xxhash.xxh3_128_hexdigest(DATA_10KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_hexdigest_64kb():
    xxhash.xxh3_128_hexdigest(DATA_64KB, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_hexdigest_2mb():
    xxhash.xxh3_128_hexdigest(DATA_2MB, seed=SEED_64)


# ---------------------------------------------------------------------------
#  Constructor  —  xxh32(bytes, seed=…)  —  tests tp_vectorcall
# ---------------------------------------------------------------------------

@pytest.mark.benchmark
def test_xxh32_ctor_empty():
    xxhash.xxh32()


@pytest.mark.benchmark
def test_xxh32_ctor():
    xxhash.xxh32(DATA_5B)


@pytest.mark.benchmark
def test_xxh32_ctor_seed_kw():
    xxhash.xxh32(DATA_5B, seed=SEED_32)


@pytest.mark.benchmark
def test_xxh64_ctor_empty():
    xxhash.xxh64()


@pytest.mark.benchmark
def test_xxh64_ctor():
    xxhash.xxh64(DATA_5B, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh64_ctor_seed_kw():
    xxhash.xxh64(DATA_5B, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_ctor_empty():
    xxhash.xxh3_64()


@pytest.mark.benchmark
def test_xxh3_64_ctor():
    xxhash.xxh3_64(DATA_5B, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_64_ctor_seed_kw():
    xxhash.xxh3_64(DATA_5B, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_ctor_empty():
    xxhash.xxh3_128()


@pytest.mark.benchmark
def test_xxh3_128_ctor():
    xxhash.xxh3_128(DATA_5B, seed=SEED_64)


@pytest.mark.benchmark
def test_xxh3_128_ctor_seed_kw():
    xxhash.xxh3_128(DATA_5B, seed=SEED_64)


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
#  Stream (no update): create(data, seed), then finalize.
#  Covers the constructor __init__ path + finalizer.
# ---------------------------------------------------------------------------

# -- Stream 5b (no update) --

@pytest.mark.benchmark
def test_xxh32_stream_intdigest_5b():
    h = xxhash.xxh32(DATA_5B, seed=SEED_32)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh32_stream_digest_5b():
    h = xxhash.xxh32(DATA_5B, seed=SEED_32)
    h.digest()

@pytest.mark.benchmark
def test_xxh32_stream_hexdigest_5b():
    h = xxhash.xxh32(DATA_5B, seed=SEED_32)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh64_stream_intdigest_5b():
    h = xxhash.xxh64(DATA_5B, seed=SEED_64)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh64_stream_digest_5b():
    h = xxhash.xxh64(DATA_5B, seed=SEED_64)
    h.digest()

@pytest.mark.benchmark
def test_xxh64_stream_hexdigest_5b():
    h = xxhash.xxh64(DATA_5B, seed=SEED_64)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh3_64_stream_intdigest_5b():
    h = xxhash.xxh3_64(DATA_5B, seed=SEED_64)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh3_64_stream_digest_5b():
    h = xxhash.xxh3_64(DATA_5B, seed=SEED_64)
    h.digest()

@pytest.mark.benchmark
def test_xxh3_64_stream_hexdigest_5b():
    h = xxhash.xxh3_64(DATA_5B, seed=SEED_64)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh3_128_stream_intdigest_5b():
    h = xxhash.xxh3_128(DATA_5B, seed=SEED_64)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh3_128_stream_digest_5b():
    h = xxhash.xxh3_128(DATA_5B, seed=SEED_64)
    h.digest()

@pytest.mark.benchmark
def test_xxh3_128_stream_hexdigest_5b():
    h = xxhash.xxh3_128(DATA_5B, seed=SEED_64)
    h.hexdigest()


# -- Stream 64kb (no update) --

@pytest.mark.benchmark
def test_xxh32_stream_intdigest_64kb():
    h = xxhash.xxh32(DATA_64KB, seed=SEED_32)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh32_stream_digest_64kb():
    h = xxhash.xxh32(DATA_64KB, seed=SEED_32)
    h.digest()

@pytest.mark.benchmark
def test_xxh32_stream_hexdigest_64kb():
    h = xxhash.xxh32(DATA_64KB, seed=SEED_32)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh64_stream_intdigest_64kb():
    h = xxhash.xxh64(DATA_64KB, seed=SEED_64)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh64_stream_digest_64kb():
    h = xxhash.xxh64(DATA_64KB, seed=SEED_64)
    h.digest()

@pytest.mark.benchmark
def test_xxh64_stream_hexdigest_64kb():
    h = xxhash.xxh64(DATA_64KB, seed=SEED_64)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh3_64_stream_intdigest_64kb():
    h = xxhash.xxh3_64(DATA_64KB, seed=SEED_64)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh3_64_stream_digest_64kb():
    h = xxhash.xxh3_64(DATA_64KB, seed=SEED_64)
    h.digest()

@pytest.mark.benchmark
def test_xxh3_64_stream_hexdigest_64kb():
    h = xxhash.xxh3_64(DATA_64KB, seed=SEED_64)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh3_128_stream_intdigest_64kb():
    h = xxhash.xxh3_128(DATA_64KB, seed=SEED_64)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh3_128_stream_digest_64kb():
    h = xxhash.xxh3_128(DATA_64KB, seed=SEED_64)
    h.digest()

@pytest.mark.benchmark
def test_xxh3_128_stream_hexdigest_64kb():
    h = xxhash.xxh3_128(DATA_64KB, seed=SEED_64)
    h.hexdigest()


# -- Stream 2mb (no update) --

@pytest.mark.benchmark
def test_xxh32_stream_intdigest_2mb():
    h = xxhash.xxh32(DATA_2MB, seed=SEED_32)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh32_stream_digest_2mb():
    h = xxhash.xxh32(DATA_2MB, seed=SEED_32)
    h.digest()

@pytest.mark.benchmark
def test_xxh32_stream_hexdigest_2mb():
    h = xxhash.xxh32(DATA_2MB, seed=SEED_32)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh64_stream_intdigest_2mb():
    h = xxhash.xxh64(DATA_2MB, seed=SEED_64)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh64_stream_digest_2mb():
    h = xxhash.xxh64(DATA_2MB, seed=SEED_64)
    h.digest()

@pytest.mark.benchmark
def test_xxh64_stream_hexdigest_2mb():
    h = xxhash.xxh64(DATA_2MB, seed=SEED_64)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh3_64_stream_intdigest_2mb():
    h = xxhash.xxh3_64(DATA_2MB, seed=SEED_64)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh3_64_stream_digest_2mb():
    h = xxhash.xxh3_64(DATA_2MB, seed=SEED_64)
    h.digest()

@pytest.mark.benchmark
def test_xxh3_64_stream_hexdigest_2mb():
    h = xxhash.xxh3_64(DATA_2MB, seed=SEED_64)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh3_128_stream_intdigest_2mb():
    h = xxhash.xxh3_128(DATA_2MB, seed=SEED_64)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh3_128_stream_digest_2mb():
    h = xxhash.xxh3_128(DATA_2MB, seed=SEED_64)
    h.digest()

@pytest.mark.benchmark
def test_xxh3_128_stream_hexdigest_2mb():
    h = xxhash.xxh3_128(DATA_2MB, seed=SEED_64)
    h.hexdigest()


# ---------------------------------------------------------------------------
#  Stream with update: create(data, seed), update(data), then finalize.
#  Covers constructor + .update() + finalizer with per-object locking.
# ---------------------------------------------------------------------------

# -- Stream 5b with update (GIL-held) --

@pytest.mark.benchmark
def test_xxh32_stream_update_intdigest_5b():
    h = xxhash.xxh32(DATA_5B, seed=SEED_32)
    h.update(DATA_5B)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh32_stream_update_digest_5b():
    h = xxhash.xxh32(DATA_5B, seed=SEED_32)
    h.update(DATA_5B)
    h.digest()

@pytest.mark.benchmark
def test_xxh32_stream_update_hexdigest_5b():
    h = xxhash.xxh32(DATA_5B, seed=SEED_32)
    h.update(DATA_5B)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh64_stream_update_intdigest_5b():
    h = xxhash.xxh64(DATA_5B, seed=SEED_64)
    h.update(DATA_5B)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh64_stream_update_digest_5b():
    h = xxhash.xxh64(DATA_5B, seed=SEED_64)
    h.update(DATA_5B)
    h.digest()

@pytest.mark.benchmark
def test_xxh64_stream_update_hexdigest_5b():
    h = xxhash.xxh64(DATA_5B, seed=SEED_64)
    h.update(DATA_5B)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh3_64_stream_update_intdigest_5b():
    h = xxhash.xxh3_64(DATA_5B, seed=SEED_64)
    h.update(DATA_5B)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh3_64_stream_update_digest_5b():
    h = xxhash.xxh3_64(DATA_5B, seed=SEED_64)
    h.update(DATA_5B)
    h.digest()

@pytest.mark.benchmark
def test_xxh3_64_stream_update_hexdigest_5b():
    h = xxhash.xxh3_64(DATA_5B, seed=SEED_64)
    h.update(DATA_5B)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh3_128_stream_update_intdigest_5b():
    h = xxhash.xxh3_128(DATA_5B, seed=SEED_64)
    h.update(DATA_5B)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh3_128_stream_update_digest_5b():
    h = xxhash.xxh3_128(DATA_5B, seed=SEED_64)
    h.update(DATA_5B)
    h.digest()

@pytest.mark.benchmark
def test_xxh3_128_stream_update_hexdigest_5b():
    h = xxhash.xxh3_128(DATA_5B, seed=SEED_64)
    h.update(DATA_5B)
    h.hexdigest()


# -- Stream 64kb with update (GIL_MINSIZE boundary, GIL-held) --

@pytest.mark.benchmark
def test_xxh32_stream_update_intdigest_64kb():
    h = xxhash.xxh32(DATA_64KB, seed=SEED_32)
    h.update(DATA_64KB)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh32_stream_update_digest_64kb():
    h = xxhash.xxh32(DATA_64KB, seed=SEED_32)
    h.update(DATA_64KB)
    h.digest()

@pytest.mark.benchmark
def test_xxh32_stream_update_hexdigest_64kb():
    h = xxhash.xxh32(DATA_64KB, seed=SEED_32)
    h.update(DATA_64KB)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh64_stream_update_intdigest_64kb():
    h = xxhash.xxh64(DATA_64KB, seed=SEED_64)
    h.update(DATA_64KB)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh64_stream_update_digest_64kb():
    h = xxhash.xxh64(DATA_64KB, seed=SEED_64)
    h.update(DATA_64KB)
    h.digest()

@pytest.mark.benchmark
def test_xxh64_stream_update_hexdigest_64kb():
    h = xxhash.xxh64(DATA_64KB, seed=SEED_64)
    h.update(DATA_64KB)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh3_64_stream_update_intdigest_64kb():
    h = xxhash.xxh3_64(DATA_64KB, seed=SEED_64)
    h.update(DATA_64KB)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh3_64_stream_update_digest_64kb():
    h = xxhash.xxh3_64(DATA_64KB, seed=SEED_64)
    h.update(DATA_64KB)
    h.digest()

@pytest.mark.benchmark
def test_xxh3_64_stream_update_hexdigest_64kb():
    h = xxhash.xxh3_64(DATA_64KB, seed=SEED_64)
    h.update(DATA_64KB)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh3_128_stream_update_intdigest_64kb():
    h = xxhash.xxh3_128(DATA_64KB, seed=SEED_64)
    h.update(DATA_64KB)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh3_128_stream_update_digest_64kb():
    h = xxhash.xxh3_128(DATA_64KB, seed=SEED_64)
    h.update(DATA_64KB)
    h.digest()

@pytest.mark.benchmark
def test_xxh3_128_stream_update_hexdigest_64kb():
    h = xxhash.xxh3_128(DATA_64KB, seed=SEED_64)
    h.update(DATA_64KB)
    h.hexdigest()


# -- Stream 2mb with update (GIL-released) --

@pytest.mark.benchmark
def test_xxh32_stream_update_intdigest_2mb():
    h = xxhash.xxh32(DATA_2MB, seed=SEED_32)
    h.update(DATA_2MB)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh32_stream_update_digest_2mb():
    h = xxhash.xxh32(DATA_2MB, seed=SEED_32)
    h.update(DATA_2MB)
    h.digest()

@pytest.mark.benchmark
def test_xxh32_stream_update_hexdigest_2mb():
    h = xxhash.xxh32(DATA_2MB, seed=SEED_32)
    h.update(DATA_2MB)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh64_stream_update_intdigest_2mb():
    h = xxhash.xxh64(DATA_2MB, seed=SEED_64)
    h.update(DATA_2MB)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh64_stream_update_digest_2mb():
    h = xxhash.xxh64(DATA_2MB, seed=SEED_64)
    h.update(DATA_2MB)
    h.digest()

@pytest.mark.benchmark
def test_xxh64_stream_update_hexdigest_2mb():
    h = xxhash.xxh64(DATA_2MB, seed=SEED_64)
    h.update(DATA_2MB)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh3_64_stream_update_intdigest_2mb():
    h = xxhash.xxh3_64(DATA_2MB, seed=SEED_64)
    h.update(DATA_2MB)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh3_64_stream_update_digest_2mb():
    h = xxhash.xxh3_64(DATA_2MB, seed=SEED_64)
    h.update(DATA_2MB)
    h.digest()

@pytest.mark.benchmark
def test_xxh3_64_stream_update_hexdigest_2mb():
    h = xxhash.xxh3_64(DATA_2MB, seed=SEED_64)
    h.update(DATA_2MB)
    h.hexdigest()

@pytest.mark.benchmark
def test_xxh3_128_stream_update_intdigest_2mb():
    h = xxhash.xxh3_128(DATA_2MB, seed=SEED_64)
    h.update(DATA_2MB)
    h.intdigest()

@pytest.mark.benchmark
def test_xxh3_128_stream_update_digest_2mb():
    h = xxhash.xxh3_128(DATA_2MB, seed=SEED_64)
    h.update(DATA_2MB)
    h.digest()

@pytest.mark.benchmark
def test_xxh3_128_stream_update_hexdigest_2mb():
    h = xxhash.xxh3_128(DATA_2MB, seed=SEED_64)
    h.update(DATA_2MB)
    h.hexdigest()
