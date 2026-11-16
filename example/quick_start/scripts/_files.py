"""Small file-safety primitives shared by the teaching helpers.

Copyright (c) 2026 Huawei Technologies Co., Ltd.
Licensed under Mulan PSL v2. See the repository LICENSE.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import stat
import tempfile


class PreparationError(Exception):
    """Expected input, conflict or state error, safe to show without a traceback."""


def safe_path(value):
    """Reject traversal, links (including ancestor links), and special files."""
    path = Path(value).expanduser()
    if ".." in path.parts:
        raise PreparationError("Parent traversal '..' is not accepted: " + str(path))
    path = Path(os.path.abspath(path))
    for part in reversed((path, *path.parents)):
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise PreparationError("Symbolic links/junctions are not managed: " + str(part))
        if part.exists() and not (part.is_file() or part.is_dir()):
            raise PreparationError("Not a regular file or directory: " + str(part))
    return path


def read_file(path):
    path = safe_path(path)
    if not path.is_file():
        raise PreparationError("Required regular file is missing: " + str(path))
    return path.read_bytes()


def check_copy(path, content):
    path = safe_path(path)
    if path.exists() and (not path.is_file() or path.read_bytes() != content):
        raise PreparationError("File conflict; preserve your edits or use a fresh directory: " + str(path))


@contextmanager
def directory_lock(directory):
    directory = safe_path(directory)
    if directory.exists() and not directory.is_dir():
        raise PreparationError("Expected a directory: " + str(directory))
    directory.mkdir(parents=True, exist_ok=True)
    path = safe_path(directory / ".msot-prepare.lock")
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise PreparationError("Preparation lock exists (another writer or interrupted operation); "
                               "inspect it before retrying: " + str(path)) from error
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as lock:
            lock.write("pid={}\n".format(os.getpid()))
            lock.flush()
            os.fsync(lock.fileno())
        yield
    finally:
        path.unlink()


def atomic_write(path, content, mode=None):
    """Replace one file using a private same-directory temporary file."""
    path = safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not path.is_file():
        raise PreparationError("Expected a regular file: " + str(path))
    if mode is None:
        mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    fd, name = tempfile.mkstemp(prefix=".msot-write-", dir=str(path.parent))
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def apply_changes(changes, pending=None):
    """Preflight, journal, replace; roll back ordinary failures, never guess after a crash.

    Callers hold the directory locks. The journal deliberately remains if the process
    is interrupted or rollback fails; subsequent helpers must refuse that state.
    """
    if pending is not None:
        pending = safe_path(pending)
        if pending.exists():
            raise PreparationError("Unfinished transaction: " + str(pending))
    updates = {}
    originals = {}
    for target, content in changes.items():
        target = safe_path(target)
        if target.exists() and not target.is_file():
            raise PreparationError("Expected a regular file: " + str(target))
        old = target.read_bytes() if target.exists() else None
        if old == content:
            continue
        originals[target] = (old, stat.S_IMODE(target.stat().st_mode) if old is not None else None)
        updates[target] = content
    if not updates:
        return
    created_dirs = {directory for target in (*updates, *((pending,) if pending else ()))
                    for directory in target.parents if not directory.exists()}
    if pending is not None:
        atomic_write(pending, json.dumps({"pid": os.getpid(), "files": [str(p) for p in updates]},
                                        indent=2).encode("utf-8"), 0o600)
    written = []
    try:
        for target, content in updates.items():
            atomic_write(target, content)
            written.append(target)
    except Exception as error:
        try:
            for target in reversed(written):
                old, mode = originals[target]
                if old is None:
                    safe_path(target).unlink()
                else:
                    atomic_write(target, old, mode)
        except Exception as rollback_error:
            raise PreparationError("Write and rollback failed; do not delete the transaction record. "
                                   "Inspect managed files: " + str(rollback_error)) from error
        if pending is not None:
            pending.unlink()
        for directory in sorted(created_dirs, key=lambda p: len(p.parts), reverse=True):
            try:
                directory.rmdir()  # Only remove directories this transaction created, if empty.
            except OSError:
                pass
        raise PreparationError("Write failed; file contents rolled back: " + str(error)) from error
    if pending is not None:
        pending.unlink()
