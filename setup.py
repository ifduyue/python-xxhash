import os
import re
import sysconfig
from pathlib import Path

from setuptools import Extension, setup

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

ext_modules = [
    Extension(
        "_xxhash",
        source,
        include_dirs=include_dirs,
        libraries=libraries,
        define_macros=define_macros,
    )
]

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
    package_data={"xxhash": ["py.typed", "**.pyi"]},
)
