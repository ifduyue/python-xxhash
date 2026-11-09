"""Walltime benchmarks for long XXH3 inputs.

Inputs longer than 240 bytes take XXH3's long-hash path, which is the code
that the x86 runtime dispatcher (SSE2 / AVX2 / AVX512) accelerates. These
benchmarks are meant to be run in CodSpeed walltime mode, so the measured
time reflects the SIMD variant actually selected on the runner's CPU.
"""

import os

import pytest

import xxhash

SEED = 0x9E3779B97F4A7C15

SIZES = {
    "1kb": 1024,
    "64kb": 64 * 1024,
    "1mb": 1024 * 1024,
    "16mb": 16 * 1024 * 1024,
}
DATA = {name: os.urandom(size) for name, size in SIZES.items()}

# Streaming input: 16 MiB fed to update() in 64 KiB chunks.
STREAM_CHUNK = 64 * 1024
STREAM_CHUNKS = [
    memoryview(DATA["16mb"])[i:i + STREAM_CHUNK]
    for i in range(0, len(DATA["16mb"]), STREAM_CHUNK)
]

ONESHOT = {
    "xxh3_64": xxhash.xxh3_64_intdigest,
    "xxh3_128": xxhash.xxh3_128_intdigest,
}
STREAM = {
    "xxh3_64": xxhash.xxh3_64,
    "xxh3_128": xxhash.xxh3_128,
}


@pytest.mark.parametrize("size", list(SIZES))
@pytest.mark.parametrize("algo", list(ONESHOT))
def test_xxh3_long_oneshot(benchmark, algo, size):
    func = ONESHOT[algo]
    data = DATA[size]
    benchmark(func, data)


@pytest.mark.parametrize("size", list(SIZES))
@pytest.mark.parametrize("algo", list(ONESHOT))
def test_xxh3_long_oneshot_seed(benchmark, algo, size):
    func = ONESHOT[algo]
    data = DATA[size]
    benchmark(func, data, SEED)


@pytest.mark.parametrize("algo", list(STREAM))
def test_xxh3_long_stream_update_16mb(benchmark, algo):
    cls = STREAM[algo]

    def run():
        h = cls()
        for chunk in STREAM_CHUNKS:
            h.update(chunk)
        return h.intdigest()

    benchmark(run)
