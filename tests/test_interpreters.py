"""
Tests for subinterpreter support (PEP 684 / PEP 489 / PEP 689).

xxhash declares Py_MOD_PER_INTERPRETER_GIL_SUPPORTED (3.12+) and
Py_MOD_GIL_NOT_USED (3.13t+), so these tests verify that the module
can be loaded and used safely inside sub-interpreters.
"""

import os
import unittest


# ── helpers ─────────────────────────────────────────────────────────────

def _get_interp_module():
    """Return the available subinterpreter module, or None."""
    for name in ('_interpreters', '_xxsubinterpreters'):
        try:
            mod = __import__(name)
            if hasattr(mod, 'create'):
                return mod
        except ImportError:
            continue
    return None


_interp_mod = _get_interp_module()

requires_interpreters = unittest.skipUnless(
    _interp_mod is not None,
    "subinterpreter API not available in this Python build",
)


def _subinterp_code(code):
    """Wrap code with preamble so xxhash can be imported in a subinterpreter."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parent.parent
    return 'import sys; sys.path.insert(0, %r); ' % str(root) + code


# ── test base class ─────────────────────────────────────────────────────

@requires_interpreters
class _SubinterpreterTestCase(unittest.TestCase):
    """Creates/destroys a subinterpreter per test.  Call self._run(code)
    to execute Python code in it with the path preamble."""

    def setUp(self):
        self.iid = _interp_mod.create()

    def tearDown(self):
        _interp_mod.destroy(self.iid)

    def _run(self, code):
        _interp_mod.run_string(self.iid, _subinterp_code(code))

    def _run_in(self, iid, code):
        _interp_mod.run_string(iid, _subinterp_code(code))


# ── basic functionality ─────────────────────────────────────────────────

HASH_TYPES = ["xxh32", "xxh64", "xxh3_64", "xxh3_128"]


class TestSubinterpreterBasic(_SubinterpreterTestCase):

    def test_import(self):
        self._run("import xxhash")

    def test_version_exists(self):
        self._run("""\
import xxhash
assert isinstance(xxhash.VERSION, str)
assert isinstance(xxhash.XXHASH_VERSION, str)
""")

    def _test_type_oneshot(self, typename):
        self._run("""\
import xxhash, os
data = os.urandom(64)
d = xxhash.%s_digest(data)
assert isinstance(d, bytes)
assert len(d) > 0
""" % typename)

    def test_xxh32_oneshot(self):
        self._test_type_oneshot("xxh32")

    def test_xxh64_oneshot(self):
        self._test_type_oneshot("xxh64")

    def test_xxh3_64_oneshot(self):
        self._test_type_oneshot("xxh3_64")

    def test_xxh3_128_oneshot(self):
        self._test_type_oneshot("xxh3_128")

    def _test_type_stream(self, typename):
        self._run("""\
import xxhash
h = xxhash.%s(b'hello', seed=42)
h.update(b' world')
d = h.digest()
hd = h.hexdigest()
id = h.intdigest()
assert isinstance(d, bytes)
assert isinstance(hd, str)
assert isinstance(id, int)
assert hd == d.hex()
""" % typename)

    def test_xxh32_stream(self):
        self._test_type_stream("xxh32")

    def test_xxh64_stream(self):
        self._test_type_stream("xxh64")

    def test_xxh3_64_stream(self):
        self._test_type_stream("xxh3_64")

    def test_xxh3_128_stream(self):
        self._test_type_stream("xxh3_128")

    def test_copy(self):
        self._run("""\
import xxhash
h = xxhash.xxh64(b'data', seed=12345)
c = h.copy()
h.update(b' more')
c.update(b' different')
assert h.digest() != c.digest()
""")

    def test_reset(self):
        self._run("""\
import xxhash
h = xxhash.xxh64(b'data', seed=42)
d1 = h.digest()
h.reset()
h.update(b'data')
d2 = h.digest()
assert d1 == d2
""")

    def test_xxh128_alias(self):
        self._run("""\
import xxhash
assert xxhash.xxh128 is xxhash.xxh3_128
assert xxhash.xxh128_digest is xxhash.xxh3_128_digest
""")


# ── isolation ───────────────────────────────────────────────────────────

class TestSubinterpreterIsolation(_SubinterpreterTestCase):

    def test_immutable_type(self):
        """The single xxhash type is immutable inside subinterpreters (3.12+).
        The constructors (xxh32, xxh64, xxh3_64, xxh3_128) are functions,
        not types, so we get the type from a constructed instance."""
        self._run("""\
import sys, xxhash
t = type(xxhash.xxh32())
if sys.version_info >= (3, 12):
    try:
        t.newattr = 42
        raise AssertionError('type should be immutable')
    except TypeError:
        pass
    assert t.__flags__ & (1 << 8), 'immutable flag not set'
""")

    def test_module_dict_not_shared(self):
        """Modifying a module attribute in one interpreter is invisible
        in another."""
        id_a = _interp_mod.create()
        id_b = _interp_mod.create()
        self._run_in(id_a, "import xxhash; xxhash._test_marker = 'a'")
        self._run_in(id_b, "import xxhash; assert not hasattr(xxhash, '_test_marker')")
        _interp_mod.destroy(id_a)
        _interp_mod.destroy(id_b)

    def test_independent_hashers(self):
        """Two interpreters each create their own hasher with independent state."""
        id_a = _interp_mod.create()
        id_b = _interp_mod.create()

        self._run_in(id_a, """\
import xxhash
h = xxhash.xxh64(b'data from A', seed=1)
assert h.hexdigest() == '42d0c0db68d72d07'
""")
        self._run_in(id_b, """\
import xxhash
h = xxhash.xxh64(b'data from B', seed=2)
assert h.hexdigest() == 'ada244d1f6adc3b1'
""")

        _interp_mod.destroy(id_a)
        _interp_mod.destroy(id_b)

    def test_algorithms_available(self):
        self._run("""\
import xxhash
assert 'xxh32' in xxhash.algorithms_available
assert 'xxh64' in xxhash.algorithms_available
assert 'xxh3_64' in xxhash.algorithms_available
assert 'xxh3_128' in xxhash.algorithms_available
""")


# ── many interpreters ───────────────────────────────────────────────────

class TestManyInterpreters(_SubinterpreterTestCase):

    def _test_type_in_eight(self, typename):
        ids = [_interp_mod.create() for _ in range(8)]
        for iid in ids:
            self._run_in(iid, """\
import os, xxhash
seed = int.from_bytes(os.urandom(4), 'big')
h = xxhash.%s(seed=seed)
for _ in range(32):
    h.update(os.urandom(128))
    _ = h.digest()
    _ = h.hexdigest()
    _ = h.intdigest()
""" % typename)
        for iid in ids:
            _interp_mod.destroy(iid)

    def test_xxh32_in_eight(self):
        self._test_type_in_eight("xxh32")

    def test_xxh64_in_eight(self):
        self._test_type_in_eight("xxh64")

    def test_xxh3_64_in_eight(self):
        self._test_type_in_eight("xxh3_64")

    def test_xxh3_128_in_eight(self):
        self._test_type_in_eight("xxh3_128")


# ── rapid create / destroy ─────────────────────────────────────────────

class TestSubinterpreterTeardown(_SubinterpreterTestCase):

    def test_destroy_after_use(self):
        iid = _interp_mod.create()
        _interp_mod.run_string(iid, _subinterp_code(
            "import xxhash; xxhash.xxh64(b'x').digest()"))
        _interp_mod.destroy(iid)

    def test_rapid_create_destroy(self):
        for _ in range(8):
            iid = _interp_mod.create()
            _interp_mod.run_string(iid, _subinterp_code("""\
import xxhash
h = xxhash.xxh64(seed=42)
for i in range(16):
    h.update(bytes([i] * 64))
    _ = h.digest()
    _ = h.copy().digest()
"""))
            _interp_mod.destroy(iid)


# ── concurrent.interpreters (Python 3.14+) ──────────────────────────────

def _has_concurrent_interpreters():
    try:
        import concurrent.interpreters
        return True
    except ImportError:
        return False


requires_concurrent = unittest.skipUnless(
    _has_concurrent_interpreters(),
    "concurrent.interpreters not available (requires Python 3.14+)",
)


@requires_concurrent
class TestConcurrentInterpreters(unittest.TestCase):
    """Tests using concurrent.interpreters (Python 3.14+)."""

    @staticmethod
    def _preamble():
        import pathlib
        root = pathlib.Path(__file__).resolve().parent.parent
        return 'import sys; sys.path.insert(0, %r); ' % str(root)

    def test_exec_xxh64(self):
        import concurrent.interpreters as ci
        interp = ci.create()
        interp.exec(self._preamble() + """\
import xxhash
h = xxhash.xxh64(b'Hello from concurrent.interpreters!', seed=42)
assert h.hexdigest() == 'b4da5436af54a52b'
""")
        interp.close()

    def test_exec_stream(self):
        import concurrent.interpreters as ci
        interp = ci.create()
        interp.exec(self._preamble() + """\
import xxhash
h = xxhash.xxh3_128(seed=123)
h.update(b'stream of data')
h.update(b'across interpreters')
d = h.digest()
assert len(d) == 16
""")
        interp.close()

    def test_queue_cross_interpreter(self):
        """Hash in interpreter A, pass digest via Queue,
        verify in interpreter B."""
        import concurrent.interpreters as ci

        q = ci.create_queue()
        pre = self._preamble()

        a = ci.create()
        b = ci.create()
        a.prepare_main({'q': q})
        b.prepare_main({'q': q})

        # Interpreter A: hash and put digest on queue
        a.exec(pre + '''\
import xxhash
h = xxhash.xxh64(b"cross-interpreter data", seed=99)
q.put(h.hexdigest())
''')

        # Interpreter B: read from queue and verify
        b.exec(pre + '''\
import xxhash
expected = q.get()
actual = xxhash.xxh64_hexdigest(b"cross-interpreter data", seed=99)
assert actual == expected, f"mismatch: {actual} != {expected}"
''')

        a.close()
        b.close()

    def test_immutable_type(self):
        import concurrent.interpreters as ci
        interp = ci.create()
        interp.exec(self._preamble() + """\
import sys, xxhash
t = type(xxhash.xxh32())
if sys.version_info >= (3, 12):
    assert t.__flags__ & (1 << 8), 'immutable flag not set'
    try:
        t.newattr = 42
        raise AssertionError('type should be immutable')
    except TypeError:
        pass
""")
        interp.close()

    def test_close_after_use(self):
        """Verify interpreter can be closed cleanly after using xxhash."""
        import concurrent.interpreters as ci
        for _ in range(8):
            interp = ci.create()
            interp.exec(self._preamble() + """\
import xxhash
h = xxhash.xxh64(seed=42)
for i in range(8):
    h.update(bytes([i] * 128))
    _ = h.digest()
""")
            interp.close()


if __name__ == '__main__':
    unittest.main()
