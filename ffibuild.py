import cffi

ffi = cffi.FFI()

ffi.set_source(
    '_cffi',
    '#include "xxhash.h"',
    sources=['c-xxhash/xxhash.c'],
    include_dirs=['c-xxhash']
)

ffi.cdef('''
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




if __name__ == '__main__':
    ffi.compile()
