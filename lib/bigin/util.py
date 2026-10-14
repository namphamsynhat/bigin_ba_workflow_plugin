"""Small shared helpers: dates, id ordering, JSON I/O, output."""
import contextlib
import datetime
import errno
import hashlib
import json
import os
import re
import sys
import time

try:
    import fcntl
except ImportError:  # Windows
    fcntl = None

try:
    import msvcrt
except ImportError:  # POSIX
    msvcrt = None

ID_RE = re.compile(r"\b(UC|BR|INT|EN|PP|UX|PRD|FR|SCN)-(\d+)\b")

# Windows msvcrt.locking contention (sharing / lock violation), not generic I/O failure.
_MSVCRT_LOCK_RETRY_ERRNOS = frozenset({errno.EACCES, errno.EAGAIN, getattr(errno, "EDEADLK", 35)})
_MSVCRT_LOCK_RETRY_WINERR = frozenset({32, 33})  # ERROR_SHARING_VIOLATION, ERROR_LOCK_VIOLATION
_MSVCRT_LOCK_WAIT_SEC = 120


def _msvcrt_lock_retryable(exc):
    if not isinstance(exc, OSError):
        return False
    if exc.errno in _MSVCRT_LOCK_RETRY_ERRNOS:
        return True
    return getattr(exc, "winerror", None) in _MSVCRT_LOCK_RETRY_WINERR


@contextlib.contextmanager
def exclusive_file_lock(path):
    """Exclusive lock on ``path`` (created if missing). Uses fcntl on POSIX, msvcrt on Windows.

    On Windows, never read the locked byte — a contended ``read`` raises PermissionError
    before ``LK_LOCK`` can wait. Ensure a lockable byte via size, then lock with retry
    (``LK_LOCK`` only waits ~10s per call).
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "a+b") as f:
        if fcntl:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        elif msvcrt:
            # Size check / append — do not read byte 0 (that byte is what we lock).
            if os.fstat(f.fileno()).st_size == 0:
                f.write(b"\0")
                f.flush()
            f.seek(0)
            deadline = time.monotonic() + _MSVCRT_LOCK_WAIT_SEC
            while True:
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
                    break
                except OSError as e:
                    if not _msvcrt_lock_retryable(e):
                        raise
                    if time.monotonic() >= deadline:
                        raise EngineError(
                            f"timed out after {_MSVCRT_LOCK_WAIT_SEC}s waiting for lock on {path}"
                        ) from e
                    f.seek(0)
                    time.sleep(0.05)
        try:
            yield
        finally:
            if fcntl:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            elif msvcrt:
                f.seek(0)
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass


def today():
    """ISO date. BIGIN_TODAY overrides it so tests and replays are reproducible."""
    return os.environ.get("BIGIN_TODAY") or datetime.date.today().isoformat()


def now_stamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def num_key(ident):
    """Sort key for ids like UC-007, BR-2550, S12, '12a'."""
    m = re.search(r"(\d+)", str(ident))
    return (str(ident).split("-")[0] if "-" in str(ident) else "", int(m.group(1)) if m else 0, str(ident))


def sort_ids(ids):
    return sorted(dict.fromkeys(ids), key=num_key)


def sha(text):
    """Anchor fingerprint: sha1 of whitespace-normalised text (first 12 hex chars)."""
    norm = re.sub(r"\s+", " ", (text or "")).strip()
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]


def norm_ws(text):
    return re.sub(r"\s+", " ", text or "").strip()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(obj, path=None):
    text = json.dumps(obj, indent=2, ensure_ascii=False) + "\n"
    if path:
        d = os.path.dirname(os.path.abspath(path))
        os.makedirs(d, exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    return text


def load_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def batch_mode():
    return os.environ.get("BIGIN_BATCH") == "1"


class EngineError(Exception):
    """A refusal the caller should see as one line, not a traceback."""


def say(*parts):
    print(*parts)
    sys.stdout.flush()
