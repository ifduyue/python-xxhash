/*
 * Copyright (c) 2014-2025, Yue Du
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
 non-cryptographic hash algorithm algorithm */


#include <Python.h>
#include <string.h>

#include "xxhash.h"

#define TOSTRING(x) #x
#define VALUE_TO_STRING(x) TOSTRING(x)
#define XXHASH_VERSION XXH_VERSION_MAJOR.XXH_VERSION_MINOR.XXH_VERSION_RELEASE

#define XXH32_DIGESTSIZE 4
#define XXH32_BLOCKSIZE 16
#define XXH64_DIGESTSIZE 8
#define XXH64_BLOCKSIZE 32
#define XXH128_DIGESTSIZE 16
#define XXH128_BLOCKSIZE 64


/* Get a buffer from an object, or UTF-8 encode if it's a str.
 * On success, *owner is set to the object that owns the buffer
 * (NULL if the arg itself supports the buffer protocol).
 * Caller must PyBuffer_Release(buf) and Py_XDECREF(*owner). */
#ifndef Py_ALWAYS_INLINE
#  define Py_ALWAYS_INLINE
#endif

static Py_ALWAYS_INLINE int
_get_buffer_or_str(PyObject *obj, Py_buffer *buf, PyObject **owner)
{
    /* Check str first to avoid a guaranteed-failing PyObject_GetBuffer call
     * and the resulting set/clear of a TypeError. */
    if (PyUnicode_Check(obj)) {
        *owner = PyUnicode_AsUTF8String(obj);
        if (*owner == NULL)
            return -1;
        if (PyObject_GetBuffer(*owner, buf, PyBUF_SIMPLE) < 0) {
            Py_DECREF(*owner);
            return -1;
        }
        return 0;
    }
    if (PyObject_GetBuffer(obj, buf, PyBUF_SIMPLE) < 0)
        return -1;
    *owner = NULL;
    return 0;
}

/* Parse input buffer and optional seed from fastcall arguments.
 * Handles: positional 'input', positional 'seed', keyword 'input',
 * keyword 'seed', with proper error reporting for unknown keywords,
 * duplicate arguments, and too many positional args.
 * Returns 0 on success, -1 on error with exception set. */
static Py_ALWAYS_INLINE int
_parse_fastcall_args(PyObject *const *args, Py_ssize_t nargs,
                     PyObject *kwnames, const char *funcname,
                     int input_required,
                     Py_buffer *buf, PyObject **buf_owner,
                     unsigned long long *seed)
{
    int input_found = 0;
    int seed_found = 0;

    *seed = 0;
    buf->buf = NULL;
    *buf_owner = NULL;

    /* positional args */
    if (nargs >= 1) {
        if (_get_buffer_or_str(args[0], buf, buf_owner) < 0)
            return -1;
        input_found = 1;
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

            if (PyUnicode_CompareWithASCIIString(key, "input") == 0) {
                if (input_found) {
                    PyErr_Format(PyExc_TypeError,
                        "%s() got multiple values for argument 'input'",
                        funcname);
                    goto error;
                }
                if (_get_buffer_or_str(val, buf, buf_owner) < 0)
                    return -1;
                input_found = 1;
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

    if (!input_found && input_required) {
        PyErr_Format(PyExc_TypeError,
            "%s() missing required argument 'input'", funcname);
        return -1;
    }
    return 0;

error:
    if (input_found) {
        PyBuffer_Release(buf);
        Py_XDECREF(*buf_owner);
    }
    return -1;
}

/*****************************************************************************
 * Module Functions ***********************************************************
 ****************************************************************************/

/* XXH32 */
static PyObject *xxh32_digest(PyObject *self, PyObject *const *args,
                               Py_ssize_t nargs, PyObject *kwnames)
{
    XXH32_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh32_digest", 1, &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH32_hash_t)raw_seed;

    XXH32_hash_t intdigest = XXH32(buf.buf, buf.len, seed);
    PyBuffer_Release(&buf);
    Py_XDECREF(buf_owner);

    char retbuf[XXH32_DIGESTSIZE];
    XXH32_canonicalFromHash((XXH32_canonical_t *)retbuf, intdigest);
    return PyBytes_FromStringAndSize(retbuf, sizeof(retbuf));
}
static PyObject *xxh32_intdigest(PyObject *self, PyObject *const *args,
                                  Py_ssize_t nargs, PyObject *kwnames)
{
    XXH32_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh32_intdigest", 1, &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH32_hash_t)raw_seed;

    XXH32_hash_t intdigest = XXH32(buf.buf, buf.len, seed);
    PyBuffer_Release(&buf);
    Py_XDECREF(buf_owner);

    return PyLong_FromUnsignedLong(intdigest);
}
static PyObject *xxh32_hexdigest(PyObject *self, PyObject *const *args,
                                  Py_ssize_t nargs, PyObject *kwnames)
{
    XXH32_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh32_hexdigest", 1, &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH32_hash_t)raw_seed;

    XXH32_hash_t intdigest = XXH32(buf.buf, buf.len, seed);
    PyBuffer_Release(&buf);
    Py_XDECREF(buf_owner);

    char digest[XXH32_DIGESTSIZE];
    XXH32_canonicalFromHash((XXH32_canonical_t *)digest, intdigest);

    char retbuf[XXH32_DIGESTSIZE * 2];
    int i, j;
    for (i = j = 0; i < XXH32_DIGESTSIZE; i++) {
        unsigned char c;
        c = (digest[i] >> 4) & 0xf;
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
        c = (digest[i] & 0xf);
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
    }

    return PyUnicode_FromStringAndSize(retbuf, sizeof(retbuf));
}

/* XXH64 */
static PyObject *xxh64_digest(PyObject *self, PyObject *const *args,
                               Py_ssize_t nargs, PyObject *kwnames)
{
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh64_digest", 1, &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    XXH64_hash_t intdigest = XXH64(buf.buf, buf.len, seed);
    PyBuffer_Release(&buf);
    Py_XDECREF(buf_owner);

    char retbuf[XXH64_DIGESTSIZE];
    XXH64_canonicalFromHash((XXH64_canonical_t *)retbuf, intdigest);
    return PyBytes_FromStringAndSize(retbuf, sizeof(retbuf));
}
static PyObject *xxh64_intdigest(PyObject *self, PyObject *const *args,
                                  Py_ssize_t nargs, PyObject *kwnames)
{
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh64_intdigest", 1, &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    XXH64_hash_t intdigest = XXH64(buf.buf, buf.len, seed);
    PyBuffer_Release(&buf);
    Py_XDECREF(buf_owner);

    return PyLong_FromUnsignedLongLong(intdigest);
}
static PyObject *xxh64_hexdigest(PyObject *self, PyObject *const *args,
                                  Py_ssize_t nargs, PyObject *kwnames)
{
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh64_hexdigest", 1, &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    XXH64_hash_t intdigest = XXH64(buf.buf, buf.len, seed);
    PyBuffer_Release(&buf);
    Py_XDECREF(buf_owner);

    char digest[XXH64_DIGESTSIZE];
    XXH64_canonicalFromHash((XXH64_canonical_t *)digest, intdigest);

    char retbuf[XXH64_DIGESTSIZE * 2];
    int i, j;
    for (i = j = 0; i < XXH64_DIGESTSIZE; i++) {
        unsigned char c;
        c = (digest[i] >> 4) & 0xf;
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
        c = (digest[i] & 0xf);
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
    }

    return PyUnicode_FromStringAndSize(retbuf, sizeof(retbuf));
}

/* XXH3_64 */
static PyObject *xxh3_64_digest(PyObject *self, PyObject *const *args,
                               Py_ssize_t nargs, PyObject *kwnames)
{
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh3_64_digest", 1, &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    XXH64_hash_t intdigest = XXH3_64bits_withSeed(buf.buf, buf.len, seed);
    PyBuffer_Release(&buf);
    Py_XDECREF(buf_owner);

    char retbuf[XXH64_DIGESTSIZE];
    XXH64_canonicalFromHash((XXH64_canonical_t *)retbuf, intdigest);
    return PyBytes_FromStringAndSize(retbuf, sizeof(retbuf));
}
static PyObject *xxh3_64_intdigest(PyObject *self, PyObject *const *args,
                                  Py_ssize_t nargs, PyObject *kwnames)
{
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh3_64_intdigest", 1, &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    XXH64_hash_t intdigest = XXH3_64bits_withSeed(buf.buf, buf.len, seed);
    PyBuffer_Release(&buf);
    Py_XDECREF(buf_owner);

    return PyLong_FromUnsignedLongLong(intdigest);
}
static PyObject *xxh3_64_hexdigest(PyObject *self, PyObject *const *args,
                                  Py_ssize_t nargs, PyObject *kwnames)
{
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh3_64_hexdigest", 1, &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    XXH64_hash_t intdigest = XXH3_64bits_withSeed(buf.buf, buf.len, seed);
    PyBuffer_Release(&buf);
    Py_XDECREF(buf_owner);

    char digest[XXH64_DIGESTSIZE];
    XXH64_canonicalFromHash((XXH64_canonical_t *)digest, intdigest);

    char retbuf[XXH64_DIGESTSIZE * 2];
    int i, j;
    for (i = j = 0; i < XXH64_DIGESTSIZE; i++) {
        unsigned char c;
        c = (digest[i] >> 4) & 0xf;
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
        c = (digest[i] & 0xf);
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
    }

    return PyUnicode_FromStringAndSize(retbuf, sizeof(retbuf));
}

/* XXH3_128 */
static PyObject *xxh3_128_digest(PyObject *self, PyObject *const *args,
                               Py_ssize_t nargs, PyObject *kwnames)
{
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh3_128_digest", 1, &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    XXH128_hash_t intdigest = XXH3_128bits_withSeed(buf.buf, buf.len, seed);
    PyBuffer_Release(&buf);
    Py_XDECREF(buf_owner);

    char retbuf[XXH128_DIGESTSIZE];
    XXH128_canonicalFromHash((XXH128_canonical_t *)retbuf, intdigest);
    return PyBytes_FromStringAndSize(retbuf, sizeof(retbuf));
}
static PyObject *xxh3_128_intdigest(PyObject *self, PyObject *const *args,
                                     Py_ssize_t nargs, PyObject *kwnames)
{
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh3_128_intdigest", 1, &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    XXH128_hash_t intdigest = XXH3_128bits_withSeed(buf.buf, buf.len, seed);
    PyBuffer_Release(&buf);
    Py_XDECREF(buf_owner);

    PyObject *sixtyfour = PyLong_FromLong(64);
    PyObject *low = PyLong_FromUnsignedLongLong(intdigest.low64);
    PyObject *high = PyLong_FromUnsignedLongLong(intdigest.high64);
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
static PyObject *xxh3_128_hexdigest(PyObject *self, PyObject *const *args,
                                  Py_ssize_t nargs, PyObject *kwnames)
{
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;
    if (_parse_fastcall_args(args, nargs, kwnames, "xxh3_128_hexdigest", 1, &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    XXH128_hash_t intdigest = XXH3_128bits_withSeed(buf.buf, buf.len, seed);
    PyBuffer_Release(&buf);
    Py_XDECREF(buf_owner);

    char digest[XXH128_DIGESTSIZE];
    XXH128_canonicalFromHash((XXH128_canonical_t *)digest, intdigest);

    char retbuf[XXH128_DIGESTSIZE * 2];
    int i, j;
    for (i = j = 0; i < XXH128_DIGESTSIZE; i++) {
        unsigned char c;
        c = (digest[i] >> 4) & 0xf;
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
        c = (digest[i] & 0xf);
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
    }

    return PyUnicode_FromStringAndSize(retbuf, sizeof(retbuf));
}

/*****************************************************************************
 * Module Types ***************************************************************
 ****************************************************************************/

/* XXH32 */

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    XXH32_state_t *xxhash_state;
    XXH32_hash_t seed;
} PYXXH32Object;

static PyTypeObject PYXXH32Type;

static void PYXXH32_dealloc(PYXXH32Object *self)
{
    if (self->xxhash_state)
        XXH32_freeState(self->xxhash_state);
    PyObject_Del(self);
}

static void PYXXH32_do_update(PYXXH32Object *self, Py_buffer *buf)
{
    Py_BEGIN_ALLOW_THREADS
    XXH32_update(self->xxhash_state, buf->buf, buf->len);
    Py_END_ALLOW_THREADS

    PyBuffer_Release(buf);
}

static PyObject *
PYXXH32_vectorcall(PyObject *type, PyObject *const *args,
                   size_t nargsf, PyObject *kwnames)
{
    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);
    XXH32_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;

    if (_parse_fastcall_args(args, nargs, kwnames, "xxhash.xxh32()", 0,
                             &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH32_hash_t)raw_seed;

    PYXXH32Object *self = (PYXXH32Object *)
        ((PyTypeObject *)type)->tp_alloc((PyTypeObject *)type, 0);
    if (self == NULL) {
        PyBuffer_Release(&buf);
        Py_XDECREF(buf_owner);
        return NULL;
    }

    self->xxhash_state = XXH32_createState();
    if (self->xxhash_state == NULL) {
        Py_DECREF(self);
        PyBuffer_Release(&buf);
        Py_XDECREF(buf_owner);
        return PyErr_NoMemory();
    }
    self->seed = seed;
    XXH32_reset(self->xxhash_state, seed);

    if (buf.buf) {
        Py_BEGIN_ALLOW_THREADS
        XXH32_update(self->xxhash_state, buf.buf, buf.len);
        Py_END_ALLOW_THREADS
        PyBuffer_Release(&buf);
    }
    Py_XDECREF(buf_owner);
    return (PyObject *)self;
}

/* XXH32 methods */

static PyObject *PYXXH32_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PYXXH32Object *self;

    if ((self = PyObject_New(PYXXH32Object, &PYXXH32Type)) == NULL) {
        return NULL;
    }

    if ((self->xxhash_state = XXH32_createState()) == NULL) {
        Py_DECREF(self);
        PyErr_NoMemory();
        return NULL;
    }

    self->seed = 0;
    XXH32_reset(self->xxhash_state, 0);

    return (PyObject *)self;
}

static int PYXXH32_init(PYXXH32Object *self, PyObject *args, PyObject *kwargs)
{
    XXH32_hash_t seed = 0;
    char *keywords[] = {"input", "seed", NULL};
    Py_buffer buf;

    buf.buf = buf.obj = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|s*I:__init__", keywords, &buf, &seed)) {
        return -1;
    }

    self->seed = seed;
    XXH32_reset(self->xxhash_state, seed);

    if (buf.buf) {
        PYXXH32_do_update(self, &buf);
    }

    return 0;
}

PyDoc_STRVAR(
    PYXXH32_update_doc,
    "update (input)\n\n"
    "Update the xxh32 object with the string input. Repeated calls are\n"
    "equivalent to a single call with the concatenation of all the arguments.");

static PyObject *PYXXH32_update(PYXXH32Object *self, PyObject *args)
{
    Py_buffer buf;

    buf.buf = buf.obj = NULL;

    if (!PyArg_ParseTuple(args, "s*:update", &buf)) {
        return NULL;
    }

    PYXXH32_do_update(self, &buf);

    Py_RETURN_NONE;
}


PyDoc_STRVAR(
    PYXXH32_digest_doc,
    "digest() -> string\n\n"
    "Return the digest of the strings passed to the update() method so\n"
    "far. This is a 4-byte string which may contain non-ASCII characters,\n"
    "including null bytes.");

static PyObject *PYXXH32_digest(PYXXH32Object *self)
{
    char retbuf[XXH32_DIGESTSIZE];
    XXH32_hash_t intdigest;

    intdigest = XXH32_digest(self->xxhash_state);
    XXH32_canonicalFromHash((XXH32_canonical_t *)retbuf, intdigest);

    return PyBytes_FromStringAndSize(retbuf, sizeof(retbuf));
}

PyDoc_STRVAR(
    PYXXH32_hexdigest_doc,
    "hexdigest() -> string\n\n"
    "Like digest(), but returns the digest as a string of hexadecimal digits.");

static PyObject *PYXXH32_hexdigest(PYXXH32Object *self)
{
    XXH32_hash_t intdigest;
    char digest[XXH32_DIGESTSIZE];
    char retbuf[XXH32_DIGESTSIZE * 2];
    int i, j;

    intdigest = XXH32_digest(self->xxhash_state);
    XXH32_canonicalFromHash((XXH32_canonical_t *)digest, intdigest);

    for (i = j = 0; i < XXH32_DIGESTSIZE; i++) {
        unsigned char c;
        c = (digest[i] >> 4) & 0xf;
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
        c = (digest[i] & 0xf);
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
    }

    return PyUnicode_FromStringAndSize(retbuf, sizeof(retbuf));
}

PyDoc_STRVAR(
    PYXXH32_intdigest_doc,
    "intdigest() -> int\n\n"
    "Like digest(), but returns the digest as an integer, which is the integer\n"
    "returned by xxhash C API");

static PyObject *PYXXH32_intdigest(PYXXH32Object *self)
{
    XXH32_hash_t digest = XXH32_digest(self->xxhash_state);
    return PyLong_FromUnsignedLong(digest);
}

PyDoc_STRVAR(
    PYXXH32_copy_doc,
    "copy() -> xxh32 object\n\n"
    "Return a copy (``clone'') of the xxh32 object.");

static PyObject *PYXXH32_copy(PYXXH32Object *self)
{
    PYXXH32Object *p;

    if ((p = PyObject_New(PYXXH32Object, &PYXXH32Type)) == NULL) {
        return NULL;
    }

    if ((p->xxhash_state = XXH32_createState()) == NULL) {
        Py_DECREF(p);
        PyErr_NoMemory();
        return NULL;
    }

    p->seed = self->seed;
    XXH32_copyState(p->xxhash_state, self->xxhash_state);

    return (PyObject *)p;
}

PyDoc_STRVAR(
    PYXXH32_reset_doc,
    "reset()\n\n"
    "Reset state.");

static PyObject *PYXXH32_reset(PYXXH32Object *self)
{
    XXH32_reset(self->xxhash_state, self->seed);
    Py_RETURN_NONE;
}

static PyMethodDef PYXXH32_methods[] = {
    {"update", (PyCFunction)PYXXH32_update, METH_VARARGS, PYXXH32_update_doc},
    {"digest", (PyCFunction)PYXXH32_digest, METH_NOARGS, PYXXH32_digest_doc},
    {"hexdigest", (PyCFunction)PYXXH32_hexdigest, METH_NOARGS, PYXXH32_hexdigest_doc},
    {"intdigest", (PyCFunction)PYXXH32_intdigest, METH_NOARGS, PYXXH32_intdigest_doc},
    {"copy", (PyCFunction)PYXXH32_copy, METH_NOARGS, PYXXH32_copy_doc},
    {"reset", (PyCFunction)PYXXH32_reset, METH_NOARGS, PYXXH32_reset_doc},
    {NULL, NULL, 0, NULL}
};

static PyObject *PYXXH32_get_block_size(PYXXH32Object *self, void *closure)
{
    return PyLong_FromLong(XXH32_BLOCKSIZE);
}

static PyObject *
PYXXH32_get_digest_size(PYXXH32Object *self, void *closure)
{
    return PyLong_FromLong(XXH32_DIGESTSIZE);
}

static PyObject *
PYXXH32_get_name(PYXXH32Object *self, void *closure)
{
    return PyUnicode_FromStringAndSize("XXH32", strlen("XXH32"));
}

static PyObject *
PYXXH32_get_seed(PYXXH32Object *self, void *closure)
{
    return PyLong_FromUnsignedLong(self->seed);
}

static PyGetSetDef PYXXH32_getseters[] = {
    {
        "digest_size",
        (getter)PYXXH32_get_digest_size, NULL,
        "Digest size.",
        NULL
    },
    {
        "block_size",
        (getter)PYXXH32_get_block_size, NULL,
        "Block size.",
        NULL
    },
    {
        "name",
        (getter)PYXXH32_get_name, NULL,
        "Name. Always XXH32.",
        NULL
    },
    {
        "digestsize",
        (getter)PYXXH32_get_digest_size, NULL,
        "Digest size.",
        NULL
    },
    {
        "seed",
        (getter)PYXXH32_get_seed, NULL,
        "Seed.",
        NULL
    },
    {NULL}  /* Sentinel */
};

PyDoc_STRVAR(
    PYXXH32Type_doc,
    "An xxh32 represents the object used to calculate the XXH32 hash of a\n"
    "string of information.\n"
    "\n"
    "Methods:\n"
    "\n"
    "update(input) -- updates the current digest with the provided string.\n"
    "digest() -- return the current digest value\n"
    "hexdigest() -- return the current digest as a string of hexadecimal digits\n"
    "intdigest() -- return the current digest as an integer\n"
    "copy() -- return a copy of the current xxh32 object");

static PyTypeObject PYXXH32Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "xxhash.xxh32",                /* tp_name */
    sizeof(PYXXH32Object),         /* tp_basicsize */
    0,                             /* tp_itemsize */
    (destructor)PYXXH32_dealloc,   /* tp_dealloc */
    0,                             /* tp_print */
    0,                             /* tp_getattr */
    0,                             /* tp_setattr */
    0,                             /* tp_compare */
    0,                             /* tp_repr */
    0,                             /* tp_as_number */
    0,                             /* tp_as_sequence */
    0,                             /* tp_as_mapping */
    0,                             /* tp_hash */
    0,                             /* tp_call */
    0,                             /* tp_str */
    0,                             /* tp_getattro */
    0,                             /* tp_setattro */
    0,                             /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_VECTORCALL,  /* tp_flags */
    PYXXH32Type_doc,               /* tp_doc */
    0,                             /* tp_traverse */
    0,                             /* tp_clear */
    0,                             /* tp_richcompare */
    0,                             /* tp_weaklistoffset */
    0,                             /* tp_iter */
    0,                             /* tp_iternext */
    PYXXH32_methods,               /* tp_methods */
    0,                             /* tp_members */
    PYXXH32_getseters,             /* tp_getset */
    0,                             /* tp_base */
    0,                             /* tp_dict */
    0,                             /* tp_descr_get */
    0,                             /* tp_descr_set */
    0,                             /* tp_dictoffset */
    (initproc)PYXXH32_init,        /* tp_init */
    0,                             /* tp_alloc */
    PYXXH32_new,                   /* tp_new */
    0,                             /* tp_free */
    0,                             /* tp_is_gc */
    0,                             /* tp_bases */
    0,                             /* tp_mro */
    0,                             /* tp_cache */
    0,                             /* tp_subclasses */
    0,                             /* tp_weaklist */
    0,                             /* tp_del */
    0,                             /* tp_version_tag */
    0,                             /* tp_finalize */
    PYXXH32_vectorcall,            /* tp_vectorcall */
};


/* XXH64 */

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    XXH64_state_t *xxhash_state;
    XXH64_hash_t seed;
} PYXXH64Object;

static PyTypeObject PYXXH64Type;

static void PYXXH64_dealloc(PYXXH64Object *self)
{
    if (self->xxhash_state)
        XXH64_freeState(self->xxhash_state);
    PyObject_Del(self);
}

static void PYXXH64_do_update(PYXXH64Object *self, Py_buffer *buf)
{
    Py_BEGIN_ALLOW_THREADS
    XXH64_update(self->xxhash_state, buf->buf, buf->len);
    Py_END_ALLOW_THREADS

    PyBuffer_Release(buf);
}

static PyObject *
PYXXH64_vectorcall(PyObject *type, PyObject *const *args,
                   size_t nargsf, PyObject *kwnames)
{
    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;

    if (_parse_fastcall_args(args, nargs, kwnames, "xxhash.xxh64()", 0,
                             &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    PYXXH64Object *self = (PYXXH64Object *)
        ((PyTypeObject *)type)->tp_alloc((PyTypeObject *)type, 0);
    if (self == NULL) {
        PyBuffer_Release(&buf);
        Py_XDECREF(buf_owner);
        return NULL;
    }

    self->xxhash_state = XXH64_createState();
    if (self->xxhash_state == NULL) {
        Py_DECREF(self);
        PyBuffer_Release(&buf);
        Py_XDECREF(buf_owner);
        return PyErr_NoMemory();
    }
    self->seed = seed;
    XXH64_reset(self->xxhash_state, seed);

    if (buf.buf) {
        Py_BEGIN_ALLOW_THREADS
        XXH64_update(self->xxhash_state, buf.buf, buf.len);
        Py_END_ALLOW_THREADS
        PyBuffer_Release(&buf);
    }
    Py_XDECREF(buf_owner);
    return (PyObject *)self;
}
static PyObject *PYXXH64_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PYXXH64Object *self;

    if ((self = PyObject_New(PYXXH64Object, &PYXXH64Type)) == NULL) {
        return NULL;
    }

    if ((self->xxhash_state = XXH64_createState()) == NULL) {
        Py_DECREF(self);
        PyErr_NoMemory();
        return NULL;
    }

    self->seed = 0;
    XXH64_reset(self->xxhash_state, 0);

    return (PyObject *)self;
}

static int PYXXH64_init(PYXXH64Object *self, PyObject *args, PyObject *kwargs)
{
    XXH64_hash_t seed = 0;
    char *keywords[] = {"input", "seed", NULL};
    Py_buffer buf;

    buf.buf = buf.obj = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|s*K:__init__", keywords, &buf, &seed)) {
        return -1;
    }

    self->seed = seed;
    XXH64_reset(self->xxhash_state, seed);

    if (buf.buf) {
        PYXXH64_do_update(self, &buf);
    }

    return 0;
}

PyDoc_STRVAR(
    PYXXH64_update_doc,
    "update (input)\n\n"
    "Update the xxh64 object with the string input. Repeated calls are\n"
    "equivalent to a single call with the concatenation of all the arguments.");

static PyObject *PYXXH64_update(PYXXH64Object *self, PyObject *args)
{
    Py_buffer buf;

    buf.buf = buf.obj = NULL;

    if (!PyArg_ParseTuple(args, "s*:update", &buf)) {
        return NULL;
    }

    PYXXH64_do_update(self, &buf);

    Py_RETURN_NONE;
}

PyDoc_STRVAR(
    PYXXH64_digest_doc,
    "digest() -> string\n\n"
    "Return the digest of the strings passed to the update() method so\n"
    "far. This is a 8-byte string which may contain non-ASCII characters,\n"
    "including null bytes.");

static PyObject *PYXXH64_digest(PYXXH64Object *self)
{
    char retbuf[XXH64_DIGESTSIZE];
    XXH64_hash_t intdigest;

    intdigest = XXH64_digest(self->xxhash_state);
    XXH64_canonicalFromHash((XXH64_canonical_t *)retbuf, intdigest);

    return PyBytes_FromStringAndSize(retbuf, sizeof(retbuf));
}

PyDoc_STRVAR(
    PYXXH64_hexdigest_doc,
    "hexdigest() -> string\n\n"
    "Like digest(), but returns the digest as a string of hexadecimal digits.");

static PyObject *PYXXH64_hexdigest(PYXXH64Object *self)
{
    XXH64_hash_t intdigest;
    char digest[XXH64_DIGESTSIZE];
    char retbuf[XXH64_DIGESTSIZE * 2];
    int i, j;

    intdigest = XXH64_digest(self->xxhash_state);
    XXH64_canonicalFromHash((XXH64_canonical_t *)digest, intdigest);

    for (i = j = 0; i < XXH64_DIGESTSIZE; i++) {
        unsigned char c;
        c = (digest[i] >> 4) & 0xf;
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
        c = (digest[i] & 0xf);
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
    }

    return PyUnicode_FromStringAndSize(retbuf, sizeof(retbuf));
}


PyDoc_STRVAR(
    PYXXH64_intdigest_doc,
    "intdigest() -> int\n\n"
    "Like digest(), but returns the digest as an integer, which is the integer\n"
    "returned by xxhash C API");

static PyObject *PYXXH64_intdigest(PYXXH64Object *self)
{
    XXH64_hash_t digest = XXH64_digest(self->xxhash_state);
    return PyLong_FromUnsignedLongLong(digest);
}

PyDoc_STRVAR(
    PYXXH64_copy_doc,
    "copy() -> xxh64 object\n\n"
    "Return a copy (``clone'') of the xxh64 object.");

static PyObject *PYXXH64_copy(PYXXH64Object *self)
{
    PYXXH64Object *p;

    if ((p = PyObject_New(PYXXH64Object, &PYXXH64Type)) == NULL) {
        return NULL;
    }

    if ((p->xxhash_state = XXH64_createState()) == NULL) {
        Py_DECREF(p);
        PyErr_NoMemory();
        return NULL;
    }

    p->seed = self->seed;
    XXH64_copyState(p->xxhash_state, self->xxhash_state);

    return (PyObject *)p;
}

PyDoc_STRVAR(
    PYXXH64_reset_doc,
    "reset()\n\n"
    "Reset state.");

static PyObject *PYXXH64_reset(PYXXH64Object *self)
{
    XXH64_reset(self->xxhash_state, self->seed);
    Py_RETURN_NONE;
}

static PyMethodDef PYXXH64_methods[] = {
    {"update", (PyCFunction)PYXXH64_update, METH_VARARGS, PYXXH64_update_doc},
    {"digest", (PyCFunction)PYXXH64_digest, METH_NOARGS, PYXXH64_digest_doc},
    {"hexdigest", (PyCFunction)PYXXH64_hexdigest, METH_NOARGS, PYXXH64_hexdigest_doc},
    {"intdigest", (PyCFunction)PYXXH64_intdigest, METH_NOARGS, PYXXH64_intdigest_doc},
    {"copy", (PyCFunction)PYXXH64_copy, METH_NOARGS, PYXXH64_copy_doc},
    {"reset", (PyCFunction)PYXXH64_reset, METH_NOARGS, PYXXH64_reset_doc},
    {NULL, NULL, 0, NULL}
};

static PyObject *PYXXH64_get_block_size(PYXXH64Object *self, void *closure)
{
    return PyLong_FromLong(XXH64_BLOCKSIZE);
}

static PyObject *
PYXXH64_get_digest_size(PYXXH64Object *self, void *closure)
{
    return PyLong_FromLong(XXH64_DIGESTSIZE);
}

static PyObject *
PYXXH64_get_name(PYXXH64Object *self, void *closure)
{
    return PyUnicode_FromStringAndSize("XXH64", strlen("XXH64"));
}

static PyObject *
PYXXH64_get_seed(PYXXH64Object *self, void *closure)
{
    return PyLong_FromUnsignedLongLong(self->seed);
}

static PyGetSetDef PYXXH64_getseters[] = {
    {
        "digest_size",
        (getter)PYXXH64_get_digest_size, NULL,
        "Digest size.",
        NULL
    },
    {
        "block_size",
        (getter)PYXXH64_get_block_size, NULL,
        "Block size.",
        NULL
    },
    {
        "name",
        (getter)PYXXH64_get_name, NULL,
        "Name. Always XXH64.",
        NULL
    },
    {
        "digestsize",
        (getter)PYXXH64_get_digest_size, NULL,
        "Digest size.",
        NULL
    },
    {
        "seed",
        (getter)PYXXH64_get_seed, NULL,
        "Seed.",
        NULL
    },
    {NULL}  /* Sentinel */
};

PyDoc_STRVAR(
    PYXXH64Type_doc,
    "An xxh64 represents the object used to calculate the XXH64 hash of a\n"
    "string of information.\n"
    "\n"
    "Methods:\n"
    "\n"
    "update(input) -- updates the current digest with an additional string\n"
    "digest() -- return the current digest value\n"
    "hexdigest() -- return the current digest as a string of hexadecimal digits\n"
    "intdigest() -- return the current digest as an integer\n"
    "copy() -- return a copy of the current xxh64 object");

static PyTypeObject PYXXH64Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "xxhash.xxh64",                /* tp_name */
    sizeof(PYXXH64Object),         /* tp_basicsize */
    0,                             /* tp_itemsize */
    (destructor)PYXXH64_dealloc,   /* tp_dealloc */
    0,                             /* tp_print */
    0,                             /* tp_getattr */
    0,                             /* tp_setattr */
    0,                             /* tp_compare */
    0,                             /* tp_repr */
    0,                             /* tp_as_number */
    0,                             /* tp_as_sequence */
    0,                             /* tp_as_mapping */
    0,                             /* tp_hash */
    0,                             /* tp_call */
    0,                             /* tp_str */
    0,                             /* tp_getattro */
    0,                             /* tp_setattro */
    0,                             /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_VECTORCALL,  /* tp_flags */
    PYXXH64Type_doc,               /* tp_doc */
    0,                             /* tp_traverse */
    0,                             /* tp_clear */
    0,                             /* tp_richcompare */
    0,                             /* tp_weaklistoffset */
    0,                             /* tp_iter */
    0,                             /* tp_iternext */
    PYXXH64_methods,               /* tp_methods */
    0,                             /* tp_members */
    PYXXH64_getseters,             /* tp_getset */
    0,                             /* tp_base */
    0,                             /* tp_dict */
    0,                             /* tp_descr_get */
    0,                             /* tp_descr_set */
    0,                             /* tp_dictoffset */
    (initproc)PYXXH64_init,        /* tp_init */
    0,                             /* tp_alloc */
    PYXXH64_new,                   /* tp_new */
    0,                             /* tp_free */
    0,                             /* tp_is_gc */
    0,                             /* tp_bases */
    0,                             /* tp_mro */
    0,                             /* tp_cache */
    0,                             /* tp_subclasses */
    0,                             /* tp_weaklist */
    0,                             /* tp_del */
    0,                             /* tp_version_tag */
    0,                             /* tp_finalize */
    PYXXH64_vectorcall,            /* tp_vectorcall */
};

/* XXH3_64 */

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    XXH3_state_t *xxhash_state;
    XXH64_hash_t seed;
} PYXXH3_64Object;

static PyTypeObject PYXXH3_64Type;

static void PYXXH3_64_dealloc(PYXXH3_64Object *self)
{
    if (self->xxhash_state)
        XXH3_freeState(self->xxhash_state);
    PyObject_Del(self);
}

static void PYXXH3_64_do_update(PYXXH3_64Object *self, Py_buffer *buf)
{
    Py_BEGIN_ALLOW_THREADS
    XXH3_64bits_update(self->xxhash_state, buf->buf, buf->len);
    Py_END_ALLOW_THREADS

    PyBuffer_Release(buf);
}

static PyObject *
PYXXH3_64_vectorcall(PyObject *type, PyObject *const *args,
                     size_t nargsf, PyObject *kwnames)
{
    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;

    if (_parse_fastcall_args(args, nargs, kwnames, "xxhash.xxh3_64()", 0,
                             &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    PYXXH3_64Object *self = (PYXXH3_64Object *)
        ((PyTypeObject *)type)->tp_alloc((PyTypeObject *)type, 0);
    if (self == NULL) {
        PyBuffer_Release(&buf);
        Py_XDECREF(buf_owner);
        return NULL;
    }

    self->xxhash_state = XXH3_createState();
    if (self->xxhash_state == NULL) {
        Py_DECREF(self);
        PyBuffer_Release(&buf);
        Py_XDECREF(buf_owner);
        return PyErr_NoMemory();
    }
    self->seed = seed;
    XXH3_64bits_reset_withSeed(self->xxhash_state, seed);

    if (buf.buf) {
        Py_BEGIN_ALLOW_THREADS
        XXH3_64bits_update(self->xxhash_state, buf.buf, buf.len);
        Py_END_ALLOW_THREADS
        PyBuffer_Release(&buf);
    }
    Py_XDECREF(buf_owner);
    return (PyObject *)self;
}
static PyObject *PYXXH3_64_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PYXXH3_64Object *self;

    if ((self = PyObject_New(PYXXH3_64Object, &PYXXH3_64Type)) == NULL) {
        return NULL;
    }

    if ((self->xxhash_state = XXH3_createState()) == NULL) {
        Py_DECREF(self);
        PyErr_NoMemory();
        return NULL;
    }

    self->seed = 0;
    XXH3_64bits_reset_withSeed(self->xxhash_state, 0);

    return (PyObject *)self;
}

static int PYXXH3_64_init(PYXXH3_64Object *self, PyObject *args, PyObject *kwargs)
{
    XXH64_hash_t seed = 0;
    char *keywords[] = {"input", "seed", NULL};
    Py_buffer buf;

    buf.buf = buf.obj = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|s*K:__init__", keywords, &buf, &seed)) {
        return -1;
    }

    self->seed = seed;
    XXH3_64bits_reset_withSeed(self->xxhash_state, seed);

    if (buf.buf) {
        PYXXH3_64_do_update(self, &buf);
    }

    return 0;
}

PyDoc_STRVAR(
    PYXXH3_64_update_doc,
    "update (input)\n\n"
    "Update the xxh3_64 object with the string input. Repeated calls are\n"
    "equivalent to a single call with the concatenation of all the arguments.");

static PyObject *PYXXH3_64_update(PYXXH3_64Object *self, PyObject *args)
{
    Py_buffer buf;

    buf.buf = buf.obj = NULL;

    if (!PyArg_ParseTuple(args, "s*:update", &buf)) {
        return NULL;
    }

    PYXXH3_64_do_update(self, &buf);

    Py_RETURN_NONE;
}

PyDoc_STRVAR(
    PYXXH3_64_digest_doc,
    "digest() -> string\n\n"
    "Return the digest of the strings passed to the update() method so\n"
    "far. This is a 8-byte string which may contain non-ASCII characters,\n"
    "including null bytes.");

static PyObject *PYXXH3_64_digest(PYXXH3_64Object *self)
{
    char retbuf[XXH64_DIGESTSIZE];
    XXH64_hash_t intdigest;

    intdigest = XXH3_64bits_digest(self->xxhash_state);
    XXH64_canonicalFromHash((XXH64_canonical_t *)retbuf, intdigest);

    return PyBytes_FromStringAndSize(retbuf, sizeof(retbuf));
}

PyDoc_STRVAR(
    PYXXH3_64_hexdigest_doc,
    "hexdigest() -> string\n\n"
    "Like digest(), but returns the digest as a string of hexadecimal digits.");

static PyObject *PYXXH3_64_hexdigest(PYXXH3_64Object *self)
{
    XXH64_hash_t intdigest;
    char digest[XXH64_DIGESTSIZE];
    char retbuf[XXH64_DIGESTSIZE * 2];
    int i, j;


    intdigest = XXH3_64bits_digest(self->xxhash_state);
    XXH64_canonicalFromHash((XXH64_canonical_t *)digest, intdigest);

    for (i = j = 0; i < XXH64_DIGESTSIZE; i++) {
        unsigned char c;
        c = (digest[i] >> 4) & 0xf;
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
        c = (digest[i] & 0xf);
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
    }

    return PyUnicode_FromStringAndSize(retbuf, sizeof(retbuf));
}


PyDoc_STRVAR(
    PYXXH3_64_intdigest_doc,
    "intdigest() -> int\n\n"
    "Like digest(), but returns the digest as an integer, which is the integer\n"
    "returned by xxhash C API");

static PyObject *PYXXH3_64_intdigest(PYXXH3_64Object *self)
{
    XXH64_hash_t intdigest = XXH3_64bits_digest(self->xxhash_state);
    return PyLong_FromUnsignedLongLong(intdigest);
}

PyDoc_STRVAR(
    PYXXH3_64_copy_doc,
    "copy() -> xxh64 object\n\n"
    "Return a copy (``clone'') of the xxh64 object.");

static PyObject *PYXXH3_64_copy(PYXXH3_64Object *self)
{
    PYXXH3_64Object *p;

    if ((p = PyObject_New(PYXXH3_64Object, &PYXXH3_64Type)) == NULL) {
        return NULL;
    }

    if ((p->xxhash_state = XXH3_createState()) == NULL) {
        Py_DECREF(p);
        PyErr_NoMemory();
        return NULL;
    }

    p->seed = self->seed;
    XXH3_copyState(p->xxhash_state, self->xxhash_state);
#if XXH_VERSION_NUMBER < 704
    // v0.7.3 and earlier have a bug where states reset with a seed
    // will have a wild pointer to the original state when copied,
    // causing a use-after-free if the original is freed.
    if (p->xxhash_state->secret == &self->xxhash_state->customSecret[0])
        p->xxhash_state->secret = &p->xxhash_state->customSecret[0];
#endif

    return (PyObject *)p;
}

PyDoc_STRVAR(
    PYXXH3_64_reset_doc,
    "reset()\n\n"
    "Reset state.");

static PyObject *PYXXH3_64_reset(PYXXH3_64Object *self)
{
    XXH3_64bits_reset_withSeed(self->xxhash_state, self->seed);
    Py_RETURN_NONE;
}

static PyMethodDef PYXXH3_64_methods[] = {
    {"update", (PyCFunction)PYXXH3_64_update, METH_VARARGS, PYXXH3_64_update_doc},
    {"digest", (PyCFunction)PYXXH3_64_digest, METH_NOARGS, PYXXH3_64_digest_doc},
    {"hexdigest", (PyCFunction)PYXXH3_64_hexdigest, METH_NOARGS, PYXXH3_64_hexdigest_doc},
    {"intdigest", (PyCFunction)PYXXH3_64_intdigest, METH_NOARGS, PYXXH3_64_intdigest_doc},
    {"copy", (PyCFunction)PYXXH3_64_copy, METH_NOARGS, PYXXH3_64_copy_doc},
    {"reset", (PyCFunction)PYXXH3_64_reset, METH_NOARGS, PYXXH3_64_reset_doc},
    {NULL, NULL, 0, NULL}
};

static PyObject *PYXXH3_64_get_block_size(PYXXH3_64Object *self, void *closure)
{
    return PyLong_FromLong(XXH64_BLOCKSIZE);
}

static PyObject *
PYXXH3_64_get_digest_size(PYXXH3_64Object *self, void *closure)
{
    return PyLong_FromLong(XXH64_DIGESTSIZE);
}

static PyObject *
PYXXH3_64_get_name(PYXXH3_64Object *self, void *closure)
{
    return PyUnicode_FromStringAndSize("XXH3_64", strlen("XXH3_64"));
}

static PyObject *
PYXXH3_64_get_seed(PYXXH3_64Object *self, void *closure)
{
    return PyLong_FromUnsignedLongLong(self->seed);
}

static PyGetSetDef PYXXH3_64_getseters[] = {
    {
        "digest_size",
        (getter)PYXXH3_64_get_digest_size, NULL,
        "Digest size.",
        NULL
    },
    {
        "block_size",
        (getter)PYXXH3_64_get_block_size, NULL,
        "Block size.",
        NULL
    },
    {
        "name",
        (getter)PYXXH3_64_get_name, NULL,
        "Name. Always XXH3_64.",
        NULL
    },
    {
        "digestsize",
        (getter)PYXXH3_64_get_digest_size, NULL,
        "Digest size.",
        NULL
    },
    {
        "seed",
        (getter)PYXXH3_64_get_seed, NULL,
        "Seed.",
        NULL
    },
    {NULL}  /* Sentinel */
};

PyDoc_STRVAR(
    PYXXH3_64Type_doc,
    "An xxh3_64 represents the object used to calculate the XXH3_64 hash of a\n"
    "string of information.\n"
    "\n"
    "Methods:\n"
    "\n"
    "update(input) -- updates the current digest with an additional string\n"
    "digest() -- return the current digest value\n"
    "hexdigest() -- return the current digest as a string of hexadecimal digits\n"
    "intdigest() -- return the current digest as an integer\n"
    "copy() -- return a copy of the current xxh64 object");

static PyTypeObject PYXXH3_64Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "xxhash.xxh3_64",                /* tp_name */
    sizeof(PYXXH3_64Object),         /* tp_basicsize */
    0,                             /* tp_itemsize */
    (destructor)PYXXH3_64_dealloc,   /* tp_dealloc */
    0,                             /* tp_print */
    0,                             /* tp_getattr */
    0,                             /* tp_setattr */
    0,                             /* tp_compare */
    0,                             /* tp_repr */
    0,                             /* tp_as_number */
    0,                             /* tp_as_sequence */
    0,                             /* tp_as_mapping */
    0,                             /* tp_hash */
    0,                             /* tp_call */
    0,                             /* tp_str */
    0,                             /* tp_getattro */
    0,                             /* tp_setattro */
    0,                             /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_VECTORCALL,  /* tp_flags */
    PYXXH3_64Type_doc,               /* tp_doc */
    0,                             /* tp_traverse */
    0,                             /* tp_clear */
    0,                             /* tp_richcompare */
    0,                             /* tp_weaklistoffset */
    0,                             /* tp_iter */
    0,                             /* tp_iternext */
    PYXXH3_64_methods,               /* tp_methods */
    0,                             /* tp_members */
    PYXXH3_64_getseters,             /* tp_getset */
    0,                             /* tp_base */
    0,                             /* tp_dict */
    0,                             /* tp_descr_get */
    0,                             /* tp_descr_set */
    0,                             /* tp_dictoffset */
    (initproc)PYXXH3_64_init,        /* tp_init */
    0,                             /* tp_alloc */
    PYXXH3_64_new,                   /* tp_new */
    0,                             /* tp_free */
    0,                             /* tp_is_gc */
    0,                             /* tp_bases */
    0,                             /* tp_mro */
    0,                             /* tp_cache */
    0,                             /* tp_subclasses */
    0,                             /* tp_weaklist */
    0,                             /* tp_del */
    0,                             /* tp_version_tag */
    0,                             /* tp_finalize */
    PYXXH3_64_vectorcall,            /* tp_vectorcall */
};


/* XXH3_128 */

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    XXH3_state_t *xxhash_state;
    XXH64_hash_t seed;
} PYXXH3_128Object;

static PyTypeObject PYXXH3_128Type;

static void PYXXH3_128_dealloc(PYXXH3_128Object *self)
{
    if (self->xxhash_state)
        XXH3_freeState(self->xxhash_state);
    PyObject_Del(self);
}

static void PYXXH3_128_do_update(PYXXH3_128Object *self, Py_buffer *buf)
{
    Py_BEGIN_ALLOW_THREADS
    XXH3_128bits_update(self->xxhash_state, buf->buf, buf->len);
    Py_END_ALLOW_THREADS

    PyBuffer_Release(buf);
}

static PyObject *
PYXXH3_128_vectorcall(PyObject *type, PyObject *const *args,
                      size_t nargsf, PyObject *kwnames)
{
    Py_ssize_t nargs = PyVectorcall_NARGS(nargsf);
    XXH64_hash_t seed = 0;
    Py_buffer buf;
    PyObject *buf_owner;
    unsigned long long raw_seed;

    if (_parse_fastcall_args(args, nargs, kwnames, "xxhash.xxh3_128()", 0,
                             &buf, &buf_owner, &raw_seed) < 0)
        return NULL;
    seed = (XXH64_hash_t)raw_seed;

    PYXXH3_128Object *self = (PYXXH3_128Object *)
        ((PyTypeObject *)type)->tp_alloc((PyTypeObject *)type, 0);
    if (self == NULL) {
        PyBuffer_Release(&buf);
        Py_XDECREF(buf_owner);
        return NULL;
    }

    self->xxhash_state = XXH3_createState();
    if (self->xxhash_state == NULL) {
        Py_DECREF(self);
        PyBuffer_Release(&buf);
        Py_XDECREF(buf_owner);
        return PyErr_NoMemory();
    }
    self->seed = seed;
    XXH3_128bits_reset_withSeed(self->xxhash_state, seed);

    if (buf.buf) {
        Py_BEGIN_ALLOW_THREADS
        XXH3_128bits_update(self->xxhash_state, buf.buf, buf.len);
        Py_END_ALLOW_THREADS
        PyBuffer_Release(&buf);
    }
    Py_XDECREF(buf_owner);
    return (PyObject *)self;
}
static PyObject *PYXXH3_128_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PYXXH3_128Object *self;

    if ((self = PyObject_New(PYXXH3_128Object, &PYXXH3_128Type)) == NULL) {
        return NULL;
    }

    if ((self->xxhash_state = XXH3_createState()) == NULL) {
        Py_DECREF(self);
        PyErr_NoMemory();
        return NULL;
    }

    self->seed = 0;
    XXH3_128bits_reset_withSeed(self->xxhash_state, 0);

    return (PyObject *)self;
}

static int PYXXH3_128_init(PYXXH3_128Object *self, PyObject *args, PyObject *kwargs)
{
    XXH64_hash_t seed = 0;
    char *keywords[] = {"input", "seed", NULL};
    Py_buffer buf;

    buf.buf = buf.obj = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|s*K:__init__", keywords, &buf, &seed)) {
        return -1;
    }

    self->seed = seed;
    XXH3_128bits_reset_withSeed(self->xxhash_state, seed);

    if (buf.buf) {
        PYXXH3_128_do_update(self, &buf);
    }

    return 0;
}

PyDoc_STRVAR(
    PYXXH3_128_update_doc,
    "update (input)\n\n"
    "Update the xxh3_128 object with the string input. Repeated calls are\n"
    "equivalent to a single call with the concatenation of all the arguments.");

static PyObject *PYXXH3_128_update(PYXXH3_128Object *self, PyObject *args)
{
    Py_buffer buf;
    buf.buf = buf.obj = NULL;

    if (!PyArg_ParseTuple(args, "s*:update", &buf)) {
        return NULL;
    }

    PYXXH3_128_do_update(self, &buf);

    Py_RETURN_NONE;
}

PyDoc_STRVAR(
    PYXXH3_128_digest_doc,
    "digest() -> string\n\n"
    "Return the digest of the strings passed to the update() method so\n"
    "far. This is a 16-byte string which may contain non-ASCII characters,\n"
    "including null bytes.");

static PyObject *PYXXH3_128_digest(PYXXH3_128Object *self)
{
    char retbuf[XXH128_DIGESTSIZE];
    XXH128_hash_t intdigest;

    intdigest = XXH3_128bits_digest(self->xxhash_state);
    XXH128_canonicalFromHash((XXH128_canonical_t *)retbuf, intdigest);

    return PyBytes_FromStringAndSize(retbuf, sizeof(retbuf));
}

PyDoc_STRVAR(
    PYXXH3_128_hexdigest_doc,
    "hexdigest() -> string\n\n"
    "Like digest(), but returns the digest as a string of hexadecimal digits.");

static PyObject *PYXXH3_128_hexdigest(PYXXH3_128Object *self)
{
    XXH128_hash_t intdigest;
    char digest[XXH128_DIGESTSIZE];
    char retbuf[XXH128_DIGESTSIZE * 2];
    int i, j;

    intdigest = XXH3_128bits_digest(self->xxhash_state);
    XXH128_canonicalFromHash((XXH128_canonical_t *)digest, intdigest);

    for (i = j = 0; i < XXH128_DIGESTSIZE; i++) {
        unsigned char c;
        c = (digest[i] >> 4) & 0xf;
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
        c = (digest[i] & 0xf);
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
    }

    return PyUnicode_FromStringAndSize(retbuf, sizeof(retbuf));
}


PyDoc_STRVAR(
    PYXXH3_128_intdigest_doc,
    "intdigest() -> int\n\n"
    "Like digest(), but returns the digest as an integer, which is the integer\n"
    "returned by xxhash C API");

static PyObject *PYXXH3_128_intdigest(PYXXH3_128Object *self)
{
    XXH128_hash_t intdigest;
    PyObject *result, *high, *low, *sixtyfour;

    intdigest = XXH3_128bits_digest(self->xxhash_state);

    sixtyfour = PyLong_FromLong(64);
    low = PyLong_FromUnsignedLongLong(intdigest.low64);
    high = PyLong_FromUnsignedLongLong(intdigest.high64);
    result = NULL;

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

PyDoc_STRVAR(
    PYXXH3_128_copy_doc,
    "copy() -> xxh3_128 object\n\n"
    "Return a copy (``clone'') of the xxh3_128 object.");

static PyObject *PYXXH3_128_copy(PYXXH3_128Object *self)
{
    PYXXH3_128Object *p;

    if ((p = PyObject_New(PYXXH3_128Object, &PYXXH3_128Type)) == NULL) {
        return NULL;
    }

    if ((p->xxhash_state = XXH3_createState()) == NULL) {
        Py_DECREF(p);
        PyErr_NoMemory();
        return NULL;
    }

    p->seed = self->seed;
    XXH3_copyState(p->xxhash_state, self->xxhash_state);
#if XXH_VERSION_NUMBER < 704
    // v0.7.3 and earlier have a bug where states reset with a seed
    // will have a wild pointer to the original state when copied,
    // causing a use-after-free if the original is freed.
    if (p->xxhash_state->secret == &self->xxhash_state->customSecret[0])
        p->xxhash_state->secret = &p->xxhash_state->customSecret[0];
#endif

    return (PyObject *)p;
}

PyDoc_STRVAR(
    PYXXH3_128_reset_doc,
    "reset()\n\n"
    "Reset state.");

static PyObject *PYXXH3_128_reset(PYXXH3_128Object *self)
{
    XXH3_128bits_reset_withSeed(self->xxhash_state, self->seed);
    Py_RETURN_NONE;
}

static PyMethodDef PYXXH3_128_methods[] = {
    {"update", (PyCFunction)PYXXH3_128_update, METH_VARARGS, PYXXH3_128_update_doc},
    {"digest", (PyCFunction)PYXXH3_128_digest, METH_NOARGS, PYXXH3_128_digest_doc},
    {"hexdigest", (PyCFunction)PYXXH3_128_hexdigest, METH_NOARGS, PYXXH3_128_hexdigest_doc},
    {"intdigest", (PyCFunction)PYXXH3_128_intdigest, METH_NOARGS, PYXXH3_128_intdigest_doc},
    {"copy", (PyCFunction)PYXXH3_128_copy, METH_NOARGS, PYXXH3_128_copy_doc},
    {"reset", (PyCFunction)PYXXH3_128_reset, METH_NOARGS, PYXXH3_128_reset_doc},
    {NULL, NULL, 0, NULL}
};

static PyObject *PYXXH3_128_get_block_size(PYXXH3_128Object *self, void *closure)
{
    return PyLong_FromLong(XXH128_BLOCKSIZE);
}

static PyObject *
PYXXH3_128_get_digest_size(PYXXH3_128Object *self, void *closure)
{
    return PyLong_FromLong(XXH128_DIGESTSIZE);
}

static PyObject *
PYXXH3_128_get_name(PYXXH3_128Object *self, void *closure)
{
    return PyUnicode_FromStringAndSize("XXH3_128", strlen("XXH3_128"));
}

static PyObject *
PYXXH3_128_get_seed(PYXXH3_128Object *self, void *closure)
{
    return PyLong_FromUnsignedLongLong(self->seed);
}

static PyGetSetDef PYXXH3_128_getseters[] = {
    {
        "digest_size",
        (getter)PYXXH3_128_get_digest_size, NULL,
        "Digest size.",
        NULL
    },
    {
        "block_size",
        (getter)PYXXH3_128_get_block_size, NULL,
        "Block size.",
        NULL
    },
    {
        "name",
        (getter)PYXXH3_128_get_name, NULL,
        "Name. Always XXH3_128.",
        NULL
    },
    {
        "digestsize",
        (getter)PYXXH3_128_get_digest_size, NULL,
        "Digest size.",
        NULL
    },
    {
        "seed",
        (getter)PYXXH3_128_get_seed, NULL,
        "Seed.",
        NULL
    },
    {NULL}  /* Sentinel */
};

PyDoc_STRVAR(
    PYXXH3_128Type_doc,
    "An xxh3_128 represents the object used to calculate the XXH3_128 hash of a\n"
    "string of information.\n"
    "\n"
    "Methods:\n"
    "\n"
    "update(input) -- updates the current digest with an additional string\n"
    "digest() -- return the current digest value\n"
    "hexdigest() -- return the current digest as a string of hexadecimal digits\n"
    "intdigest() -- return the current digest as an integer\n"
    "copy() -- return a copy of the current xxh3_128 object");

static PyTypeObject PYXXH3_128Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "xxhash.xxh3_128",                /* tp_name */
    sizeof(PYXXH3_128Object),         /* tp_basicsize */
    0,                             /* tp_itemsize */
    (destructor)PYXXH3_128_dealloc,   /* tp_dealloc */
    0,                             /* tp_print */
    0,                             /* tp_getattr */
    0,                             /* tp_setattr */
    0,                             /* tp_compare */
    0,                             /* tp_repr */
    0,                             /* tp_as_number */
    0,                             /* tp_as_sequence */
    0,                             /* tp_as_mapping */
    0,                             /* tp_hash */
    0,                             /* tp_call */
    0,                             /* tp_str */
    0,                             /* tp_getattro */
    0,                             /* tp_setattro */
    0,                             /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_VECTORCALL,  /* tp_flags */
    PYXXH3_128Type_doc,               /* tp_doc */
    0,                             /* tp_traverse */
    0,                             /* tp_clear */
    0,                             /* tp_richcompare */
    0,                             /* tp_weaklistoffset */
    0,                             /* tp_iter */
    0,                             /* tp_iternext */
    PYXXH3_128_methods,               /* tp_methods */
    0,                             /* tp_members */
    PYXXH3_128_getseters,             /* tp_getset */
    0,                             /* tp_base */
    0,                             /* tp_dict */
    0,                             /* tp_descr_get */
    0,                             /* tp_descr_set */
    0,                             /* tp_dictoffset */
    (initproc)PYXXH3_128_init,        /* tp_init */
    0,                             /* tp_alloc */
    PYXXH3_128_new,                   /* tp_new */
    0,                             /* tp_free */
    0,                             /* tp_is_gc */
    0,                             /* tp_bases */
    0,                             /* tp_mro */
    0,                             /* tp_cache */
    0,                             /* tp_subclasses */
    0,                             /* tp_weaklist */
    0,                             /* tp_del */
    0,                             /* tp_version_tag */
    0,                             /* tp_finalize */
    PYXXH3_128_vectorcall,            /* tp_vectorcall */
};

/*****************************************************************************
 * Module Init ****************************************************************
 ****************************************************************************/

static int _exec(PyObject *module)
{
    if (
        PyModule_AddType(module, &PYXXH32Type) < 0 ||
        PyModule_AddType(module, &PYXXH64Type) < 0 ||
        PyModule_AddType(module, &PYXXH3_64Type) < 0 ||
        PyModule_AddType(module, &PYXXH3_128Type) < 0
    ) {
        return -1;
    }

    if (PyModule_AddStringConstant(module, "XXHASH_VERSION", VALUE_TO_STRING(XXHASH_VERSION)) < 0)
        return -1;

    return 0;
}

static PyModuleDef_Slot slots[] = {
    {Py_mod_exec, _exec},
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};

static PyMethodDef methods[] = {
    {"xxh32_digest",       (PyCFunction)xxh32_digest,       METH_FASTCALL | METH_KEYWORDS, "xxh32_digest"},
    {"xxh32_intdigest",    (PyCFunction)xxh32_intdigest,    METH_FASTCALL | METH_KEYWORDS, "xxh32_intdigest"},
    {"xxh32_hexdigest",    (PyCFunction)xxh32_hexdigest,    METH_FASTCALL | METH_KEYWORDS, "xxh32_hexdigest"},
    {"xxh64_digest",       (PyCFunction)xxh64_digest,       METH_FASTCALL | METH_KEYWORDS, "xxh64_digest"},
    {"xxh64_intdigest",    (PyCFunction)xxh64_intdigest,    METH_FASTCALL | METH_KEYWORDS, "xxh64_intdigest"},
    {"xxh64_hexdigest",    (PyCFunction)xxh64_hexdigest,    METH_FASTCALL | METH_KEYWORDS, "xxh64_hexdigest"},
    {"xxh3_64_digest",     (PyCFunction)xxh3_64_digest,     METH_FASTCALL | METH_KEYWORDS, "xxh3_64_digest"},
    {"xxh3_64_intdigest",  (PyCFunction)xxh3_64_intdigest,  METH_FASTCALL | METH_KEYWORDS, "xxh3_64_intdigest"},
    {"xxh3_64_hexdigest",  (PyCFunction)xxh3_64_hexdigest,  METH_FASTCALL | METH_KEYWORDS, "xxh3_64_hexdigest"},
    {"xxh3_128_digest",    (PyCFunction)xxh3_128_digest,    METH_FASTCALL | METH_KEYWORDS, "xxh3_128_digest"},
    {"xxh3_128_intdigest", (PyCFunction)xxh3_128_intdigest, METH_FASTCALL | METH_KEYWORDS, "xxh3_128_intdigest"},
    {"xxh3_128_hexdigest", (PyCFunction)xxh3_128_hexdigest, METH_FASTCALL | METH_KEYWORDS, "xxh3_128_hexdigest"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_xxhash",
    NULL,
    0,
    methods,
    slots,
    NULL,
    NULL,
    NULL
};


PyMODINIT_FUNC
PyInit__xxhash(void)
{
    return PyModuleDef_Init(&moduledef);
}
