from ._xxhash import (
    xxh32,
    xxh32_digest,
    xxh32_intdigest,
    xxh32_hexdigest,
    xxh64,
    xxh64_digest,
    xxh64_intdigest,
    xxh64_hexdigest,
    xxh3_64,
    xxh3_64_digest,
    xxh3_64_intdigest,
    xxh3_64_hexdigest,
    xxh3_128,
    xxh3_128_digest,
    xxh3_128_intdigest,
    xxh3_128_hexdigest,
    XXHASH_VERSION,
)

VERSION = "2.0.0"


xxh128 = xxh3_128
xxh128_hexdigest = xxh3_128_hexdigest
xxh128_intdigest = xxh3_128_intdigest
xxh128_digest = xxh3_128_digest


__all__ = [
    "xxh32",
    "xxh32_digest",
    "xxh32_intdigest",
    "xxh32_hexdigest",
    "xxh64",
    "xxh64_digest",
    "xxh64_intdigest",
    "xxh64_hexdigest",
    "xxh3_64",
    "xxh3_64_digest",
    "xxh3_64_intdigest",
    "xxh3_64_hexdigest",
    "xxh3_128",
    "xxh3_128_digest",
    "xxh3_128_intdigest",
    "xxh3_128_hexdigest",
    "xxh128",
    "xxh128_digest",
    "xxh128_intdigest",
    "xxh128_hexdigest",
    "VERSION",
    "XXHASH_VERSION",
]
