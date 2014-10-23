/*
 * Copyright (c) 2014, Yue Du
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


#include <Python.h>

#include "xxhash/xxhash.h"

#define TOSTRING(x) #x
#define VALUE_TO_STRING(x) TOSTRING(x)

#ifndef Py_TYPE
#define Py_TYPE(ob) (((PyObject*)(ob))->ob_type)
#endif

/*****************************************************************************
 * Module Functions ***********************************************************
 ****************************************************************************/

static char *keywords[] = {"input", "seed", NULL};

static PyObject *xxh32(PyObject *self, PyObject *args, PyObject *kwargs)
{
    unsigned int seed = 0, digest = 0;
    const char *s;
    unsigned int ns;
    (void)self;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#|I:xxh32", keywords, &s, &ns, &seed)) {
        return NULL;
    }

    digest = XXH32(s, ns, seed);
    return Py_BuildValue("I", digest);
}

static PyObject *xxh64(PyObject *self, PyObject *args, PyObject *kwargs)
{
    unsigned long long seed = 0, digest = 0;
    const char *s;
    unsigned int ns;
    (void)self;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#|K:xxh64", keywords, &s, &ns, &seed)) {
        return NULL;
    }

    digest = XXH64(s, ns, seed);
    return Py_BuildValue("K", digest);
}

/*****************************************************************************
 * Module Types ***************************************************************
 ****************************************************************************/

/* XXH32 */

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    XXH32_state_t xxhash_state[1];
} PYXXH32Object;

static void PYXXH32_dealloc(PYXXH32Object *self)
{
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *PYXXH32_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PYXXH32Object *self;

    self = (PYXXH32Object *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int PYXXH32_init(PYXXH32Object *self, PyObject *args, PyObject *kwargs)
{
    unsigned int seed = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|I:__init__", &keywords[1], &seed)) {
        return -1;
    }

    XXH32_reset(self->xxhash_state, seed);

    return 0;
}

static PyObject *PYXXH32_update(PYXXH32Object *self, PyObject *args)
{
    const char *s;
    unsigned int ns;

    if (!PyArg_ParseTuple(args, "s#:update", &s, &ns)) {
        return NULL;
    }

    XXH32_update(self->xxhash_state, s, ns);

    Py_RETURN_NONE;
}

static PyObject *PYXXH32_digest(PYXXH32Object *self)
{
    unsigned int digest = XXH32_digest(self->xxhash_state);
    return Py_BuildValue("I", digest);
}

static PyMethodDef PYXXH32_methods[] = {
    {"update", (PyCFunction)PYXXH32_update, METH_VARARGS, "XXH32_update"},
    {"digest", (PyCFunction)PYXXH32_digest, METH_NOARGS, "XXH32_digest"},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject PYXXH32Type = {
#if PY_MAJOR_VERSION >= 3
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
#else
    PyObject_HEAD_INIT(NULL)
    0,                             /* ob_size */
#endif
    "xxhash.XXH32",                /* tp_name */
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
    "XXH32",                       /* tp_doc */
    0,                             /* tp_traverse */
    0,                             /* tp_clear */
    0,                             /* tp_richcompare */
    0,                             /* tp_weaklistoffset */
    0,                             /* tp_iter */
    0,                             /* tp_iternext */
    PYXXH32_methods,               /* tp_methods */
    0,                             /* tp_members */
    0,                             /* tp_getset */
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
    XXH64_state_t xxhash_state[1];
} PYXXH64Object;

static void PYXXH64_dealloc(PYXXH64Object *self)
{
    ((PyObject *)self)->ob_type->tp_free(self);
}

static PyObject *PYXXH64_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PYXXH64Object *self;

    self = (PYXXH64Object *)type->tp_alloc(type, 0);
    return (PyObject *)self;
}

static int PYXXH64_init(PYXXH64Object *self, PyObject *args, PyObject *kwargs)
{
    unsigned long long seed = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|K:__init__", &keywords[1], &seed)) {
        return -1;
    }

    XXH64_reset(self->xxhash_state, seed);

    return 0;
}

static PyObject *PYXXH64_update(PYXXH64Object *self, PyObject *args)
{
    const char *s;
    unsigned int ns;

    if (!PyArg_ParseTuple(args, "s#:update", &s, &ns)) {
        return NULL;
    }

    XXH64_update(self->xxhash_state, s, ns);

    Py_RETURN_NONE;
}

static PyObject *PYXXH64_digest(PYXXH64Object *self)
{
    unsigned long long digest = XXH64_digest(self->xxhash_state);
    return Py_BuildValue("K", digest);
}

static PyMethodDef PYXXH64_methods[] = {
    {"update", (PyCFunction)PYXXH64_update, METH_VARARGS, "XXH64_update"},
    {"digest", (PyCFunction)PYXXH64_digest, METH_NOARGS, "XXH64_digest"},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject PYXXH64Type = {
#if PY_MAJOR_VERSION >= 3
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
#else
    PyObject_HEAD_INIT(NULL)
    0,                             /* ob_size */
#endif
    "xxhash.XXH64",                /* tp_name */
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
    "XXH64",                       /* tp_doc */
    0,                             /* tp_traverse */
    0,                             /* tp_clear */
    0,                             /* tp_richcompare */
    0,                             /* tp_weaklistoffset */
    0,                             /* tp_iter */
    0,                             /* tp_iternext */
    PYXXH64_methods,               /* tp_methods */
    0,                             /* tp_members */
    0,                             /* tp_getset */
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
    {"xxh32", (PyCFunction)xxh32, METH_VARARGS | METH_KEYWORDS, "XXH32"},
    {"xxh64", (PyCFunction)xxh64, METH_VARARGS | METH_KEYWORDS, "XXH64"},
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

    PYXXH32Type.tp_new = PyType_GenericNew;

    if (PyType_Ready(&PYXXH32Type) < 0) {
        INITERROR;
    }

    Py_INCREF(&PYXXH32Type);
    PyModule_AddObject(module, "XXH32", (PyObject *)&PYXXH32Type);


    PYXXH64Type.tp_new = PyType_GenericNew;

    if (PyType_Ready(&PYXXH64Type) < 0) {
        INITERROR;
    }

    Py_INCREF(&PYXXH64Type);
    PyModule_AddObject(module, "XXH64", (PyObject *)&PYXXH64Type);

    PyModule_AddStringConstant(module, "VERSION", VALUE_TO_STRING(VERSION));
    PyModule_AddStringConstant(module, "XXHASH_VERSION", VALUE_TO_STRING(XXHASH_VERSION));

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}
