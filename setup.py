import os
import sysconfig
from pathlib import Path

from setuptools import Extension, setup

if os.getenv("XXHASH_LINK_SO"):
    libraries = ["xxhash"]
    source = ["src/_xxhash.c"]
    include_dirs = []
else:
    libraries = []
    source = ["src/_xxhash.c", "deps/xxhash/xxhash.c"]
    include_dirs = ["deps/xxhash"]

# In free-threading builds the default module must be thread-safe, because
# there is no GIL protecting the internal xxHash state.  On regular GIL
# builds the default module is unlocked for maximum performance; users who
# need to share a streaming hash object across threads can use
# xxhash.threadsafe.
_is_free_threading = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))

_ext_kwargs = {
    "sources": source,
    "include_dirs": include_dirs,
    "libraries": libraries,
}

ext_modules = [
    Extension(
        "_xxhash",
        define_macros=[("XXHASH_WITH_LOCK", "1")] if _is_free_threading else [],
        **_ext_kwargs,
    ),
    Extension(
        "_xxhash_threadsafe",
        define_macros=[("XXHASH_WITH_LOCK", "1")],
        **_ext_kwargs,
    ),
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
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Free Threading :: 1 - Unstable",
    ],
    python_requires=">=3.9",
    ext_modules=ext_modules,
    package_data={"xxhash": ["py.typed", "**.pyi"]},
)
