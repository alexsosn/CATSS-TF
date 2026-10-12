"""Read-only BHSA 2021 mapping-critical raw Text-Fabric feature identity check.

This does NOT authenticate caller trust: Agora must resolve an immutable
managed parent and mount it read-only. Before loading it through Text-Fabric,
verify actual raw feature bytes against the pinned BHSA Git blob IDs.
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import re
import stat
from collections.abc import Mapping

from catss_tf.bhsa_schema import BHSA_FEATURE_BLOB_SHAS, BHSA_VERSION

_CHUNK_BYTES = 1024 * 1024
_BLOB_ID = re.compile(r"[0-9a-f]{40}\Z")
_FEATURE_NAME = re.compile(r"[A-Za-z0-9_]+\Z")


class BhsaParentFingerprintError(ValueError):
    """The candidate parent does not match the pinned BHSA source features."""


def _fingerprint_file(path: pathlib.Path) -> str:
    """Hash an unchanged regular file using Git's raw blob-object algorithm."""
    try:
        before = path.lstat()
    except OSError as exc:
        raise BhsaParentFingerprintError(f"BHSA feature missing: {path.name}") from exc
    if not stat.S_ISREG(before.st_mode):
        raise BhsaParentFingerprintError(f"BHSA feature is not a regular file: {path.name}")

    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    flags |= getattr(os, "O_BINARY", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise BhsaParentFingerprintError(f"cannot open BHSA feature: {path.name}") from exc

    try:
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode) or (
            before.st_dev,
            before.st_ino,
        ) != (opened.st_dev, opened.st_ino):
            raise BhsaParentFingerprintError(f"BHSA feature changed before open: {path.name}")

        digest = hashlib.sha1(
            b"blob " + str(opened.st_size).encode("ascii") + b"\0", usedforsecurity=False
        )
        total = 0
        while chunk := os.read(fd, _CHUNK_BYTES):
            total += len(chunk)
            if total > opened.st_size:
                raise BhsaParentFingerprintError(f"BHSA feature grew during read: {path.name}")
            digest.update(chunk)

        after = os.fstat(fd)
        try:
            name_after = path.lstat()
        except OSError as exc:
            raise BhsaParentFingerprintError(
                f"BHSA feature disappeared during read: {path.name}"
            ) from exc
        identity = lambda entry: (  # noqa: E731
            entry.st_dev,
            entry.st_ino,
            entry.st_size,
            entry.st_mtime_ns,
            entry.st_ctime_ns,
        )
        if (
            total != opened.st_size
            or identity(before) != identity(opened)
            or identity(opened) != identity(after)
            or identity(after) != identity(name_after)
        ):
            raise BhsaParentFingerprintError(f"BHSA feature changed during read: {path.name}")
        return digest.hexdigest()
    finally:
        os.close(fd)


def verify_bhsa_parent_feature_blobs(
    parent_directory: str | os.PathLike[str],
    *,
    parent_version: str,
    expected_blob_shas: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Verify selected BHSA TF raw features against their pinned Git blob IDs.

    By default this checks ALL eight immutable mapping-critical BHSA 2021
    features; the injectable expectation supports synthetic unit fixtures only.
    This function never creates a parent binding or approves an arbitrary
    directory as trusted. The later Agora adapter must require a trusted
    read-only parent from Agora and a compatible exact source revision.
    """
    if parent_version != BHSA_VERSION:
        raise BhsaParentFingerprintError(
            f"BHSA parent version must be {BHSA_VERSION}, got {parent_version!r}"
        )

    expected = dict(BHSA_FEATURE_BLOB_SHAS if expected_blob_shas is None else expected_blob_shas)
    if not expected or any(
        not isinstance(name, str)
        or _FEATURE_NAME.fullmatch(name) is None
        or not isinstance(blob_id, str)
        or _BLOB_ID.fullmatch(blob_id) is None
        for name, blob_id in expected.items()
    ):
        raise BhsaParentFingerprintError("invalid BHSA expected Git blob fingerprint mapping")

    root = pathlib.Path(parent_directory).expanduser().absolute()
    if root.is_symlink() or not root.is_dir() or root.resolve(strict=True) != root:
        raise BhsaParentFingerprintError("BHSA parent must be a real non-symlink directory")

    observed: dict[str, str] = {}
    for feature in sorted(expected):
        value = _fingerprint_file(root / f"{feature}.tf")
        if value != expected[feature]:
            raise BhsaParentFingerprintError(
                f"BHSA pinned feature fingerprint mismatch: {feature}"
            )
        observed[feature] = value
    return observed
