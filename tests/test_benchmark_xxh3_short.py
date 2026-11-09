"""Walltime control benchmarks for short XXH3 inputs.

Inputs of at most 240 bytes take XXH3's short-hash paths, which have no SIMD
variants. The x86 runtime dispatcher should therefore not make them faster;
these benchmarks check that it does not make them slower either. The seeded
and streaming variants still go through the ``*_dispatch`` wrappers, so they
also expose any per-call dispatch overhead. XXH64 is included as a control
that never touches the dispatcher.
"""

import os

import pytest

import xxhash

SEED = 0x9E3779B97F4A7C15

# 16 B: 9-16 byte path, 64 B: 17-128 byte path, 240 B: 129-240 byte path.
SIZES = {
    "16b": 16,
    "64b": 64,
    "240b": 240,
}
DATA = {name: os.urandom(size) for name, size in SIZES.items()}

ONESHOT = {
    "xxh3_64": xxhash.xxh3_64_intdigest,
    "xxh3_128": xxhash.xxh3_128_intdigest,
}
STREAM = {
    "xxh3_64": xxhash.xxh3_64,
    "xxh3_128": xxhash.xxh3_128,
}


@pytest.mark.benchmark
@pytest.mark.parametrize("size", list(SIZES))
@pytest.mark.parametrize("algo", list(ONESHOT))
def test_xxh3_short_oneshot(benchmark, algo, size):
    func = ONESHOT[algo]
    data = DATA[size]
    benchmark(func, data)


@pytest.mark.benchmark
@pytest.mark.parametrize("size", list(SIZES))
@pytest.mark.parametrize("algo", list(ONESHOT))
def test_xxh3_short_oneshot_seed(benchmark, algo, size):
    func = ONESHOT[algo]
    data = DATA[size]
    benchmark(func, data, SEED)


@pytest.mark.benchmark
@pytest.mark.parametrize("algo", list(STREAM))
def test_xxh3_short_stream_update_64b(benchmark, algo):
    cls = STREAM[algo]
    data = DATA["64b"]

    def run():
        h = cls()
        h.update(data)
        return h.intdigest()

    benchmark(run)


XXH64_DATA = {
    "64b": DATA["64b"],
    "1mb": os.urandom(1024 * 1024),
}


@pytest.mark.benchmark
@pytest.mark.parametrize("size", list(XXH64_DATA))
def test_xxh64_control(benchmark, size):
    benchmark(xxhash.xxh64_intdigest, XXH64_DATA[size])
