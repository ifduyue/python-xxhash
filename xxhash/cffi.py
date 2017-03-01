import sys
import struct
import binascii

from xxhash._cffi import ffi, lib

PY3 = sys.version_info[0] == 3

XXHASH_VERSION = "%d.%d.%d" % (lib.XXH_VERSION_MAJOR,
                               lib.XXH_VERSION_MINOR,
                               lib.XXH_VERSION_RELEASE)


class xxh32(object):
    digest_size = digestsize = 4
    block_size = 16

    def __init__(self, input=None, seed=0):
        self.xxhash_state = lib.XXH32_createState()
        self.seed = seed & (2 ** 32 - 1)
        self.reset()
        if input:
            self.update(input)

    def update(self, input):
        if PY3 and isinstance(input, str):
            lib.XXH32_update(self.xxhash_state, input.encode('utf8'), len(input))
        else:
            lib.XXH32_update(self.xxhash_state, input, len(input))

    def intdigest(self):
        return lib.XXH32_digest(self.xxhash_state)

    def digest(self):
        return struct.pack('>I', self.intdigest())

    def hexdigest(self):
        return binascii.hexlify(self.digest())

    def reset(self):
        lib.XXH32_reset(self.xxhash_state, self.seed)

    def copy(self):
        new = type(self)()
        lib.XXH32_copyState(new.xxhash_state, self.xxhash_state)
        new.seed = self.seed
        return new

    def __del__(self):
        lib.XXH32_freeState(self.xxhash_state)


class xxh64(object):
    digest_size = digestsize = 8
    block_size = 32

    def __init__(self, input=None, seed=0):
        self.xxhash_state = lib.XXH64_createState()
        self.seed = seed & (2 ** 64 - 1)
        self.reset()
        if input:
            self.update(input)

    def update(self, input):
        if PY3 and isinstance(input, str):
            lib.XXH64_update(self.xxhash_state, input.encode('utf8'), len(input))
        else:
            lib.XXH64_update(self.xxhash_state, input, len(input))

    def intdigest(self):
        return lib.XXH64_digest(self.xxhash_state)

    def digest(self):
        return struct.pack('>Q', self.intdigest())

    def hexdigest(self):
        return binascii.hexlify(self.digest())

    def reset(self):
        lib.XXH64_reset(self.xxhash_state, self.seed)

    def copy(self):
        new = type(self)()
        lib.XXH64_copyState(new.xxhash_state, self.xxhash_state)
        new.seed = self.seed
        return new

    def __del__(self):
        lib.XXH64_freeState(self.xxhash_state)
