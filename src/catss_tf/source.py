"""Inspection of user-supplied CATSS parallel source directories."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Literal


class SourceInspectionError(ValueError):
    """Raised when a configured CATSS source cannot satisfy the source contract."""


@dataclass(frozen=True, slots=True)
class SourceFileFingerprint:
    """Deterministic identity of one CATSS parallel input file."""

    relative_path: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True, slots=True)
class ParallelSourceManifest:
    """Canonical fingerprint of the CATSS parallel files selected for parsing."""

    files: tuple[SourceFileFingerprint, ...]
    source_kind: Literal["catss-parallel"] = "catss-parallel"


def inspect_parallel_source(directory: str | PathLike[str]) -> ParallelSourceManifest:
    """Fingerprint direct-child *.par files in a user-supplied directory.

    Discovery is deliberately non-recursive. CATSS-TF does not acquire data and
    does not infer a broader CATSS installation from the supplied path.
    """

    root = Path(directory)
    if not root.exists():
        raise SourceInspectionError(f"CATSS parallel source does not exist: {root}")
    if not root.is_dir():
        raise SourceInspectionError(f"CATSS parallel source is not a directory: {root}")

    paths = sorted(
        (path for path in root.iterdir() if path.is_file() and path.suffix == ".par"),
        key=lambda path: path.name,
    )
    if not paths:
        raise SourceInspectionError(
            f"CATSS parallel source contains no direct-child .par files: {root}"
        )

    files = tuple(
        SourceFileFingerprint(
            relative_path=path.name,
            size_bytes=path.stat().st_size,
            sha256=_sha256(path),
        )
        for path in paths
    )
    return ParallelSourceManifest(files=files)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
