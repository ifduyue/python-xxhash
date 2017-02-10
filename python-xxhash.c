/*
 * Copyright (c) 2014-2016, Yue Du
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

#include "xxhash/xxhash.h"

#define TOSTRING(x) #x
#define VALUE_TO_STRING(x) TOSTRING(x)

#define XXHASH_VERSION XXH_VERSION_MAJOR.XXH_VERSION_MINOR.XXH_VERSION_RELEASE
#define XXH32_DIGESTSIZE 4
#define XXH32_BLOCKSIZE 16
#define XXH64_DIGESTSIZE 8
#define XXH64_BLOCKSIZE 32


/*****************************************************************************
 * Helper Functions ***********************************************************
 ****************************************************************************/

/* u2bytes converts an unsigned int to bytes, which are the big-endian
   representation of this integer */
static void u2bytes(unsigned in, char *out)
{
    unsigned char *s = (unsigned char *)out;

    s[0] = (in >> 24) & 0xFF;
    s[1] = (in >> 16) & 0xFF;
    s[2] = (in >> 8) & 0xFF;
    s[3] = in & 0xFF;
    s[4] = '\0';
}

/* ull2bytes converts an unsigned long long to bytes, which are the big-endian
   representation of this integer */
static void ull2bytes(unsigned long long in, char *out)
{
    unsigned char *s = (unsigned char *)out;

    s[0] = (in >> 56) & 0xFF;
    s[1] = (in >> 48) & 0xFF;
    s[2] = (in >> 40) & 0xFF;
    s[3] = (in >> 32) & 0xFF;
    s[4] = (in >> 24) & 0xFF;
    s[5] = (in >> 16) & 0xFF;
    s[6] = (in >> 8) & 0xFF;
    s[7] = in & 0xFF;
    s[8] = '\0';
}

/*****************************************************************************
 * Module Types ***************************************************************
 ****************************************************************************/

/* XXH32 */

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    XXH32_state_t *xxhash_state;
    unsigned int seed;
} PYXXH32Object;

static PyTypeObject PYXXH32Type;

static void PYXXH32_dealloc(PYXXH32Object *self)
{
    XXH32_freeState(self->xxhash_state);
    PyObject_Del(self);
}

/* XXH32 methods */

static PyObject *PYXXH32_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PYXXH32Object *self;

    if ((self = PyObject_New(PYXXH32Object, &PYXXH32Type)) == NULL) {
        return NULL;
    }

    if ((self->xxhash_state = XXH32_createState()) == NULL) {
        return NULL;
    }

    return (PyObject *)self;
}

static int PYXXH32_init(PYXXH32Object *self, PyObject *args, PyObject *kwargs)
{
    unsigned int seed = 0;
    char *keywords[] = {"input", "seed", NULL};
    const char *s = NULL;
    int ns;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|s#I:__init__", keywords, &s, &ns, &seed)) {
        return -1;
    }

    self->seed = seed;
    XXH32_reset(self->xxhash_state, seed);

    if (s) {
        XXH32_update(self->xxhash_state, s, ns);
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
    const char *s;
    int ns;

    if (!PyArg_ParseTuple(args, "s#:update", &s, &ns)) {
        return NULL;
    }

    XXH32_update(self->xxhash_state, s, ns);

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
    PyObject *retval;
    char *retbuf;
    unsigned int digest;

#if PY_MAJOR_VERSION >= 3
    retval = PyBytes_FromStringAndSize(NULL, XXH32_DIGESTSIZE);
#else
    retval = PyString_FromStringAndSize(NULL, XXH32_DIGESTSIZE);
#endif

    if (!retval) {
        return NULL;
    }

#if PY_MAJOR_VERSION >= 3
    retbuf = PyBytes_AS_STRING(retval);
#else
    retbuf = PyString_AS_STRING(retval);
#endif

    if (!retbuf) {
        Py_DECREF(retval);
        return NULL;
    }

    digest = XXH32_digest(self->xxhash_state);
    u2bytes(digest, retbuf);

    return retval;
}

PyDoc_STRVAR(
    PYXXH32_hexdigest_doc,
    "hexdigest() -> string\n\n"
    "Like digest(), but returns the digest as a string of hexadecimal digits.");

static PyObject *PYXXH32_hexdigest(PYXXH32Object *self)
{
    PyObject *retval;
#if PY_MAJOR_VERSION >= 3
    Py_UNICODE *retbuf;
#else
    char *retbuf;
#endif
    unsigned int intdigest;
    char digest[XXH32_DIGESTSIZE + 1];
    int i, j;

#if PY_MAJOR_VERSION >= 3
    retval = PyUnicode_FromStringAndSize(NULL, XXH32_DIGESTSIZE * 2);
#else
    retval = PyString_FromStringAndSize(NULL, XXH32_DIGESTSIZE * 2);
#endif

    if (!retval) {
        return NULL;
    }

#if PY_MAJOR_VERSION >= 3
    retbuf = PyUnicode_AS_UNICODE(retval);
#else
    retbuf = PyString_AS_STRING(retval);
#endif

    if (!retbuf) {
        Py_DECREF(retval);
        return NULL;
    }

    intdigest = XXH32_digest(self->xxhash_state);
    u2bytes(intdigest, digest);

    for (i = j = 0; i < XXH32_DIGESTSIZE; i++) {
        unsigned char c;
        c = (digest[i] >> 4) & 0xf;
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
        c = (digest[i] & 0xf);
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
    }

    return retval;
}

PyDoc_STRVAR(
    PYXXH32_intdigest_doc,
    "intdigest() -> int\n\n"
    "Like digest(), but returns the digest as an integer, which is the integer\n"
    "returned by xxhash C API");

static PyObject *PYXXH32_intdigest(PYXXH32Object *self)
{
    unsigned int digest = XXH32_digest(self->xxhash_state);
    return Py_BuildValue("I", digest);
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
#if PY_MAJOR_VERSION >= 3
    return PyUnicode_FromStringAndSize("XXH32", 5);
#else
    return PyString_FromStringAndSize("XXH32", 5);
#endif
}

static PyObject *
PYXXH32_get_seed(PYXXH32Object *self, void *closure)
{
    return Py_BuildValue("I", self->seed);
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
#if PY_MAJOR_VERSION >= 3
    PyVarObject_HEAD_INIT(NULL, 0)
#else
    PyObject_HEAD_INIT(NULL)
    0,                             /* ob_size */
#endif
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
    Py_TPFLAGS_DEFAULT,            /* tp_flags */
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
};


/* XXH64 */

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    XXH64_state_t *xxhash_state;
    unsigned long long seed;
} PYXXH64Object;

static PyTypeObject PYXXH64Type;

static void PYXXH64_dealloc(PYXXH64Object *self)
{
    XXH64_freeState(self->xxhash_state);
    PyObject_Del(self);
}

static PyObject *PYXXH64_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PYXXH64Object *self;

    if ((self = PyObject_New(PYXXH64Object, &PYXXH64Type)) == NULL) {
        return NULL;
    }

    if ((self->xxhash_state = XXH64_createState()) == NULL) {
        return NULL;
    }

    return (PyObject *)self;
}

static int PYXXH64_init(PYXXH64Object *self, PyObject *args, PyObject *kwargs)
{
    unsigned long long seed = 0;
    char *keywords[] = {"input", "seed", NULL};
    const char *s = NULL;
    int ns;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|s#K:__init__", keywords, &s, &ns, &seed)) {
        return -1;
    }

    self->seed = seed;
    XXH64_reset(self->xxhash_state, seed);

    if (s) {
        XXH64_update(self->xxhash_state, s, ns);
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
    const char *s;
    int ns;

    if (!PyArg_ParseTuple(args, "s#:update", &s, &ns)) {
        return NULL;
    }

    XXH64_update(self->xxhash_state, s, ns);

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
    PyObject *retval;
    char *retbuf;
    unsigned long long digest;

#if PY_MAJOR_VERSION >= 3
    retval = PyBytes_FromStringAndSize(NULL, XXH64_DIGESTSIZE);
#else
    retval = PyString_FromStringAndSize(NULL, XXH64_DIGESTSIZE);
#endif

    if (!retval) {
        return NULL;
    }

#if PY_MAJOR_VERSION >= 3
    retbuf = PyBytes_AS_STRING(retval);
#else
    retbuf = PyString_AS_STRING(retval);
#endif

    if (!retbuf) {
        Py_DECREF(retval);
        return NULL;
    }

    digest = XXH64_digest(self->xxhash_state);
    ull2bytes(digest, retbuf);

    return retval;
}

PyDoc_STRVAR(
    PYXXH64_hexdigest_doc,
    "hexdigest() -> string\n\n"
    "Like digest(), but returns the digest as a string of hexadecimal digits.");

static PyObject *PYXXH64_hexdigest(PYXXH64Object *self)
{
    PyObject *retval;
#if PY_MAJOR_VERSION >= 3
    Py_UNICODE *retbuf;
#else
    char *retbuf;
#endif
    unsigned long long intdigest;
    char digest[XXH64_DIGESTSIZE + 1];
    int i, j;

#if PY_MAJOR_VERSION >= 3
    retval = PyUnicode_FromStringAndSize(NULL, XXH64_DIGESTSIZE * 2);
#else
    retval = PyString_FromStringAndSize(NULL, XXH64_DIGESTSIZE * 2);
#endif

    if (!retval) {
        return NULL;
    }

#if PY_MAJOR_VERSION >= 3
    retbuf = PyUnicode_AS_UNICODE(retval);
#else
    retbuf = PyString_AS_STRING(retval);
#endif

    if (!retbuf) {
        Py_DECREF(retval);
        return NULL;
    }

    intdigest = XXH64_digest(self->xxhash_state);
    ull2bytes(intdigest, digest);

    for (i = j = 0; i < XXH64_DIGESTSIZE; i++) {
        unsigned char c;
        c = (digest[i] >> 4) & 0xf;
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
        c = (digest[i] & 0xf);
        c = (c > 9) ? c + 'a' - 10 : c + '0';
        retbuf[j++] = c;
    }

    return retval;
}


PyDoc_STRVAR(
    PYXXH64_intdigest_doc,
    "intdigest() -> int\n\n"
    "Like digest(), but returns the digest as an integer, which is the integer\n"
    "returned by xxhash C API");

static PyObject *PYXXH64_intdigest(PYXXH64Object *self)
{
    unsigned long long digest = XXH64_digest(self->xxhash_state);
    return Py_BuildValue("K", digest);
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
#if PY_MAJOR_VERSION >= 3
    return PyUnicode_FromStringAndSize("XXH64", 5);
#else
    return PyString_FromStringAndSize("XXH64", 5);
#endif
}

static PyObject *
PYXXH64_get_seed(PYXXH64Object *self, void *closure)
{
    return Py_BuildValue("K", self->seed);
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
#if PY_MAJOR_VERSION >= 3
    PyVarObject_HEAD_INIT(NULL, 0)
#else
    PyObject_HEAD_INIT(NULL)
    0,                             /* ob_size */
#endif
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
    Py_TPFLAGS_DEFAULT,            /* tp_flags */
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
};


/*****************************************************************************
 * Module Init ****************************************************************
 ****************************************************************************/

/* ref: https://docs.python.org/2/howto/cporting.html */

struct module_state {
    PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

static PyMethodDef methods[] = {
    {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3

static int myextension_traverse(PyObject *m, visitproc visit, void *arg)
{
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int myextension_clear(PyObject *m)
{
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "xxhash",
    NULL,
    sizeof(struct module_state),
    methods,
    NULL,
    myextension_traverse,
    myextension_clear,
    NULL
};

#define INITERROR return NULL

PyObject *PyInit_xxhash(void)

#else
#define INITERROR return

void initxxhash(void)
#endif
{
    PyObject *module;
    struct module_state *st;

#if PY_MAJOR_VERSION >= 3
    module = PyModule_Create(&moduledef);
#else
    module = Py_InitModule("xxhash", methods);
#endif

    if (module == NULL) {
        INITERROR;
    }

    st = GETSTATE(module);

    st->error = PyErr_NewException("xxhash.Error", NULL, NULL);

    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

    if (PyType_Ready(&PYXXH32Type) < 0) {
        INITERROR;
    }

    Py_INCREF(&PYXXH32Type);
    PyModule_AddObject(module, "xxh32", (PyObject *)&PYXXH32Type);


    if (PyType_Ready(&PYXXH64Type) < 0) {
        INITERROR;
    }

    Py_INCREF(&PYXXH64Type);
    PyModule_AddObject(module, "xxh64", (PyObject *)&PYXXH64Type);

    PyModule_AddStringConstant(module, "VERSION", VALUE_TO_STRING(VERSION));
    PyModule_AddStringConstant(module, "XXHASH_VERSION", VALUE_TO_STRING(XXHASH_VERSION));

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}
