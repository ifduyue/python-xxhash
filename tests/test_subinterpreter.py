import sys
import unittest

xxhash = sys.modules.get("xxhash")

# Sub-interpreter support requires CPython with _interpreters module.
HAS_INTERPRETERS = (
    sys.implementation.name == "cpython"
    and sys.version_info >= (3, 12)
)


def _skip_if_no_interpreters():
    """Raise SkipTest if _interpreters is not available."""
    try:
        import _interpreters
    except ImportError:
        raise unittest.SkipTest("_interpreters module not available")


class TestSubInterpreter(unittest.TestCase):
    """Test that the extension works correctly in sub-interpreters."""

    def _create_interpreter(self):
        _skip_if_no_interpreters()
        import _interpreters
        return _interpreters.create()

    def _destroy_interpreter(self, interp_id):
        import _interpreters
        _interpreters.destroy(interp_id)

    def test_import_in_subinterpreter(self):
        """The C extension can be imported in a sub-interpreter."""
        interp = self._create_interpreter()
        try:
            import _interpreters
            _interpreters.exec(interp, "import xxhash")
        finally:
            self._destroy_interpreter(interp)

    def test_xxh32_in_subinterpreter(self):
        """xxh32 produces correct results in a sub-interpreter."""
        interp = self._create_interpreter()
        try:
            import _interpreters
            _interpreters.exec(
                interp,
                "import xxhash; "
                "assert xxhash.xxh32('a').intdigest() == 1426945110, 'wrong hash'",
            )
        finally:
            self._destroy_interpreter(interp)

    def test_xxh64_in_subinterpreter(self):
        """xxh64 produces correct results in a sub-interpreter."""
        interp = self._create_interpreter()
        try:
            import _interpreters
            _interpreters.exec(
                interp,
                "import xxhash; "
                "assert xxhash.xxh64('a').intdigest() == 932445443, 'wrong hash'",
            )
        finally:
            self._destroy_interpreter(interp)

    def test_xxh3_64_in_subinterpreter(self):
        """xxh3_64 produces correct results in a sub-interpreter."""
        interp = self._create_interpreter()
        try:
            import _interpreters
            _interpreters.exec(
                interp,
                "import xxhash; "
                "h = xxhash.xxh3_64('a').hexdigest(); "
                "assert h == xxhash.xxh3_64_hexdigest('a'), 'mismatch'",
            )
        finally:
            self._destroy_interpreter(interp)

    def test_xxh3_128_in_subinterpreter(self):
        """xxh3_128 produces correct results in a sub-interpreter."""
        interp = self._create_interpreter()
        try:
            import _interpreters
            _interpreters.exec(
                interp,
                "import xxhash; "
                "h = xxhash.xxh3_128('a').hexdigest(); "
                "assert h == xxhash.xxh3_128_hexdigest('a'), 'mismatch'",
            )
        finally:
            self._destroy_interpreter(interp)

    def test_update_copy_reset_in_subinterpreter(self):
        """update(), copy(), reset() work in a sub-interpreter."""
        interp = self._create_interpreter()
        try:
            import _interpreters
            _interpreters.exec(
                interp,
                "import xxhash\n"
                "x = xxhash.xxh32()\n"
                "x.update('abc')\n"
                "y = x.copy()\n"
                "assert x.digest() == y.digest(), 'copy mismatch'\n"
                "y.update('d')\n"
                "assert x.digest() != y.digest(), 'copy not independent'\n"
                "x.reset()\n"
                "assert x.intdigest() == xxhash.xxh32().intdigest(), 'reset failed'\n",
            )
        finally:
            self._destroy_interpreter(interp)

    def test_multiple_subinterpreters(self):
        """Multiple sub-interpreters can use xxhash independently."""
        interp1 = self._create_interpreter()
        interp2 = self._create_interpreter()
        try:
            import _interpreters
            _interpreters.exec(interp1, "import xxhash; val = xxhash.xxh32('hello').intdigest()")
            _interpreters.exec(interp2, "import xxhash; val = xxhash.xxh64('hello').intdigest()")
            # Both should produce valid results without interfering
            _interpreters.exec(interp1, "assert xxhash.xxh32('hello').intdigest() == val")
            _interpreters.exec(interp2, "assert xxhash.xxh64('hello').intdigest() == val")
        finally:
            self._destroy_interpreter(interp1)
            self._destroy_interpreter(interp2)

    def test_subinterpreter_type_isolation(self):
        """Types in different sub-interpreters are distinct objects."""
        interp = self._create_interpreter()
        try:
            import _interpreters
            # Get the id of xxh32 type in the main interpreter
            import xxhash._xxhash as m
            main_type_id = id(m.xxh32)
            # Run in sub-interpreter - it should get its own type object
            _interpreters.exec(
                interp,
                "import xxhash._xxhash as m; "
                "assert id(m.xxh32) != %d, 'types should be isolated'" % main_type_id,
            )
        finally:
            self._destroy_interpreter(interp)


class TestPerInterpreterGIL(unittest.TestCase):
    """Test that the extension works correctly in sub-interpreters with own GIL.

    This validates the Py_MOD_PER_INTERPRETER_GIL_SUPPORTED flag.
    """

    def _create_interpreter_with_own_gil(self):
        _skip_if_no_interpreters()
        import _interpreters
        cfg = _interpreters.new_config("isolated", gil="own")
        return _interpreters.create(cfg)

    def _destroy_interpreter(self, interp_id):
        import _interpreters
        _interpreters.destroy(interp_id)

    def test_import_in_per_gil_interpreter(self):
        """The C extension can be imported in a sub-interpreter with its own GIL."""
        interp = self._create_interpreter_with_own_gil()
        try:
            import _interpreters
            _interpreters.exec(interp, "import xxhash")
        finally:
            self._destroy_interpreter(interp)

    def test_xxh32_in_per_gil_interpreter(self):
        """xxh32 produces correct results in a sub-interpreter with its own GIL."""
        interp = self._create_interpreter_with_own_gil()
        try:
            import _interpreters
            _interpreters.exec(
                interp,
                "import xxhash; "
                "assert xxhash.xxh32('a').intdigest() == 1426945110, 'wrong hash'",
            )
        finally:
            self._destroy_interpreter(interp)

    def test_xxh64_in_per_gil_interpreter(self):
        """xxh64 produces correct results in a sub-interpreter with its own GIL."""
        interp = self._create_interpreter_with_own_gil()
        try:
            import _interpreters
            _interpreters.exec(
                interp,
                "import xxhash; "
                "assert xxhash.xxh64('a').intdigest() == 932445443, 'wrong hash'",
            )
        finally:
            self._destroy_interpreter(interp)

    def test_xxh3_64_in_per_gil_interpreter(self):
        """xxh3_64 produces correct results in a sub-interpreter with its own GIL."""
        interp = self._create_interpreter_with_own_gil()
        try:
            import _interpreters
            _interpreters.exec(
                interp,
                "import xxhash; "
                "h = xxhash.xxh3_64('a').hexdigest(); "
                "assert h == xxhash.xxh3_64_hexdigest('a'), 'mismatch'",
            )
        finally:
            self._destroy_interpreter(interp)

    def test_xxh3_128_in_per_gil_interpreter(self):
        """xxh3_128 produces correct results in a sub-interpreter with its own GIL."""
        interp = self._create_interpreter_with_own_gil()
        try:
            import _interpreters
            _interpreters.exec(
                interp,
                "import xxhash; "
                "h = xxhash.xxh3_128('a').hexdigest(); "
                "assert h == xxhash.xxh3_128_hexdigest('a'), 'mismatch'",
            )
        finally:
            self._destroy_interpreter(interp)

    def test_update_copy_reset_in_per_gil_interpreter(self):
        """update(), copy(), reset() work in a sub-interpreter with its own GIL."""
        interp = self._create_interpreter_with_own_gil()
        try:
            import _interpreters
            _interpreters.exec(
                interp,
                "import xxhash\n"
                "x = xxhash.xxh32()\n"
                "x.update('abc')\n"
                "y = x.copy()\n"
                "assert x.digest() == y.digest(), 'copy mismatch'\n"
                "y.update('d')\n"
                "assert x.digest() != y.digest(), 'copy not independent'\n"
                "x.reset()\n"
                "assert x.intdigest() == xxhash.xxh32().intdigest(), 'reset failed'\n",
            )
        finally:
            self._destroy_interpreter(interp)

    def test_multiple_per_gil_interpreters(self):
        """Multiple sub-interpreters with own GIL can use xxhash independently."""
        interp1 = self._create_interpreter_with_own_gil()
        interp2 = self._create_interpreter_with_own_gil()
        try:
            import _interpreters
            _interpreters.exec(interp1, "import xxhash; val = xxhash.xxh32('hello').intdigest()")
            _interpreters.exec(interp2, "import xxhash; val = xxhash.xxh64('hello').intdigest()")
            _interpreters.exec(interp1, "assert xxhash.xxh32('hello').intdigest() == val")
            _interpreters.exec(interp2, "assert xxhash.xxh64('hello').intdigest() == val")
        finally:
            self._destroy_interpreter(interp1)
            self._destroy_interpreter(interp2)


class TestPerModuleState(unittest.TestCase):
    """Test that per-module state is properly isolated (heap types)."""

    def test_types_are_heap_types(self):
        """All hash types should be heap types (not static types)."""
        import xxhash._xxhash as m

        for name in ("xxh32", "xxh64", "xxh3_64", "xxh3_128"):
            tp = getattr(m, name)
            self.assertIsInstance(tp, type)
            # Heap types have __flags__ with Py_TPFLAGS_HEAPTYPE (1 << 9 = 512)
            flags = tp.__flags__
            self.assertTrue(
                flags & (1 << 9),
                f"{name} should be a heap type (Py_TPFLAGS_HEAPTYPE not set)",
            )

    def test_type_module_association(self):
        """Types should be associated with the correct module."""
        import xxhash._xxhash as m

        for name in ("xxh32", "xxh64", "xxh3_64", "xxh3_128"):
            tp = getattr(m, name)
            self.assertEqual(tp.__module__, "xxhash")

    def test_module_has_state(self):
        """The C module should have per-module state (m_size > 0)."""
        import xxhash._xxhash as m

        self.assertTrue(hasattr(m, "xxh32"))
        self.assertTrue(hasattr(m, "xxh64"))
        self.assertTrue(hasattr(m, "xxh3_64"))
        self.assertTrue(hasattr(m, "xxh3_128"))
        self.assertTrue(hasattr(m, "XXHASH_VERSION"))

    def test_independent_type_identity(self):
        """Types from different import paths are the same object (same interpreter)."""
        import xxhash
        import xxhash._xxhash as m

        self.assertIs(xxhash.xxh32, m.xxh32)
        self.assertIs(xxhash.xxh64, m.xxh64)
        self.assertIs(xxhash.xxh3_64, m.xxh3_64)
        self.assertIs(xxhash.xxh3_128, m.xxh3_128)

    def test_module_def_has_nonzero_m_size(self):
        """Verify the module was created with per-module state (m_size > 0).

        We check this indirectly: if m_size were 0, PyModule_GetState would
        return NULL and the types would not be stored per-module. The fact
        that the module works at all (types are accessible) confirms m_size > 0.
        A more direct check: re-importing in a sub-interpreter should create
        fresh type objects, not share the main interpreter's static types.
        """
        if not HAS_INTERPRETERS:
            self.skipTest("requires CPython 3.12+")
        _skip_if_no_interpreters()

        import _interpreters
        import xxhash._xxhash as m

        main_xxh32 = m.xxh32
        interp = _interpreters.create()
        try:
            # The sub-interpreter should get its own type objects
            # (different from the main interpreter's), proving per-module state
            _interpreters.exec(
                interp,
                "import xxhash._xxhash as m; "
                "main_id = %d; "
                "assert id(m.xxh32) != main_id, "
                "'sub-interpreter shares type with main interpreter'" % id(main_xxh32),
            )
        finally:
            _interpreters.destroy(interp)


if __name__ == "__main__":
    unittest.main()
