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

static PyMethodDef methods[] = {
    {"xxh32", (PyCFunction)xxh32, METH_VARARGS | METH_KEYWORDS, "XXH32"},
    {"xxh64", (PyCFunction)xxh64, METH_VARARGS | METH_KEYWORDS, "XXH64"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initxxhash(void)
{
    PyObject *module = Py_InitModule("xxhash", methods);

    PyModule_AddStringConstant(module, "VERSION", VERSION);
    PyModule_AddStringConstant(module, "XXHASH_VERSION", XXHASH_VERSION);
}
