/*
 * Copyright (c) 2014-2026, Yue Du
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 *     * Redistributions of source code must retain the above copyright notice,
 *       this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright notice,
 *       this list of conditions and the following disclaimer in the documentation
 *       and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

/* This module provides an interface to xxhash, an extremely fast
 non-cryptographic hash algorithm.
 *
 * All four algorithms (XXH32, XXH64, XXH3_64, XXH3_128) share a single
 * C type (xxhash.xxhash), distinguished by the 'algo' enum field.
 * This follows CPython's _hashlib pattern where md5/sha1/sha256 etc.
 * are all the same HASH type differentiated only by the digest context. */

#include <Python.h>
#include <string.h>

#include "xxhash.h"

/* ------------------------------------------------------------------ */
/*  Lock type & helpers                                               */
/* ------------------------------------------------------------------ */
#if PY_VERSION_HEX >= 0x030d0000 /* Python 3.13+: always-on PyMutex (3.15+ style) */
#  define XXHASH_LOCK_FIELD      PyMutex mutex;
#  define XXHASH_LOCK_INIT(o)    ((void)((o)->mutex = (PyMutex){0}))
#  define XXHASH_LOCK_IS_ACTIVE(o)  1
#  define XXHASH_LOCK_MAYBE_INIT(o, len)  ((void)0)
#  define XXHASH_LOCK_FINI(o)    ((void)0)
#  define XXHASH_LOCK_ACQUIRE(o)          PyMutex_Lock(&(o)->mutex)
#  define XXHASH_LOCK_ACQUIRE_BLOCKING(o) XXHASH_LOCK_ACQUIRE(o)
#  define XXHASH_LOCK_RELEASE(o)       PyMutex_Unlock(&(o)->mutex)
#else  /* Python 3.9-3.12: PyThread_type_lock */
#  define XXHASH_LOCK_FIELD      PyThread_type_lock lock;
#  define XXHASH_LOCK_INIT(o)    ((o)->lock = NULL)
#  define XXHASH_LOCK_IS_ACTIVE(o)  ((o)->lock != NULL)
/* Lazy allocation on first large update */
#  define XXHASH_LOCK_MAYBE_INIT(o, len)                                 \
    do {                                                                 \
        if ((o)->lock == NULL && (len) >= XXHASH_GIL_MINSIZE) {          \
            (o)->lock = PyThread_allocate_lock();                        \
            /* fail? lock stays NULL, fall back to non-threaded code. */ \
        }                                                                \
    } while (0)
#  define XXHASH_LOCK_FINI(o)    do { if ((o)->lock)                 \
                                      PyThread_free_lock((o)->lock); \
                                  } while (0)
/* Acquire lock when GIL is already released — simple blocking acquire.
 * Only acquires if lock has been allocated (lazy init). */
#  define XXHASH_LOCK_ACQUIRE_BLOCKING(o)                \
    do {                                                 \
        if ((o)->lock) {                                 \
            PyThread_acquire_lock((o)->lock, WAIT_LOCK); \
        }                                                \
    } while (0)

/* Acquire lock with the GIL held — non-blocking try first, then release
 * GIL and block if contested (matches hashlib's ENTER_HASHLIB in 3.9-3.12).
 * Only acquires if lock has been allocated (lazy init). */
#  define XXHASH_LOCK_ACQUIRE(o)                                  \
    do {                                                          \
        if ((o)->lock) {                                          \
            if (!PyThread_acquire_lock((o)->lock, NOWAIT_LOCK)) { \
                /* Lock contested – release GIL while waiting. */ \
                Py_BEGIN_ALLOW_THREADS                            \
                PyThread_acquire_lock((o)->lock, WAIT_LOCK);      \
                Py_END_ALLOW_THREADS                              \
            }                                                     \
        }                                                         \
    } while (0)

#  define XXHASH_LOCK_RELEASE(o)              \
    do {                                      \
        if ((o)->lock) {                      \
            PyThread_release_lock((o)->lock); \
        }                                     \
    } while (0)
#endif

/* Data size threshold for releasing the GIL during hash. */
#define XXHASH_GIL_MINSIZE  65536

#define TOSTRING(x) #x
#define VALUE_TO_STRING(x) TOSTRING(x)
#define XXHASH_VERSION XXH_VERSION_MAJOR.XXH_VERSION_MINOR.XXH_VERSION_RELEASE

#define XXH32_DIGESTSIZE 4
#define XXH32_BLOCKSIZE 16
#define XXH64_DIGESTSIZE 8
#define XXH64_BLOCKSIZE 32
#define XXH128_DIGESTSIZE 16
#define XXH128_BLOCKSIZE 64

#ifndef Py_ALWAYS_INLINE
#  define Py_ALWAYS_INLINE
#endif

/* Algorithm identifier — all XXH variants share one C type.
 * Values are prefixed to avoid collision with XXH32()/XXH64() function names
 * from the xxhash.h header. */
typedef enum {
    XXH_ALGO_XXH32,
    XXH_ALGO_XXH64,
    XXH_ALGO_XXH3_64,
    XXH_ALGO_XXH3_128,
} XXH_Algo;

/* Single struct for all algorithms, following CPython _hashlib's one-type
 * pattern: algorithm differences live in the state/union, not the type. */
typedef struct {
    PyObject_HEAD
    union {
        XXH32_state_t *xxh32;
        XXH64_state_t *xxh64;
        XXH3_state_t  *xxh3;
    } state;
    XXH_Algo algo;
    XXH64_hash_t seed;       /* stored as XXH64 for uniformity across all algorithms */
    XXHASH_LOCK_FIELD
} XXHASHObject;

/* Per-algorithm metadata table. */
typedef struct {
    const char *name;
    unsigned char digest_size;
    unsigned char block_size;
} XXH_AlgoInfo;

static const XXH_AlgoInfo XXH_ALGO_TABLE[] = {
    [XXH_ALGO_XXH32]   = { "XXH32",    XXH32_DIGESTSIZE,  XXH32_BLOCKSIZE },
    [XXH_ALGO_XXH64]   = { "XXH64",    XXH64_DIGESTSIZE,  XXH64_BLOCKSIZE },
    [XXH_ALGO_XXH3_64] = { "XXH3_64",  XXH64_DIGESTSIZE,  XXH64_BLOCKSIZE },
    [XXH_ALGO_XXH3_128]= { "XXH3_128", XXH128_DIGESTSIZE, XXH128_BLOCKSIZE},
};

/* ------------------------------------------------------------------ */
/*  Per-algorithm dispatch table — replaces all switch(algo)          */
/* ------------------------------------------------------------------ */

/* Wrappers to normalize function signatures across algorithms. */
static inline Py_ALWAYS_INLINE void
_algo_xxh32_reset(void *state, XXH64_hash_t seed)
{
    XXH32_reset((XXH32_state_t *)state, (XXH32_hash_t)seed);
}
static inline Py_ALWAYS_INLINE void
_algo_xxh64_reset(void *state, XXH64_hash_t seed)
{
    XXH64_reset((XXH64_state_t *)state, seed);
}
static inline Py_ALWAYS_INLINE void
_algo_xxh3_64_reset(void *state, XXH64_hash_t seed)
{
    XXH3_64bits_reset_withSeed((XXH3_state_t *)state, seed);
}
static inline Py_ALWAYS_INLINE void
_algo_xxh3_128_reset(void *state, XXH64_hash_t seed)
{
    XXH3_128bits_reset_withSeed((XXH3_state_t *)state, seed);
}

static inline Py_ALWAYS_INLINE void
_algo_xxh32_digest(void *state, void *out)
{
    XXH32_hash_t h = XXH32_digest((XXH32_state_t *)state);
    XXH32_canonicalFromHash((XXH32_canonical_t *)out, h);
}
static inline Py_ALWAYS_INLINE void
_algo_xxh64_digest(void *state, void *out)
{
    XXH64_hash_t h = XXH64_digest((XXH64_state_t *)state);
    XXH64_canonicalFromHash((XXH64_canonical_t *)out, h);
}
static inline Py_ALWAYS_INLINE void
_algo_xxh3_64_digest(void *state, void *out)
{
    XXH64_hash_t h = XXH3_64bits_digest((XXH3_state_t *)state);
    XXH64_canonicalFromHash((XXH64_canonical_t *)out, h);
}
static inline Py_ALWAYS_INLINE void
_algo_xxh3_128_digest(void *state, void *out) {
    XXH128_hash_t h = XXH3_128bits_digest((XXH3_state_t *)state);
    XXH128_canonicalFromHash((XXH128_canonical_t *)out, h);
}

static inline Py_ALWAYS_INLINE PyObject *
_algo_xxh32_intdigest(void *state)
{
    return PyLong_FromUnsignedLong(XXH32_digest((XXH32_state_t *)state));
}
static inline Py_ALWAYS_INLINE PyObject *
_algo_xxh64_intdigest(void *state)
{
    return PyLong_FromUnsignedLongLong(XXH64_digest((XXH64_state_t *)state));
}
static inline Py_ALWAYS_INLINE PyObject *
_algo_xxh3_64_intdigest(void *state)
{
    return PyLong_FromUnsignedLongLong(XXH3_64bits_digest((XXH3_state_t *)state));
}

static inline Py_ALWAYS_INLINE PyObject *
_algo_xxh3_128_intdigest(void *state) {
    XXH128_hash_t h = XXH3_128bits_digest((XXH3_state_t *)state);
    PyObject *sixtyfour = PyLong_FromLong(64);
    PyObject *low  = PyLong_FromUnsignedLongLong(h.low64);
    PyObject *high = PyLong_FromUnsignedLongLong(h.high64);
    PyObject *result = NULL;
    if (sixtyfour && low && high) {
        PyObject *shifted = PyNumber_Lshift(high, sixtyfour);
        if (shifted) {
            result = PyNumber_Add(shifted, low);
            Py_DECREF(shifted);
        }
    }
    Py_XDECREF(high);
    Py_XDECREF(low);
    Py_XDECREF(sixtyfour);
    return result;
}

typedef struct {
    void *(*create_state)(void);
    void  (*free_state)(void *state);
    void  (*reset)(void *state, XXH64_hash_t seed);
    void  (*update)(void *state, const void *data, size_t len);
    void  (*digest)(void *state, void *out);  /* canonical bytes to out */
    PyObject *(*intdigest)(void *state);
    void  (*copy_state)(void *dst, const void *src);
} XXH_AlgoDispatch;

static const XXH_AlgoDispatch XXH_DISPATCH[] = {
    [XXH_ALGO_XXH32] = {
        .create_state = (void *(*)(void))XXH32_createState,
        .free_state   = (void  (*)(void *))XXH32_freeState,
        .reset        = _algo_xxh32_reset,
        .update       = (void  (*)(void *, const void *, size_t))XXH32_update,
        .digest       = _algo_xxh32_digest,
        .intdigest    = _algo_xxh32_intdigest,
        .copy_state   = (void  (*)(void *, const void *))XXH32_copyState,
    },
    [XXH_ALGO_XXH64] = {
        .create_state = (void *(*)(void))XXH64_createState,
        .free_state   = (void  (*)(void *))XXH64_freeState,
        .reset        = _algo_xxh64_reset,
        .update       = (void  (*)(void *, const void *, size_t))XXH64_update,
        .digest       = _algo_xxh64_digest,
        .intdigest    = _algo_xxh64_intdigest,
        .copy_state   = (void  (*)(void *, const void *))XXH64_copyState,
    },
    [XXH_ALGO_XXH3_64] = {
        .create_state = (void *(*)(void))XXH3_createState,
        .free_state   = (void  (*)(void *))XXH3_freeState,
        .reset        = _algo_xxh3_64_reset,
        .update       = (void  (*)(void *, const void *, size_t))XXH3_64bits_update,
        .digest       = _algo_xxh3_64_digest,
        .intdigest    = _algo_xxh3_64_intdigest,
        .copy_state   = (void  (*)(void *, const void *))XXH3_copyState,
    },
    [XXH_ALGO_XXH3_128] = {
        .create_state = (void *(*)(void))XXH3_createState,
        .free_state   = (void  (*)(void *))XXH3_freeState,
        .reset        = _algo_xxh3_128_reset,
        .update       = (void  (*)(void *, const void *, size_t))XXH3_128bits_update,
        .digest       = _algo_xxh3_128_digest,
        .intdigest    = _algo_xxh3_128_intdigest,
        .copy_state   = (void  (*)(void *, const void *))XXH3_copyState,
    },
};

/* Helper: return opaque state pointer for the current algo. */
static inline void *
_xxhash_state_ptr(XXHASHObject *self)
{
    /* xxh3 is used for both XXH3_64 and XXH3_128 */
    if (self->algo == XXH_ALGO_XXH32)
        return (void *)self->state.xxh32;
    if (self->algo == XXH_ALGO_XXH64)
        return (void *)self->state.xxh64;
    return (void *)self->state.xxh3;
}

/* Macro: single dispatch call. */
#define XXH_DISPATCH(self, field)  (XXH_DISPATCH[(self)->algo].field)

/* Macro: call with state pointer. */
#define XXH_DISPATCH_CALL(self, field, ...)                                    \
    (XXH_DISPATCH[(self)->algo].field(_xxhash_state_ptr(self), ##__VA_ARGS__))

/* Module state: holds the heap type. */
typedef struct {
    PyTypeObject *xxhash_type;
} XXHASH_ModuleState;

/* ------------------------------------------------------------------ */
/*  Buffer / argument helpers                                         */
/* ------------------------------------------------------------------ */

/* Get a buffer from an object. Rejects str with hashlib-compatible error. */
static inline Py_ALWAYS_INLINE int
_get_buffer_or_str(PyObject *obj, Py_buffer *buf)
{
    if (obj == Py_None) {
        PyErr_SetString(PyExc_TypeError,
            "object supporting the buffer API required");
        return -1;
    }
    if (PyUnicode_Check(obj)) {
        PyErr_SetString(PyExc_TypeError,
            "Strings must be encoded before hashing");
        return -1;
    }
    /* Fast path: bypass PyObject_GetBuffer dispatch for bytes objects.
     * For PyBUF_SIMPLE this is equivalent to PyBuffer_FillInfo(...).
     * PyBuffer_Release will DECREF buf->obj (bytes has no releaseproc). */
    if (PyBytes_Check(obj)) {
        buf->buf = PyBytes_AS_STRING(obj);
        buf->len = PyBytes_GET_SIZE(obj);
        buf->obj = (PyObject *)obj;
        Py_INCREF(obj);
        buf->readonly = 1;
        buf->itemsize = 1;
        buf->format = NULL;
        buf->ndim = 1;
        buf->shape = NULL;
        buf->strides = NULL;
        buf->suboffsets = NULL;
        buf->internal = NULL;
        return 0;
    }
    if (PyObject_GetBuffer(obj, buf, PyBUF_SIMPLE) < 0)
        return -1;
    return 0;
}

/* Parse data buffer and optional seed from fastcall arguments.
 * Handles: positional 'data', positional 'seed', keyword 'data',
 * keyword 'seed', with proper error reporting for unknown keywords,
 * duplicate arguments, and too many positional args.
 * Returns 0 on success, -1 on error with exception set. */
static inline int
_parse_fastcall_args(PyObject *const *args, Py_ssize_t nargs,
                     PyObject *kwnames, const char *funcname,
                     int data_required,
                     Py_buffer *buf,
                     unsigned long long *seed)
{
    int data_found = 0;
    int seed_found = 0;

    *seed = 0;
    buf->buf = NULL;
    buf->obj = NULL;

    /* positional args */
    if (nargs >= 1) {
        if (_get_buffer_or_str(args[0], buf) < 0)
            return -1;
        data_found = 1;
    }
    if (nargs >= 2) {
        *seed = PyLong_AsUnsignedLongLongMask(args[1]);
        if (PyErr_Occurred())
            goto error;
        seed_found = 1;
    }
    if (nargs > 2) {
        PyErr_Format(PyExc_TypeError,
            "%s() takes at most 2 positional arguments (%zd given)",
            funcname, nargs);
        goto error;
    }

    /* keyword args */
    if (kwnames) {
        Py_ssize_t nkw = PyTuple_GET_SIZE(kwnames);
        for (Py_ssize_t i = 0; i < nkw; i++) {
            PyObject *key = PyTuple_GET_ITEM(kwnames, i);
            PyObject *val = args[nargs + i];

            if (PyUnicode_CompareWithASCIIString(key, "data") == 0) {
                if (data_found) {
                    PyErr_Format(PyExc_TypeError,
                        "%s() got multiple values for argument 'data'",
                        funcname);
                    goto error;
                }
                if (_get_buffer_or_str(val, buf) < 0)
                    return -1;
                data_found = 1;
            } else if (PyUnicode_CompareWithASCIIString(key, "seed") == 0) {
                if (seed_found) {
                    PyErr_Format(PyExc_TypeError,
                        "%s() got multiple values for argument 'seed'",
                        funcname);
                    goto error;
                }
                *seed = PyLong_AsUnsignedLongLongMask(val);
                if (PyErr_Occurred())
                    goto error;
                seed_found = 1;
            } else {
                PyErr_Format(PyExc_TypeError,
                    "'%U' is an invalid keyword argument for '%s()'",
                    key, funcname);
                goto error;
            }
        }
    }

    if (!data_found && data_required) {
        PyErr_Format(PyExc_TypeError,
            "%s() missing required argument 'data'", funcname);
        return -1;
    }
    return 0;

error:
    if (data_found) {
        PyBuffer_Release(buf);
    }
    return -1;
}

/* Shared helper for parsing __init__ arguments (old-style args+kwargs).
 * Handles positional and keyword 'data' and 'seed', validates keywords,
 * and detects duplicate/multiple values.
 * Returns 0 on success, -1 on error.
 * On success *data_obj is set (or NULL) and *seed is populated. */
static int
_parse_init_args(PyObject *args, PyObject *kwargs,
                 PyObject **data_obj, unsigned long long *seed,
                 const char *funcname)
{
    Py_ssize_t nargs = PyTuple_GET_SIZE(args);

    if (!kwargs) {
        /* fast path: no keywords */
    } else {
        Py_ssize_t pos = 0;
        PyObject *key, *val;
        while (PyDict_Next(kwargs, &pos, &key, &val)) {
            if (PyUnicode_CompareWithASCIIString(key, "data") == 0 ||
                PyUnicode_CompareWithASCIIString(key, "seed") == 0)
                continue;
            PyErr_Format(PyExc_TypeError,
                "'%U' is an invalid keyword argument for this function", key);
            return -1;
        }
    }

    *data_obj = NULL;
    *seed = 0;

    if (nargs >= 1) {
        *data_obj = PyTuple_GET_ITEM(args, 0);
        if (kwargs && PyDict_GetItemString(kwargs, "data")) {
            PyErr_Format(PyExc_TypeError,
                "%s() got multiple values for argument 'data'", funcname);
            return -1;
        }
    }
    if (nargs >= 2) {
        *seed = PyLong_AsUnsignedLongLongMask(PyTuple_GET_ITEM(args, 1));
        if (PyErr_Occurred()) return -1;
        if (kwargs && PyDict_GetItemString(kwargs, "seed")) {
            PyErr_Format(PyExc_TypeError,
                "%s() got multiple values for argument 'seed'", funcname);
            return -1;
        }
    }
    if (nargs > 2) {
        PyErr_Format(PyExc_TypeError,
            "%s() takes at most 2 positional arguments (%zd given)",
            funcname, nargs);
        return -1;
    }

    if (kwargs) {
        PyObject *val = PyDict_GetItemString(kwargs, "data");
        if (val) {
            if (*data_obj) return -1; /* unreachable, caught above */
            *data_obj = val;
        }
        val = PyDict_GetItemString(kwargs, "seed");
        if (val) {
            *seed = PyLong_AsUnsignedLongLongMask(val);
            if (PyErr_Occurred()) return -1;
        }
    }
    return 0;
}

/*****************************************************************************
 * Module Functions — one-shot xxh*_digest / xxh*_hexdigest / xxh*_intdigest *
 ****************************************************************************/

/* Generic one-shot compute: returns bytes / int / str depending on return_type.
 * return_type: 0=digest (bytes), 1=intdigest (int), 2=hexdigest (str) */
/* ------------------------------------------------------------------ */
/*  Oneshot: hexdigest helper                                           */
/* ------------------------------------------------------------------ */

/* Format digest bytes as a lowercase hex string. */
static inline Py_ALWAYS_INLINE PyObject *
_xxhash_hexdigest_from_bytes(const unsigned char *digest, Py_ssize_t ds)
{
    PyObject *ret = PyUnicode_New(ds * 2, 127);
    if (ret == NULL) return NULL;
    Py_UCS1 *b = PyUnicode_1BYTE_DATA(ret);
    for (Py_ssize_t i = 0; i < ds; i++) {
        unsigned char c;
        c = (digest[i] >> 4) & 0xf;
        b[i * 2] = (c > 9) ? c + 'a' - 10 : c + '0';
        c = digest[i] & 0xf;
        b[i * 2 + 1] = (c > 9) ? c + 'a' - 10 : c + '0';
    }
    return ret;
}

/* ------------------------------------------------------------------ */
/*  XXH3_128 intdigest: low64 + (high64 << 64) as a Python int        */
/* ------------------------------------------------------------------ */
static inline Py_ALWAYS_INLINE PyObject *
_xxhash_xxh128_intdigest_result(XXH128_hash_t h)
{
    PyObject *sixtyfour = PyLong_FromLong(64);
    PyObject *low  = PyLong_FromUnsignedLongLong(h.low64);
    PyObject *high = PyLong_FromUnsignedLongLong(h.high64);
    PyObject *result = NULL;
    if (sixtyfour && low && high) {
        PyObject *shifted = PyNumber_Lshift(high, sixtyfour);
        if (shifted) {
            result = PyNumber_Add(shifted, low);
            Py_DECREF(shifted);
        }
    }
    Py_XDECREF(high);
    Py_XDECREF(low);
    Py_XDECREF(sixtyfour);
    return result;
}

/* ------------------------------------------------------------------ */
/*  Oneshot function macros — fully specialized per algo + return     */
/*  type, eliminating the generic switch dispatch.                    */
/* ------------------------------------------------------------------ */

/* Run xxhash computation, releasing the GIL for large inputs.
 * seed_expr is the seed value expression (e.g. "(XXH32_hash_t)seed" or just "seed"). */
#define XXHASH_GIL_RELEASE(buf, seed_expr, hash_var, xxh_func)                 \
    do {                                                                       \
        if ((buf).len > XXHASH_GIL_MINSIZE) {                                  \
            Py_BEGIN_ALLOW_THREADS                                             \
            (hash_var) = xxh_func((buf).buf, (buf).len, (seed_expr));          \
            Py_END_ALLOW_THREADS                                               \
        } else {                                                               \
            (hash_var) = xxh_func((buf).buf, (buf).len, (seed_expr));          \
        }                                                                      \
    } while (0)

#define DEFINE_ONESHOT_INT(name, seed_expr, xxh_func, hash_type, int_conv)     \
static PyObject *                                                              \
xxh##name##_intdigest(PyObject *self, PyObject *const *args,                   \
                       Py_ssize_t nargs, PyObject *kwnames)                    \
{                                                                              \
    XXH64_hash_t seed = 0;                                                     \
    Py_buffer buf;                                                             \
    unsigned long long raw_seed;                                               \
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh" #name "_intdigest",   \
                             1, &buf, &raw_seed) < 0)                          \
        return NULL;                                                           \
    seed = (XXH64_hash_t)raw_seed;                                             \
    hash_type h;                                                               \
    XXHASH_GIL_RELEASE(buf, seed_expr, h, xxh_func);                           \
    PyBuffer_Release(&buf);                                                    \
    return int_conv(h);                                                        \
}

#define DEFINE_ONESHOT_DH(name, seed_expr, xxh_func, hash_type,                \
                           canon_func, canon_type, ds)                         \
/* digest */                                                                   \
static PyObject *                                                              \
xxh##name##_digest(PyObject *self, PyObject *const *args,                      \
                    Py_ssize_t nargs, PyObject *kwnames)                       \
{                                                                              \
    XXH64_hash_t seed = 0;                                                     \
    Py_buffer buf;                                                             \
    unsigned long long raw_seed;                                               \
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh" #name "_digest",      \
                             1, &buf, &raw_seed) < 0)                          \
        return NULL;                                                           \
    seed = (XXH64_hash_t)raw_seed;                                             \
    hash_type h;                                                               \
    XXHASH_GIL_RELEASE(buf, seed_expr, h, xxh_func);                           \
    unsigned char digest[ds];                                                  \
    canon_func((canon_type *)digest, h);                                       \
    PyBuffer_Release(&buf);                                                    \
    return PyBytes_FromStringAndSize((char *)digest, ds);                      \
}                                                                              \
/* hexdigest */                                                                \
static PyObject *                                                              \
xxh##name##_hexdigest(PyObject *self, PyObject *const *args,                   \
                       Py_ssize_t nargs, PyObject *kwnames)                    \
{                                                                              \
    XXH64_hash_t seed = 0;                                                     \
    Py_buffer buf;                                                             \
    unsigned long long raw_seed;                                               \
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh" #name "_hexdigest",   \
                             1, &buf, &raw_seed) < 0)                          \
        return NULL;                                                           \
    seed = (XXH64_hash_t)raw_seed;                                             \
    hash_type h;                                                               \
    XXHASH_GIL_RELEASE(buf, seed_expr, h, xxh_func);                           \
    unsigned char digest[ds];                                                  \
    canon_func((canon_type *)digest, h);                                       \
    PyBuffer_Release(&buf);                                                    \
    return _xxhash_hexdigest_from_bytes(digest, ds);                           \
}

/* XXH32 — seed is truncated to uint32_t at call site */
DEFINE_ONESHOT_INT(32, (XXH32_hash_t)seed, XXH32, XXH32_hash_t, PyLong_FromUnsignedLong)
DEFINE_ONESHOT_DH( 32, (XXH32_hash_t)seed, XXH32, XXH32_hash_t, XXH32_canonicalFromHash, XXH32_canonical_t, 4)

/* XXH64 */
DEFINE_ONESHOT_INT(64, seed, XXH64, XXH64_hash_t, PyLong_FromUnsignedLongLong)
DEFINE_ONESHOT_DH( 64, seed, XXH64, XXH64_hash_t, XXH64_canonicalFromHash, XXH64_canonical_t, 8)

/* XXH3_64 */
DEFINE_ONESHOT_INT(3_64, seed, XXH3_64bits_withSeed, XXH64_hash_t, PyLong_FromUnsignedLongLong)
DEFINE_ONESHOT_DH( 3_64, seed, XXH3_64bits_withSeed, XXH64_hash_t, XXH64_canonicalFromHash, XXH64_canonical_t, 8)

/* XXH3_128 — intdigest uses special big-integer construction */
static PyObject *
xxh3_128_intdigest(PyObject *self, PyObject *const *args,
                    Py_ssize_t nargs, PyObject *kwnames)
{
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh3_128_intdigest",
                             1, &buf, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;
    XXH128_hash_t h;
    XXHASH_GIL_RELEASE(buf, seed, h, XXH3_128bits_withSeed);
    PyBuffer_Release(&buf);
    return _xxhash_xxh128_intdigest_result(h);
}

DEFINE_ONESHOT_DH(3_128, seed, XXH3_128bits_withSeed, XXH128_hash_t, XXH128_canonicalFromHash, XXH128_canonical_t, 16)

#undef XXHASH_GIL_RELEASE
#undef DEFINE_ONESHOT_INT
#undef DEFINE_ONESHOT_DH

/*****************************************************************************
 * Shared type methods — single set shared by all algorithms                 *
 ****************************************************************************/

/* Create and initialize state based on algo (assumes state field is NULL). */
static int
_xxhash_init_state(XXHASHObject *self)
{
    void *state = XXH_DISPATCH(self, create_state)();
    if (!state) {
        PyErr_NoMemory();
        return -1;
    }
    /* Store into the correct union member so _xxhash_state_ptr works. */
    if (self->algo == XXH_ALGO_XXH32)
        self->state.xxh32 = (XXH32_state_t *)state;
    else if (self->algo == XXH_ALGO_XXH64)
        self->state.xxh64 = (XXH64_state_t *)state;
    else
        self->state.xxh3 = (XXH3_state_t *)state;
    XXH_DISPATCH(self, reset)(state, self->seed);
    return 0;
}

/* Free state based on algo. */
static void
_xxhash_free_state(XXHASHObject *self)
{
    void *state = _xxhash_state_ptr(self);
    if (state)
        XXH_DISPATCH(self, free_state)(state);
    self->state.xxh32 = NULL;
}

/* Reset state with current seed. */
static void
_xxhash_reset_state(XXHASHObject *self)
{
    XXH_DISPATCH_CALL(self, reset, self->seed);
}

/* DO_UPDATE: single implementation with algo dispatch.
 * Matches CPython 3.9-3.12 md5 pattern: release GIL first (for large data),
 * then acquire lock, hash, release lock, re-acquire GIL.
 * For small data, acquire lock with GIL held (try-then-block if contested). */
static inline Py_ALWAYS_INLINE void
_xxhash_do_update(XXHASHObject *self, Py_buffer *buf)
{
    void *state = _xxhash_state_ptr(self);
    XXHASH_LOCK_MAYBE_INIT(self, buf->len);
    if (XXHASH_LOCK_IS_ACTIVE(self)) {
        if (buf->len > XXHASH_GIL_MINSIZE) {
            /* Release GIL first, then acquire lock. */
            Py_BEGIN_ALLOW_THREADS
            XXHASH_LOCK_ACQUIRE_BLOCKING(self);
            XXH_DISPATCH(self, update)(state, buf->buf, buf->len);
            XXHASH_LOCK_RELEASE(self);
            Py_END_ALLOW_THREADS
        } else {
            /* Acquire lock with GIL held. */
            XXHASH_LOCK_ACQUIRE(self);
            XXH_DISPATCH(self, update)(state, buf->buf, buf->len);
            XXHASH_LOCK_RELEASE(self);
        }
    } else {
        /* No lock: hash directly, no GIL release. */
        XXH_DISPATCH(self, update)(state, buf->buf, buf->len);
    }
    PyBuffer_Release(buf);
}

/* Shared constructor helper: allocate + init + optionally update with data.
 * Used by the four public constructors (xxh32, xxh64, xxh3_64, xxh3_128). */
static PyObject *
_xxhash_new(PyTypeObject *type, XXH_Algo algo,
            const void *data, Py_ssize_t datalen, XXH64_hash_t seed)
{
    XXHASHObject *self = (XXHASHObject *)type->tp_alloc(type, 0);
    if (self == NULL)
        return NULL;

    XXHASH_LOCK_INIT(self);
    self->algo = algo;
    self->seed = seed;
    self->state.xxh32 = NULL;  /* any union member works */

    if (_xxhash_init_state(self) < 0) {
        Py_DECREF(self);
        return NULL;
    }

    if (data) {
        /* Constructor: no concurrent access possible, skip locking. */
        void *state = _xxhash_state_ptr(self);
        if (datalen > XXHASH_GIL_MINSIZE) {
            Py_BEGIN_ALLOW_THREADS
            XXH_DISPATCH(self, update)(state, data, datalen);
            Py_END_ALLOW_THREADS
        } else {
            XXH_DISPATCH(self, update)(state, data, datalen);
        }
    }
    return (PyObject *)self;
}

/* Thin wrapper: construct from fastcall args (data, seed). */
static PyObject *
_xxhash_new_from_args(PyObject *module, XXH_Algo algo,
                      PyObject *const *args, Py_ssize_t nargs,
                      PyObject *kwnames)
{
    XXH64_hash_t seed = 0;
    Py_buffer buf = {NULL, NULL};
    unsigned long long raw_seed;

    /* Build a descriptive funcname for error messages. */
    const char *funcname = XXH_ALGO_TABLE[algo].name;

    if (_parse_fastcall_args(args, nargs, kwnames, funcname, 0,
                             &buf, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    XXHASH_ModuleState *state = (XXHASH_ModuleState *)PyModule_GetState(module);
    PyTypeObject *type = state->xxhash_type;

    PyObject *obj = _xxhash_new(type, algo,
                                buf.obj ? buf.buf : NULL,
                                buf.obj ? buf.len : 0,
                                seed);
    if (buf.obj) {
        PyBuffer_Release(&buf);
    }
    return obj;
}

/* ------------------------------------------------------------------ */
/*  tp_dealloc                                                         */
/* ------------------------------------------------------------------ */

static void XXHASH_dealloc(XXHASHObject *self)
{
    _xxhash_free_state(self);
    XXHASH_LOCK_FINI(self);
    PyTypeObject *tp = Py_TYPE(self);
    tp->tp_free((PyObject *)self);
    Py_DECREF(tp);
}

/* ------------------------------------------------------------------ */
/*  tp_repr                                                            */
/* ------------------------------------------------------------------ */

static PyObject *
XXHASH_repr(XXHASHObject *self)
{
    /* Match CPython _hashlib: <md5 _hashlib.HASH object> */
    return PyUnicode_FromFormat("<%s %s object>",
                                XXH_ALGO_TABLE[self->algo].name,
                                Py_TYPE(self)->tp_name);
}

/* ------------------------------------------------------------------ */
/*  tp_new                                                             */
/* ------------------------------------------------------------------ */

static PyObject *
XXHASH_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    /* Match CPython _hashlib.HASH: direct construction is forbidden.
     * Only factory functions (xxh32(), xxh64(), etc.) may create instances. */
    return PyErr_Format(PyExc_TypeError,
                        "cannot create '%.100s' instances",
                        type->tp_name);
}

/* ------------------------------------------------------------------ */
/*  tp_init                                                            */
/* ------------------------------------------------------------------ */

static int
XXHASH_init(XXHASHObject *self, PyObject *args, PyObject *kwargs)
{
    unsigned long long seed_val = 0;
    PyObject *data_obj = NULL;
    Py_buffer buf = {NULL, NULL};

    if (_parse_init_args(args, kwargs, &data_obj, &seed_val,
                         "__init__()") < 0)
        return -1;

    if (data_obj) {
        if (_get_buffer_or_str(data_obj, &buf) < 0)
            return -1;
    }

    XXHASH_LOCK_ACQUIRE(self);
    self->seed = (XXH64_hash_t)seed_val;
    _xxhash_reset_state(self);

    if (buf.obj) {
        XXH_DISPATCH_CALL(self, update, buf.buf, buf.len);
        PyBuffer_Release(&buf);
    }
    XXHASH_LOCK_RELEASE(self);
    return 0;
}

/* ------------------------------------------------------------------ */
/*  Public constructors (module-level functions, one per algo)         */
/* ------------------------------------------------------------------ */

static PyObject *
xxh32_construct(PyObject *module, PyObject *const *args,
                Py_ssize_t nargs, PyObject *kwnames)
{
    return _xxhash_new_from_args(module, XXH_ALGO_XXH32, args, nargs, kwnames);
}

static PyObject *
xxh64_construct(PyObject *module, PyObject *const *args,
                Py_ssize_t nargs, PyObject *kwnames)
{
    return _xxhash_new_from_args(module, XXH_ALGO_XXH64, args, nargs, kwnames);
}

static PyObject *
xxh3_64_construct(PyObject *module, PyObject *const *args,
                  Py_ssize_t nargs, PyObject *kwnames)
{
    return _xxhash_new_from_args(module, XXH_ALGO_XXH3_64, args, nargs, kwnames);
}

static PyObject *
xxh3_128_construct(PyObject *module, PyObject *const *args,
                   Py_ssize_t nargs, PyObject *kwnames)
{
    return _xxhash_new_from_args(module, XXH_ALGO_XXH3_128, args, nargs, kwnames);
}

/* ------------------------------------------------------------------ */
/*  update                                                             */
/* ------------------------------------------------------------------ */

PyDoc_STRVAR(
    XXHASH_update_doc,
    "update (data)\n\n"
    "Update the xxhash object with bytes-like data. Repeated calls are\n"
    "equivalent to a single call with the concatenation of all the arguments.");

static PyObject *
XXHASH_update(XXHASHObject *self, PyObject *const *args,
              Py_ssize_t nargs, PyObject *kwnames)
{
    PyObject *arg = NULL;

    /* validate keywords first */
    if (kwnames) {
        Py_ssize_t nkw = PyTuple_GET_SIZE(kwnames);
        for (Py_ssize_t i = 0; i < nkw; i++) {
            PyObject *key = PyTuple_GET_ITEM(kwnames, i);
            if (PyUnicode_CompareWithASCIIString(key, "data") == 0) {
                if (nargs >= 1) {
                    const char *name = XXH_ALGO_TABLE[self->algo].name;
                    PyErr_Format(PyExc_TypeError,
                        "%s.update() got multiple values for argument 'data'",
                        name);
                    return NULL;
                }
                arg = args[nargs + i];
            } else {
                const char *name = XXH_ALGO_TABLE[self->algo].name;
                PyErr_Format(PyExc_TypeError,
                    "'%U' is an invalid keyword argument for '%s.update()'",
                    key, name);
                return NULL;
            }
        }
    }

    if (nargs >= 1) {
        if (nargs > 1) {
            const char *name = XXH_ALGO_TABLE[self->algo].name;
            PyErr_Format(PyExc_TypeError,
                "%s.update() takes at most 1 positional argument (%zd given)",
                name, nargs);
            return NULL;
        }
        arg = args[0];
    }

    if (!arg) {
        const char *name = XXH_ALGO_TABLE[self->algo].name;
        PyErr_Format(PyExc_TypeError,
            "%s.update() missing required argument 'data'", name);
        return NULL;
    }

    Py_buffer buf;
    if (_get_buffer_or_str(arg, &buf) < 0)
        return NULL;
    _xxhash_do_update(self, &buf);
    Py_RETURN_NONE;
}

/* ------------------------------------------------------------------ */
/*  digest                                                            */
/* ------------------------------------------------------------------ */

PyDoc_STRVAR(
    XXHASH_digest_doc,
    "digest() -> string\n\n"
    "Return the digest of the data passed to the update() method so\n"
    "far. This is a variable-length string which may contain non-ASCII\n"
    "characters, including null bytes.");

static PyObject *
XXHASH_digest(XXHASHObject *self)
{
    unsigned char ds = XXH_ALGO_TABLE[self->algo].digest_size;
    char digest[16];  /* max 16 bytes (XXH128) */

    XXHASH_LOCK_ACQUIRE(self);
    XXH_DISPATCH_CALL(self, digest, digest);
    XXHASH_LOCK_RELEASE(self);

    return PyBytes_FromStringAndSize(digest, ds);
}

/* ------------------------------------------------------------------ */
/*  hexdigest                                                         */
/* ------------------------------------------------------------------ */

PyDoc_STRVAR(
    XXHASH_hexdigest_doc,
    "hexdigest() -> string\n\n"
    "Like digest(), but returns the digest as a string of hexadecimal digits.");

static PyObject *
XXHASH_hexdigest(XXHASHObject *self)
{
    unsigned char ds = XXH_ALGO_TABLE[self->algo].digest_size;
    char digest[16];  /* max 16 bytes (XXH128) */

    XXHASH_LOCK_ACQUIRE(self);
    XXH_DISPATCH_CALL(self, digest, digest);
    XXHASH_LOCK_RELEASE(self);

    return _xxhash_hexdigest_from_bytes((unsigned char *)digest, ds);
}

/* ------------------------------------------------------------------ */
/*  intdigest                                                         */
/* ------------------------------------------------------------------ */

PyDoc_STRVAR(
    XXHASH_intdigest_doc,
    "intdigest() -> int\n\n"
    "Like digest(), but returns the digest as an integer, which is the integer\n"
    "returned by xxhash C API");

static PyObject *
XXHASH_intdigest(XXHASHObject *self)
{
    XXHASH_LOCK_ACQUIRE(self);
    PyObject *ret = XXH_DISPATCH_CALL(self, intdigest);
    XXHASH_LOCK_RELEASE(self);
    return ret;
}

/* ------------------------------------------------------------------ */
/*  copy                                                              */
/* ------------------------------------------------------------------ */

PyDoc_STRVAR(
    XXHASH_copy_doc,
    "copy() -> xxhash object\n\n"
    "Return a copy (``clone'') of the xxhash object.");

static PyObject *
XXHASH_copy(XXHASHObject *self)
{
    XXHASHObject *p;

    if ((p = (XXHASHObject *)Py_TYPE(self)->tp_alloc(Py_TYPE(self), 0)) == NULL) {
        return NULL;
    }

    XXHASH_LOCK_INIT(p);
    p->algo = self->algo;
    p->state.xxh32 = NULL;
    p->seed = self->seed;

    /* Allocate destination state (same algo as source). */
    void *dst = XXH_DISPATCH(self, create_state)();
    if (!dst) {
        Py_DECREF(p);
        return PyErr_NoMemory();
    }
    /* Store into the correct union member. */
    if (self->algo == XXH_ALGO_XXH32)
        p->state.xxh32 = (XXH32_state_t *)dst;
    else if (self->algo == XXH_ALGO_XXH64)
        p->state.xxh64 = (XXH64_state_t *)dst;
    else
        p->state.xxh3 = (XXH3_state_t *)dst;

    XXHASH_LOCK_ACQUIRE(self);
    XXH_DISPATCH(self, copy_state)(dst, _xxhash_state_ptr(self));
#if XXH_VERSION_NUMBER < 704
    // v0.7.3 and earlier have a bug where states reset with a seed
    // will have a wild pointer to the original state when copied,
    // causing a use-after-free if the original is freed.
    if (self->algo >= XXH_ALGO_XXH3_64) {
        XXH3_state_t *d = p->state.xxh3;
        XXH3_state_t *s = self->state.xxh3;
        if (d->secret == &s->customSecret[0])
            d->secret = &d->customSecret[0];
    }
#endif
    XXHASH_LOCK_RELEASE(self);

    return (PyObject *)p;
}

/* ------------------------------------------------------------------ */
/*  reset                                                             */
/* ------------------------------------------------------------------ */

PyDoc_STRVAR(
    XXHASH_reset_doc,
    "reset()\n\n"
    "Reset state.");

static PyObject *
XXHASH_reset(XXHASHObject *self)
{
    XXHASH_LOCK_ACQUIRE(self);
    _xxhash_reset_state(self);
    XXHASH_LOCK_RELEASE(self);
    Py_RETURN_NONE;
}

/* ------------------------------------------------------------------ */
/*  Getseters                                                         */
/* ------------------------------------------------------------------ */

static PyObject *
XXHASH_get_digest_size(XXHASHObject *self, void *closure)
{
    return PyLong_FromLong(XXH_ALGO_TABLE[self->algo].digest_size);
}

static PyObject *
XXHASH_get_block_size(XXHASHObject *self, void *closure)
{
    return PyLong_FromLong(XXH_ALGO_TABLE[self->algo].block_size);
}

static PyObject *
XXHASH_get_name(XXHASHObject *self, void *closure)
{
    return PyUnicode_FromString(XXH_ALGO_TABLE[self->algo].name);
}

static PyObject *
XXHASH_get_seed(XXHASHObject *self, void *closure)
{
    switch (self->algo) {
        case XXH_ALGO_XXH32:
            return PyLong_FromUnsignedLong((XXH32_hash_t)self->seed);
        case XXH_ALGO_XXH64:
        case XXH_ALGO_XXH3_64:
        case XXH_ALGO_XXH3_128:
            return PyLong_FromUnsignedLongLong(self->seed);
        default:
            return NULL;
    }
}

static PyGetSetDef XXHASH_getseters[] = {
    {
        "digest_size",
        (getter)XXHASH_get_digest_size, NULL,
        "Digest size.",
        NULL
    },
    {
        "block_size",
        (getter)XXHASH_get_block_size, NULL,
        "Block size.",
        NULL
    },
    {
        "name",
        (getter)XXHASH_get_name, NULL,
        "Algorithm name (XXH32, XXH64, XXH3_64, or XXH3_128).",
        NULL
    },
    {
        "digestsize",
        (getter)XXHASH_get_digest_size, NULL,
        "Digest size.",
        NULL
    },
    {
        "seed",
        (getter)XXHASH_get_seed, NULL,
        "Seed.",
        NULL
    },
    {NULL}  /* Sentinel */
};

/* ------------------------------------------------------------------ */
/*  Methods                                                           */
/* ------------------------------------------------------------------ */

static PyMethodDef XXHASH_methods[] = {
    {"update",    (PyCFunction)XXHASH_update,    METH_FASTCALL | METH_KEYWORDS, XXHASH_update_doc},
    {"digest",    (PyCFunction)XXHASH_digest,    METH_NOARGS,  XXHASH_digest_doc},
    {"hexdigest", (PyCFunction)XXHASH_hexdigest, METH_NOARGS,  XXHASH_hexdigest_doc},
    {"intdigest", (PyCFunction)XXHASH_intdigest, METH_NOARGS,  XXHASH_intdigest_doc},
    {"copy",      (PyCFunction)XXHASH_copy,      METH_NOARGS,  XXHASH_copy_doc},
    {"reset",     (PyCFunction)XXHASH_reset,     METH_NOARGS,  XXHASH_reset_doc},
    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(
    XXHASHType_doc,
    "An xxhash represents the object used to calculate xxHash digests.\n"
    "\n"
    "This type supports all four xxHash algorithms (XXH32, XXH64, XXH3_64,\n"
    "XXH3_128).  Use the xxh32(), xxh64(), xxh3_64(), or xxh3_128()\n"
    "constructor to create an instance for a specific algorithm.\n"
    "\n"
    "Methods:\n"
    "\n"
    "update(data) -- updates the current digest with the provided data\n"
    "digest() -- return the current digest value\n"
    "hexdigest() -- return the current digest as a string of hexadecimal digits\n"
    "intdigest() -- return the current digest as an integer\n"
    "copy() -- return a copy of the current xxhash object\n"
    "reset() -- reset state");

/* ------------------------------------------------------------------ */
/*  Type slots + spec                                                 */
/* ------------------------------------------------------------------ */

static PyType_Slot XXHASHType_slots[] = {
    {Py_tp_dealloc, XXHASH_dealloc},
    {Py_tp_doc, (void *)XXHASHType_doc},
    {Py_tp_methods, XXHASH_methods},
    {Py_tp_getset, XXHASH_getseters},
    {Py_tp_init, XXHASH_init},
    {Py_tp_new, XXHASH_new},
    {Py_tp_repr, XXHASH_repr},
    {0, NULL},
};

static PyType_Spec XXHASHType_spec = {
    .name = "_xxhash.HASH",
    .basicsize = sizeof(XXHASHObject),
    .flags = Py_TPFLAGS_DEFAULT
#if PY_VERSION_HEX >= 0x030c0000
           | Py_TPFLAGS_IMMUTABLETYPE
#endif
    ,
    .slots = XXHASHType_slots,
};

/****************************************************************************
 * Module Init **************************************************************
 ****************************************************************************/

static int _exec(PyObject *module)
{
    /* Create the single heap type bound to this module (sub-interpreter safe). */
    PyObject *xxhash_type = PyType_FromModuleAndSpec(module, &XXHASHType_spec, NULL);
    if (!xxhash_type) return -1;

    /* Store in module state for constructor functions. */
    XXHASH_ModuleState *modstate = (XXHASH_ModuleState *)PyModule_GetState(module);
    modstate->xxhash_type = (PyTypeObject *)xxhash_type;

    /* Module-level function definitions for the four constructors.
     * Each is added with METH_FASTCALL | METH_KEYWORDS so Python sees them as
     * functions, not types — but they return type instances. */
    static PyMethodDef xxh32_def = {
        "xxh32", (PyCFunction)xxh32_construct,
        METH_FASTCALL | METH_KEYWORDS,
        "xxh32(data=..., seed=0) -> xxhash object\n\nCompute XXH32 hash."
    };
    static PyMethodDef xxh64_def = {
        "xxh64", (PyCFunction)xxh64_construct,
        METH_FASTCALL | METH_KEYWORDS,
        "xxh64(data=..., seed=0) -> xxhash object\n\nCompute XXH64 hash."
    };
    static PyMethodDef xxh3_64_def = {
        "xxh3_64", (PyCFunction)xxh3_64_construct,
        METH_FASTCALL | METH_KEYWORDS,
        "xxh3_64(data=..., seed=0) -> xxhash object\n\nCompute XXH3_64 hash."
    };
    static PyMethodDef xxh3_128_def = {
        "xxh3_128", (PyCFunction)xxh3_128_construct,
        METH_FASTCALL | METH_KEYWORDS,
        "xxh3_128(data=..., seed=0) -> xxhash object\n\nCompute XXH3_128 hash."
    };

    /* Add type to module — shares the same name as the module for discoverability.
     * We add both the type and constructor functions to the module. */
    if (PyModule_AddType(module, (PyTypeObject *)xxhash_type) < 0) {
        Py_DECREF(xxhash_type); return -1;
    }

    /* Add constructor functions. These are also accessible directly:
     *   import xxhash
     *   xxhash.xxh32(data)  # function, not type
     */
#define ADD_CONSTRUCTOR(name)                                                  \
    do {                                                                       \
        PyObject *func = PyCFunction_NewEx(& name##_def, module, NULL);        \
        if (!func) { Py_DECREF(xxhash_type); return -1; }                      \
        if (PyModule_AddObject(module, #name, func) < 0) {                     \
            Py_DECREF(func); Py_DECREF(xxhash_type); return -1;                \
        }                                                                      \
    } while (0)

    ADD_CONSTRUCTOR(xxh32);
    ADD_CONSTRUCTOR(xxh64);
    ADD_CONSTRUCTOR(xxh3_64);
    ADD_CONSTRUCTOR(xxh3_128);

#undef ADD_CONSTRUCTOR

    /* There's still a DECREF for xxhash_type since PyModule_AddType increfs it.
     * PyModule_AddObject for constructors also increfs the function objects
     * (they own themselves through PyCFunction_NewEx), so no extra DECREF needed. */
    Py_DECREF(xxhash_type);

    if (PyModule_AddStringConstant(module, "XXHASH_VERSION", VALUE_TO_STRING(XXHASH_VERSION)) < 0)
        return -1;

    if (PyModule_AddIntConstant(module, "_GIL_MINSIZE", XXHASH_GIL_MINSIZE) < 0)
        return -1;

    return 0;
}

static PyModuleDef_Slot slots[] = {
    {Py_mod_exec, _exec},
#if PY_VERSION_HEX >= 0x030c0000  /* Python 3.12+: sub-interpreter support */
    {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
#endif
#if PY_VERSION_HEX >= 0x030d0000
    /* Python 3.13+: module is thread-safe with per-object lock */
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};

/* Module-level one-shot functions (xxh32_digest, xxh64_digest, etc.) */
static PyMethodDef methods[] = {
    {"xxh32_digest",       (PyCFunction)xxh32_digest,       METH_FASTCALL | METH_KEYWORDS, "xxh32_digest"      },
    {"xxh32_intdigest",    (PyCFunction)xxh32_intdigest,    METH_FASTCALL | METH_KEYWORDS, "xxh32_intdigest"   },
    {"xxh32_hexdigest",    (PyCFunction)xxh32_hexdigest,    METH_FASTCALL | METH_KEYWORDS, "xxh32_hexdigest"   },
    {"xxh64_digest",       (PyCFunction)xxh64_digest,       METH_FASTCALL | METH_KEYWORDS, "xxh64_digest"      },
    {"xxh64_intdigest",    (PyCFunction)xxh64_intdigest,    METH_FASTCALL | METH_KEYWORDS, "xxh64_intdigest"   },
    {"xxh64_hexdigest",    (PyCFunction)xxh64_hexdigest,    METH_FASTCALL | METH_KEYWORDS, "xxh64_hexdigest"   },
    {"xxh3_64_digest",     (PyCFunction)xxh3_64_digest,     METH_FASTCALL | METH_KEYWORDS, "xxh3_64_digest"    },
    {"xxh3_64_intdigest",  (PyCFunction)xxh3_64_intdigest,  METH_FASTCALL | METH_KEYWORDS, "xxh3_64_intdigest" },
    {"xxh3_64_hexdigest",  (PyCFunction)xxh3_64_hexdigest,  METH_FASTCALL | METH_KEYWORDS, "xxh3_64_hexdigest" },
    {"xxh3_128_digest",    (PyCFunction)xxh3_128_digest,    METH_FASTCALL | METH_KEYWORDS, "xxh3_128_digest"   },
    {"xxh3_128_intdigest", (PyCFunction)xxh3_128_intdigest, METH_FASTCALL | METH_KEYWORDS, "xxh3_128_intdigest"},
    {"xxh3_128_hexdigest", (PyCFunction)xxh3_128_hexdigest, METH_FASTCALL | METH_KEYWORDS, "xxh3_128_hexdigest"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_xxhash",
    NULL,
    sizeof(XXHASH_ModuleState),
    methods,
    slots,
    NULL,  /* m_traverse */
    NULL,  /* m_clear */
    NULL,  /* m_free */
};

PyMODINIT_FUNC
PyInit__xxhash(void)
{
    return PyModuleDef_Init(&moduledef);
}
