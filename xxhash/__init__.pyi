from typing import Protocol, final

class _Buffer(Protocol):
    """Objects that support the buffer protocol (PEP 688)."""
    def __buffer__(self, flags: int, /) -> memoryview: ...

_DataType = _Buffer

VERSION: str
XXHASH_VERSION: str

algorithms_available: set[str]
algorithms_guaranteed: set[str]

__all__: list[str] = [
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
    "algorithms_available",
    "algorithms_guaranteed",
]

class _Hasher:
    def __init__(self, data: _DataType = ..., seed: int = ...) -> None: ...
    def update(self, data: _DataType) -> None: ...
    def digest(self) -> bytes: ...
    def hexdigest(self) -> str: ...
    def intdigest(self) -> int: ...
    def copy(self) -> _Hasher: ...
    def reset(self) -> None: ...
    @property
    def digestsize(self) -> int: ...
    @property
    def digest_size(self) -> int: ...
    @property
    def block_size(self) -> int: ...
    @property
    def name(self) -> str: ...
    @property
    def seed(self) -> int: ...

@final
class xxh32(_Hasher): ...

@final
class xxh64(_Hasher): ...

@final
class xxh3_64(_Hasher): ...

@final
class xxh3_128(_Hasher): ...

xxh128 = xxh3_128

def xxh32_digest(data: _DataType, seed: int = ...) -> bytes: ...
def xxh32_hexdigest(data: _DataType, seed: int = ...) -> str: ...
def xxh32_intdigest(data: _DataType, seed: int = ...) -> int: ...

def xxh3_64_digest(data: _DataType, seed: int = ...) -> bytes: ...
def xxh3_64_hexdigest(data: _DataType, seed: int = ...) -> str: ...
def xxh3_64_intdigest(data: _DataType, seed: int = ...) -> int: ...

def xxh3_128_digest(data: _DataType, seed: int = ...) -> bytes: ...
def xxh3_128_hexdigest(data: _DataType, seed: int = ...) -> str: ...
def xxh3_128_intdigest(data: _DataType, seed: int = ...) -> int: ...

xxh64_digest = xxh3_64_digest
xxh64_hexdigest = xxh3_64_hexdigest
xxh64_intdigest = xxh3_64_intdigest

xxh128_digest = xxh3_128_digest
xxh128_hexdigest = xxh3_128_hexdigest
xxh128_intdigest = xxh3_128_intdigest
