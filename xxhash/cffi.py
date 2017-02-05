from __future__ import absolute_import

import cffi
import struct
import binascii

ffibuilder = cffi.FFI()
ffibuilder.cdef('''
#define XXH_VERSION_MAJOR ...
#define XXH_VERSION_MINOR ...
#define XXH_VERSION_RELEASE ...

typedef enum { XXH_OK=0, XXH_ERROR } XXH_errorcode;


typedef unsigned int       XXH32_hash_t;

typedef struct XXH32_state_s XXH32_state_t;   /* incomplete type */
 XXH32_state_t* XXH32_createState(void);
 XXH_errorcode  XXH32_freeState(XXH32_state_t* statePtr);
 void XXH32_copyState(XXH32_state_t* restrict dst_state, const XXH32_state_t* restrict src_state);

 XXH_errorcode XXH32_reset  (XXH32_state_t* statePtr, unsigned int seed);
 XXH_errorcode XXH32_update (XXH32_state_t* statePtr, const void* input, size_t length);
 XXH32_hash_t  XXH32_digest (const XXH32_state_t* statePtr);


typedef unsigned long long XXH64_hash_t;

typedef struct XXH64_state_s XXH64_state_t;   /* incomplete type */
 XXH64_state_t* XXH64_createState(void);
 XXH_errorcode  XXH64_freeState(XXH64_state_t* statePtr);
 void XXH64_copyState(XXH64_state_t* restrict dst_state, const XXH64_state_t* restrict src_state);

 XXH_errorcode XXH64_reset  (XXH64_state_t* statePtr, unsigned long long seed);
 XXH_errorcode XXH64_update (XXH64_state_t* statePtr, const void* input, size_t length);
 XXH64_hash_t  XXH64_digest (const XXH64_state_t* statePtr);
''')


lib = ffibuilder.verify(
    '''#include "xxhash.h"''',
    modulename='xxhash_cffi',
    ext_package='xxhash',
    sources=['c-xxhash/xxhash.c'],
    include_dirs=['c-xxhash']
)


XXHASH_VERSION = "{}.{}.{}".format(lib.XXH_VERSION_MAJOR,
                                   lib.XXH_VERSION_MINOR,
                                   lib.XXH_VERSION_RELEASE)


class xxh32(object):
    def __init__(self, input=None, seed=0):
        self.xxhash_state = ffibuilder.gc(lib.XXH32_createState(), lib.XXH32_freeState)
        self.seed = seed
        self.reset()
        if input:
            lib.XXH32_update(self.xxhash_state, input, len(input))

    def update(self, input):
        lib.XXH32_update(self.xxhash_state, input, len(input))

    def intdigest(self):
        return lib.XXH32_digest(self.xxhash_state)

    def digest(self):
        return struct.pack('>I', self.intdigest())

    def hexdigest(self):
        return binascii.hexlify(self.digest())

    def reset(self):
        lib.XXH32_reset(self.xxhash_state, self.seed)


class xxh64(object):
    def __init__(self, input=None, seed=0):
        self.xxhash_state = ffibuilder.gc(lib.XXH64_createState(), lib.XXH64_freeState)
        self.seed = seed
        self.reset()
        if input:
            lib.XXH64_update(self.xxhash_state, input, len(input))

    def update(self, input):
        lib.XXH64_update(self.xxhash_state, input, len(input))

    def intdigest(self):
        return lib.XXH64_digest(self.xxhash_state)

    def digest(self):
        return struct.pack('>Q', self.intdigest())

    def hexdigest(self):
        return binascii.hexlify(self.digest())

    def reset(self):
        lib.XXH64_reset(self.xxhash_state, self.seed)
