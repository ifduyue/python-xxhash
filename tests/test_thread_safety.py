"""
Thread-safety tests for xxhash.threadsafe.

The default ``xxhash`` module is optimized for speed and does not protect
streaming hash objects with a per-object lock.  Concurrent access to the same
hash object from multiple threads is only safe when using the
``xxhash.threadsafe`` submodule, which adds a per-object lock around every
operation that touches the internal xxHash state.

The tests below verify that:
  * no crashes occur under concurrent access to ``threadsafe`` hash objects
  * hash results are deterministic (no data races)
"""

import os
import sys
import subprocess
import signal
import unittest
from xxhash import threadsafe as xxhash


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_in_subprocess(code: str, timeout: float = 60.0):
    """Run *code* in a subprocess and return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        # Return a sentinel that tells the caller the subprocess hung.
        return -999, "", "TIMEOUT (possible deadlock)"


# ---------------------------------------------------------------------------
# Scenario: concurrent digest() during update()
# ---------------------------------------------------------------------------

CONCURRENT_DIGEST_CODE = r"""
import sys, threading; from xxhash import threadsafe as xxhash

h = xxhash.xxh32()
BLOCK = b'x' * (4 * 1024 * 1024)          # 4 MiB
N = 50
barrier = threading.Barrier(4)
errors = []

def updater():
    barrier.wait()
    for _ in range(N):
        h.update(BLOCK)

def digester():
    barrier.wait()
    for _ in range(N * 5):
        try:
            _ = h.digest()
        except Exception as e:
            errors.append(e)

t1 = threading.Thread(target=updater)
t2 = threading.Thread(target=digester)
t3 = threading.Thread(target=digester)
t4 = threading.Thread(target=digester)
for t in (t1, t2, t3, t4):
    t.start()
for t in (t1, t2, t3, t4):
    t.join(timeout=120)
    if t.is_alive():
        errors.append(RuntimeError('thread timed out'))

if errors:
    for e in errors:
        print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
else:
    print('OK')
"""


# ---------------------------------------------------------------------------
# Scenario: concurrent reset() during update()  – most destructive
# ---------------------------------------------------------------------------

CONCURRENT_RESET_CODE = r"""
import sys, threading; from xxhash import threadsafe as xxhash

h = xxhash.xxh32()
BLOCK = b'x' * (4 * 1024 * 1024)
N = 50
barrier = threading.Barrier(4)
errors = []

def updater():
    barrier.wait()
    for _ in range(N):
        h.update(BLOCK)

def reseter():
    barrier.wait()
    for _ in range(N * 3):
        try:
            h.reset()
        except Exception as e:
            errors.append(e)

t1 = threading.Thread(target=updater)
t2 = threading.Thread(target=reseter)
t3 = threading.Thread(target=reseter)
t4 = threading.Thread(target=reseter)
for t in (t1, t2, t3, t4):
    t.start()
for t in (t1, t2, t3, t4):
    t.join(timeout=120)
    if t.is_alive():
        errors.append(RuntimeError('thread timed out'))

if errors:
    for e in errors:
        print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
else:
    print('OK')
"""


# ---------------------------------------------------------------------------
# Scenario: concurrent update() from all threads  – rawest race
# ---------------------------------------------------------------------------

CONCURRENT_UPDATE_CODE = r"""
import sys, threading; from xxhash import threadsafe as xxhash

h = xxhash.xxh32()
BLOCK = b'x' * (4 * 1024 * 1024)
N = 50
barrier = threading.Barrier(4)
errors = []

def updater():
    barrier.wait()
    for _ in range(N):
        try:
            h.update(BLOCK)
        except Exception as e:
            errors.append(e)

t1 = threading.Thread(target=updater)
t2 = threading.Thread(target=updater)
t3 = threading.Thread(target=updater)
t4 = threading.Thread(target=updater)
for t in (t1, t2, t3, t4):
    t.start()
for t in (t1, t2, t3, t4):
    t.join(timeout=120)
    if t.is_alive():
        errors.append(RuntimeError('thread timed out'))

if errors:
    for e in errors:
        print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
else:
    print('OK')
"""


# ---------------------------------------------------------------------------
# Scenario: non-determinism detector
#
# If there is a data race, concurrent updates to the same state will
# produce different hash values on each run.  We run the race multiple
# times and count unique digests – more than 1 is evidence of corruption.
# ---------------------------------------------------------------------------

NON_DETERMINISM_CODE = r"""
import sys, threading; from xxhash import threadsafe as xxhash

h = xxhash.xxh32()
BLOCK = b'x' * (4 * 1024 * 1024)
N = 30
barrier = threading.Barrier(4)
results = set()

def updater():
    barrier.wait()
    for _ in range(N):
        h.update(BLOCK)

t1 = threading.Thread(target=updater)
t2 = threading.Thread(target=updater)
t3 = threading.Thread(target=updater)
t4 = threading.Thread(target=updater)
for t in (t1, t2, t3, t4):
    t.start()
for t in (t1, t2, t3, t4):
    t.join(timeout=120)

print(h.digest().hex())
"""


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# xxh128: update + reset race
#
# xxh128 uses XXH3_state_t which contains a ``const unsigned char* extSecret``
# pointer.  When reset() is called while update() is running (GIL released),
# ``XXH3_128bits_reset_withSeed()`` sets ``extSecret = NULL`` while
# ``XXH3_128bits_update()`` may still dereference it, causing a segfault.
# ---------------------------------------------------------------------------

XXH128_UPDATE_RESET_CODE = r"""
import sys, threading; from xxhash import threadsafe as xxhash

h = xxhash.xxh128()
BLOCK = b'x' * 16          # tiny block: more calls = more race windows
N = 200                     # iterations per thread
NUM_UPDATERS = 6
NUM_RESETERS = 6
barrier = threading.Barrier(NUM_UPDATERS + NUM_RESETERS)
errors = []

def updater():
    barrier.wait()
    for _ in range(N):
        try:
            h.update(BLOCK)
        except Exception as e:
            errors.append(e)

def reseter():
    barrier.wait()
    for _ in range(N * 3):
        try:
            h.reset()
        except Exception as e:
            errors.append(e)

threads = [threading.Thread(target=updater) for _ in range(NUM_UPDATERS)]
threads += [threading.Thread(target=reseter) for _ in range(NUM_RESETERS)]
for t in threads:
    t.start()
for t in threads:
    t.join(timeout=120)
    if t.is_alive():
        errors.append(RuntimeError('thread timed out'))

if errors:
    for e in errors:
        print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
else:
    print('OK')
"""


# ---------------------------------------------------------------------------
# xxh128: update + copy race
#
# copy() calls XXH3_copyState() which does a memcpy of the entire
# XXH3_state_t, including the extSecret pointer.  If update() is
# concurrently modifying the state, the copied state can have torn
# values leading to crashes when used later.
# ---------------------------------------------------------------------------

XXH128_UPDATE_COPY_CODE = r"""
import sys, threading; from xxhash import threadsafe as xxhash

h = xxhash.xxh128()
copies = []
BLOCK = b'x' * 16
N = 150
NUM_UPDATERS = 4
NUM_COPIERS = 4
barrier = threading.Barrier(NUM_UPDATERS + NUM_COPIERS)
errors = []
lock = threading.Lock()

def updater():
    barrier.wait()
    for _ in range(N):
        try:
            h.update(BLOCK)
        except Exception as e:
            errors.append(e)

def copier():
    barrier.wait()
    for _ in range(N):
        try:
            c = h.copy()
            with lock:
                copies.append(c)
            # Use the copy immediately (may crash if state was torn)
            c.update(BLOCK)
            _ = c.digest()
        except Exception as e:
            errors.append(e)

threads = [threading.Thread(target=updater) for _ in range(NUM_UPDATERS)]
threads += [threading.Thread(target=copier) for _ in range(NUM_COPIERS)]
for t in threads:
    t.start()
for t in threads:
    t.join(timeout=120)
    if t.is_alive():
        errors.append(RuntimeError('thread timed out'))

if errors:
    for e in errors:
        print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
else:
    print('OK')
"""


# ---------------------------------------------------------------------------
# xxh128: all-methods fuzzer
#
# Every thread picks a random method (update, reset, copy, digest) and
# calls it on the shared xxh128 object.  Maximum contention.
# ---------------------------------------------------------------------------

XXH128_ALL_METHODS_CODE = r"""
import sys, random, threading; from xxhash import threadsafe as xxhash

h = xxhash.xxh128()
BLOCK = b'x' * 32
N = 100
NUM_THREADS = 12
barrier = threading.Barrier(NUM_THREADS)
errors = []

def worker():
    barrier.wait()
    for _ in range(N):
        method = random.randint(0, 3)
        try:
            if method == 0:
                h.update(BLOCK)
            elif method == 1:
                h.reset()
            elif method == 2:
                c = h.copy()
                c.update(BLOCK)
                _ = c.digest()
            else:
                _ = h.digest()
        except Exception as e:
            errors.append(e)

threads = [threading.Thread(target=worker) for _ in range(NUM_THREADS)]
for t in threads:
    t.start()
for t in threads:
    t.join(timeout=120)
    if t.is_alive():
        errors.append(RuntimeError('thread timed out'))

if errors:
    for e in errors:
        print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
else:
    print('OK')
"""


# ---------------------------------------------------------------------------
# xxh64: aggressive race with maximum thread count
# ---------------------------------------------------------------------------

XXH64_AGGRESSIVE_RACE_CODE = r"""
import sys, threading; from xxhash import threadsafe as xxhash

h = xxhash.xxh64()
BLOCK = b'x' * 16
N = 300
NUM_THREADS = 16
barrier = threading.Barrier(NUM_THREADS)
errors = []

def worker():
    barrier.wait()
    for _ in range(N):
        try:
            h.update(BLOCK)
            if _ % 5 == 0:
                h.reset()
        except Exception as e:
            errors.append(e)

threads = [threading.Thread(target=worker) for _ in range(NUM_THREADS)]
for t in threads:
    t.start()
for t in threads:
    t.join(timeout=120)
    if t.is_alive():
        errors.append(RuntimeError('thread timed out'))

if errors:
    for e in errors:
        print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
else:
    print('OK')
"""


class TestThreadSafety(unittest.TestCase):
    """Verify that concurrent access to a single threadsafe hash object works.

    These tests import ``xxhash.threadsafe`` (not the default ``xxhash``
    module), which uses a per-object lock around all streaming operations.
    We run each scenario many times (``REPETITIONS``) to verify that no
    crashes, deadlocks, or unexpected exceptions occur.
    """

    REPETITIONS = int(os.environ.get("XXHASH_TEST_REPETITIONS", "20"))
    TIMEOUT = int(os.environ.get("XXHASH_TEST_TIMEOUT", "120"))

    def _run_many(self, code, scenario_name):
        failed = 0
        errors = []
        for i in range(self.REPETITIONS):
            rc, out, err = _run_in_subprocess(code, timeout=self.TIMEOUT)
            if rc == -999:
                failed += 1
                errors.append(f"run {i}: TIMEOUT (possible deadlock)")
            elif rc == -signal.SIGSEGV:
                failed += 1
                errors.append(f"run {i}: SEGFAULT")
            elif rc == -signal.SIGABRT:
                failed += 1
                errors.append(f"run {i}: SIGABRT")
            elif sys.platform == "win32" and rc >= 0xC0000000:
                # Windows structured exception (STATUS_ACCESS_VIOLATION, etc.)
                failed += 1
                errors.append(f"run {i}: Windows exception 0x{rc:08X}")
            elif rc != 0:
                # Any non-zero exit is a failure in thread-safety tests
                failed += 1
                errors.append(f"run {i}: exit {rc} {err[:200]}")
            # else: OK, no news is good news

        if failed:
            self.fail(
                f"{scenario_name}: {failed}/{self.REPETITIONS} runs failed: "
                f"{'; '.join(errors[:5])}"
            )

    # -- individual scenarios ------------------------------------------------

    def test_concurrent_digest(self):
        """update() + concurrent digest() – read races with write."""
        self._run_many(CONCURRENT_DIGEST_CODE, "digest × update")

    def test_concurrent_reset(self):
        """update() + concurrent reset() – write races with write."""
        self._run_many(CONCURRENT_RESET_CODE, "reset × update")

    def test_concurrent_update(self):
        """All threads call update() concurrently – write-write race."""
        self._run_many(CONCURRENT_UPDATE_CODE, "update × update")

    def test_xxh128_update_reset_race(self):
        """xxh128: concurrent update() + reset() – races on XXH3_state_t
        which contains a ``const unsigned char* extSecret`` pointer that
        ``reset()`` sets to NULL while ``update()`` may dereference it.
        """
        self._run_many(XXH128_UPDATE_RESET_CODE, "xxh128 update × reset")

    def test_xxh128_update_copy_race(self):
        """xxh128: concurrent update() + copy() – memcpy races with write."""
        self._run_many(XXH128_UPDATE_COPY_CODE, "xxh128 update × copy")

    def test_xxh128_all_methods_fuzz(self):
        """xxh128: all methods (update/reset/copy/digest) racing together."""
        self._run_many(XXH128_ALL_METHODS_CODE, "xxh128 all-methods fuzz")

    def test_xxh64_update_reset_race_aggressive(self):
        """xxh64: aggressive update + reset race with many threads."""
        self._run_many(XXH64_AGGRESSIVE_RACE_CODE, "xxh64 aggressive race")


class TestNonDeterminism(unittest.TestCase):
    """Detect non-deterministic digests caused by data races.

    If concurrent updates race on the internal state, the final digest
    will differ from run to run.  We run the race multiple times and
    check whether we get more than one unique result.
    """

    SAMPLES = int(os.environ.get("XXHASH_TEST_SAMPLES", "10"))
    TIMEOUT = int(os.environ.get("XXHASH_TEST_TIMEOUT", "120"))

    def test_concurrent_update_is_deterministic(self):
        """Concurrent update() on a threadsafe object should be deterministic."""
        digests = set()
        for i in range(self.SAMPLES):
            rc, out, err = _run_in_subprocess(
                NON_DETERMINISM_CODE, timeout=self.TIMEOUT
            )
            if rc != 0:
                self.fail(f"run {i} failed: exit {rc} {err[:200]}")
            digest = out.strip()
            if digest:
                digests.add(digest)

        if len(digests) > 1:
            # Non-determinism should not happen with per-object locking.
            # If it does, the lock is not working correctly.
            self.fail(
                f"DATA RACE: {len(digests)} unique digests across "
                f"{self.SAMPLES} runs (digests: {sorted(digests)[:5]}...)\n"
                "Per-object locking should prevent this. "
                "The lock may not be working correctly."
            )


# ---------------------------------------------------------------------------
# Known issues / expected failures
# ---------------------------------------------------------------------------

# With per-object locking, all races are now prevented.  The tests above
# verify that concurrent access no longer crashes and that hash results
# are deterministic.

if __name__ == "__main__":
    unittest.main()
