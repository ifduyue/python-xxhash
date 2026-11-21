import os
import re
import sysconfig
import threading
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext as _build_ext

# Must cover the whole build_extension (compile + link), not just the
# build_temp swap. ``build_ext -j`` shares one command instance; a
# narrower lock would still let two variants mix object files.
_build_temp_lock = threading.Lock()

# xxh_x86dispatch.c only builds for x86, and only with baseline flags.
# -mavx*, -march=native, or /arch:AVX* would make the wheel require that ISA.
_X86_ARCH = re.compile(
    r"(?:^|[^a-z0-9])(?:x86_64|amd64|i[3-6]86|x86)(?:[^a-z0-9]|$)"
)


def _target_is_x86():
    plat = sysconfig.get_platform().lower()
    # 32-bit Windows reports "win32" and does not name the arch.
    if plat == "win32":
        return True
    return _X86_ARCH.search(plat) is not None


if os.getenv("XXHASH_LINK_SO"):
    # A system libxxhash does not export the XXH3_*_dispatch symbols.
    libraries = ["xxhash"]
    source = ["src/_xxhash.c"]
    include_dirs = []
    define_macros = []
else:
    libraries = []
    source = ["src/_xxhash.c", "deps/xxhash/xxhash.c"]
    include_dirs = ["deps/xxhash"]
    define_macros = []
    if _target_is_x86():
        source.append("deps/xxhash/xxh_x86dispatch.c")
        define_macros.append(("XXHASH_X86_DISPATCH", "1"))

# The default ``xxhash._xxhash`` extension is built with per-object locks.
# ``xxhash._xxhash_nolock`` (public ``xxhash.nolock``) is compiled from the
# same source with locking disabled, for callers that exclusively own each
# streaming hash object.

_ext_kwargs = {
    "sources": source,
    "include_dirs": include_dirs,
    "libraries": libraries,
}

ext_modules = [
    Extension(
        "_xxhash",
        define_macros=define_macros + [
            ("XXHASH_WITH_LOCK", "1"),
        ],
        **_ext_kwargs,
    ),
    Extension(
        "_xxhash_nolock",
        define_macros=define_macros + [
            ("XXHASH_WITH_LOCK", "0"),
            ("XXHASH_MODULE_NAME", "_xxhash_nolock"),
            ("XXHASH_TP_NAME_PREFIX", "xxhash.nolock"),
        ],
        **_ext_kwargs,
    ),
]


class build_ext(_build_ext):
    """Build each extension in its own temp directory.

    Both extensions are compiled from ``src/_xxhash.c`` with different
    macros; a shared temp dir would let one variant link the other's objects.
    """

    def build_extension(self, ext):
        with _build_temp_lock:
            old_build_temp = self.build_temp
            self.build_temp = os.path.join(old_build_temp, ext.name)
            try:
                super().build_extension(ext)
            finally:
                self.build_temp = old_build_temp


d = Path(__file__).parent
long_description = d.joinpath("README.rst").read_text() + "\n" + d.joinpath("CHANGELOG.rst").read_text()

version_dict = {}
exec(d.joinpath("xxhash", "version.py").read_text(), {}, version_dict)
version = version_dict["VERSION"]

setup(
    name="xxhash",
    version=version,
    description="Python binding for xxHash",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Yue Du",
    author_email="ifduyue@gmail.com",
    url="https://github.com/ifduyue/python-xxhash",
    license="BSD-2-Clause",
    license_files=["LICENSE"],
    packages=["xxhash"],
    ext_package="xxhash",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Free Threading :: 1 - Unstable",
    ],
    python_requires=">=3.9",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    package_data={"xxhash": ["py.typed", "**.pyi"]},
)
