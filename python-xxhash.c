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
#include <stdlib.h>

#include "xxhash/xxhash.h"

static char *keywords[] = {"input", "seed", NULL};

static PyObject *xxh32(PyObject *self, PyObject *args, PyObject *kwargs)
{
    unsigned int seed = 0, digest = 0;
    const char *s;
    unsigned int ns;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#|I", keywords, &s, &ns, &seed)) {
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

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#|K", keywords, &s, &ns, &seed)) {
        return NULL;
    }

    digest = XXH64(s, ns, seed);
    return Py_BuildValue("K", digest);
}

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

PyObject *
PyInit_xxhash(void)

#else
#define INITERROR return

void
initxxhash(void)
#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule("xxhash", methods);
#endif

    if (module == NULL) {
        INITERROR;
    }

    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("xxhash.Error", NULL, NULL);

    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

    PyModule_AddStringConstant(module, "VERSION", VERSION);
    PyModule_AddStringConstant(module, "XXHASH_VERSION", XXHASH_VERSION);

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}
