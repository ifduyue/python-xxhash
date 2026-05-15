"""Validate the .pyi type stubs using pyright."""

import subprocess
import tempfile
import unittest
from pathlib import Path


class TestStubsPyright(unittest.TestCase):
    def _run_pyright(self, source: str) -> subprocess.CompletedProcess:
        """Run pyright on a temporary file with the given source.

        The file is placed under the repo root so pyright can discover the
        xxhash package and its .pyi stubs via pyproject.toml.
        """
        repo_root = Path(__file__).resolve().parent.parent
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            prefix="__pyright_check_",
            dir=repo_root,
            delete=False,
        ) as f:
            f.write(source)
            tmp_path = f.name

        try:
            return subprocess.run(
                ["pyright", "--project", str(repo_root), tmp_path],
                capture_output=True,
                text=True,
                cwd=repo_root,
                timeout=30,
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_valid_buffer_types(self):
        """Valid buffer types should type-check without errors."""
        code = """\
import xxhash

h1 = xxhash.xxh32(b"hello")
h1.update(b"world")
xxhash.xxh32_digest(b"hello")

h2 = xxhash.xxh32(bytearray(b"hello"))
h2.update(bytearray(b"world"))

h3 = xxhash.xxh32(memoryview(b"hello"))
h3.update(memoryview(b"world"))

h4 = xxhash.xxh32()
h4.update(b"test")
"""
        result = self._run_pyright(code)
        if result.returncode != 0:
            self.fail(
                f"pyright reported errors for valid buffer types:\n"
                f"{result.stdout}\n{result.stderr}"
            )

    def test_str_is_rejected(self):
        """str should be rejected (not a buffer type)."""
        code = """\
import xxhash
xxhash.xxh32("hello")
"""
        result = self._run_pyright(code)
        if result.returncode == 0:
            self.fail("pyright did not reject str argument")

    def test_int_is_rejected(self):
        """int should be rejected (not a buffer type)."""
        code = """\
import xxhash
xxhash.xxh32(42)
"""
        result = self._run_pyright(code)
        if result.returncode == 0:
            self.fail("pyright did not reject int argument")
