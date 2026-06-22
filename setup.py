import os
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext as _build_ext

if os.getenv("XXHASH_LINK_SO"):
    libraries = ["xxhash"]
    source = ["src/_xxhash.c"]
    include_dirs = []
else:
    libraries = []
    source = ["src/_xxhash.c", "deps/xxhash/xxhash.c"]
    include_dirs = ["deps/xxhash"]

# The default ``xxhash._xxhash`` extension is built without per-object locks
# for maximum performance.  Users who need to share a streaming hash object
# across threads can use ``xxhash._xxhash_threadsafe`` (exposed as the public
# ``xxhash.threadsafe`` submodule), which is compiled from the same source
# with locking enabled.

_ext_kwargs = {
    "sources": source,
    "include_dirs": include_dirs,
    "libraries": libraries,
}

ext_modules = [
    Extension(
        "_xxhash",
        **_ext_kwargs,
    ),
    Extension(
        "_xxhash_threadsafe",
        define_macros=[
            ("XXHASH_WITH_LOCK", "1"),
            ("XXHASH_MODULE_NAME", "_xxhash_threadsafe"),
            ("XXHASH_TP_NAME_PREFIX", "xxhash.threadsafe"),
        ],
        **_ext_kwargs,
    ),
]


class build_ext(_build_ext):
    """Build each extension in its own temp directory.

    Both extensions are built from the same ``src/_xxhash.c`` source file.
    Without separate temp directories their object files would overwrite
    each other, causing one variant to be linked with the wrong macros.

    ``try/finally`` restores ``self.build_temp`` so that incremental builds
    (where ``build_ext`` may be reused) still work correctly.
    """

    def build_extension(self, ext):
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
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Free Threading :: 1 - Unstable",
    ],
    python_requires=">=3.9",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    package_data={"xxhash": ["py.typed", "**.pyi"]},
)
