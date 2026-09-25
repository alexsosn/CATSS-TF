"""CATSS parallel-source acquisition and deterministic source inspection."""

import collections.abc
import dataclasses
import hashlib
import os
import pathlib
import typing
import urllib.request

CCAT_PARALLEL_BASE_URL = "https://ccat.sas.upenn.edu/gopher/text/religion/biblical/parallel"
CCAT_USER_DECLARATION_URL = (
    "https://ccat.sas.upenn.edu/gopher/text/religion/biblical/parallel/00.user-declaration.txt"
)

# CCAT currently exposes 46 parallel files; preserve both Daniel OG and Theodotion.
CATSS_PARALLEL_FILENAMES: tuple[str, ...] = (
    "01.Genesis.par",
    "02.Exodus.par",
    "03.Lev.par",
    "04.Num.par",
    "05.Deut.par",
    "06.JoshB.par",
    "07.JoshA.par",
    "08.JudgesB.par",
    "09.JudgesA.par",
    "10.Ruth.par",
    "11.1Sam.par",
    "12.2Sam.par",
    "13.1Kings.par",
    "14.2Kings.par",
    "15.1Chron.par",
    "16.2Chron.par",
    "17.1Esdras.par",
    "18.Esther.par",
    "18.Ezra.par",
    "19.Neh.par",
    "20.Psalms.par",
    "22.Ps151.par",
    "23.Prov.par",
    "24.Qoh.par",
    "25.Cant.par",
    "26.Job.par",
    "27.Sirach.par",
    "28.Hosea.par",
    "29.Micah.par",
    "30.Amos.par",
    "31.Joel.par",
    "32.Jonah.par",
    "33.Obadiah.par",
    "34.Nahum.par",
    "35.Hab.par",
    "36.Zeph.par",
    "37.Haggai.par",
    "38.Zech.par",
    "39.Malachi.par",
    "40.Isaiah.par",
    "41.Jer.par",
    "42.Baruch.par",
    "43.Lam.par",
    "44.Ezekiel.par",
    "45.DanielOG.par",
    "46.DanielTh.par",
)


class SourceInspectionError(ValueError):
    """Raised when a configured CATSS source cannot satisfy the source contract."""


class SourceDownloadError(RuntimeError):
    """Raised when CATSS source acquisition cannot produce a valid local file."""


@dataclasses.dataclass(frozen=True, slots=True)
class SourceFileFingerprint:
    """Deterministic identity of one CATSS parallel input file."""

    relative_path: str
    size_bytes: int
    sha256: str


@dataclasses.dataclass(frozen=True, slots=True)
class ParallelSourceManifest:
    """Canonical fingerprint of the CATSS parallel files selected for parsing."""

    files: tuple[SourceFileFingerprint, ...]
    source_kind: typing.Literal["catss-parallel"] = "catss-parallel"


def download_parallel_source(
    destination: str | os.PathLike[str],
    *,
    base_url: str = CCAT_PARALLEL_BASE_URL,
    filenames: collections.abc.Iterable[str] = CATSS_PARALLEL_FILENAMES,
    overwrite: bool = False,
) -> ParallelSourceManifest:
    """Download CATSS parallel files directly from the configured upstream host.

    The caller is responsible for any upstream terms governing CATSS data.
    CATSS-TF supplies acquisition software but does not redistribute the corpus.
    Existing non-empty files are preserved unless overwrite is true.
    """

    root = pathlib.Path(destination)
    root.mkdir(parents=True, exist_ok=True)

    names = tuple(sorted(filenames))
    if not names:
        raise SourceDownloadError("no CATSS parallel filenames were requested")
    if len(names) != len(set(names)):
        raise SourceDownloadError("duplicate CATSS parallel filenames were requested")

    upstream = base_url.rstrip("/")
    for name in names:
        _validate_filename(name)
        target = root / name
        if target.is_file() and target.stat().st_size > 0 and not overwrite:
            continue

        url = f"{upstream}/{name}"
        try:
            payload = _fetch_bytes(url)
        except Exception as exc:
            raise SourceDownloadError(f"failed to download {url}: {exc}") from exc
        if not payload:
            raise SourceDownloadError(f"empty response while downloading {url}")

        partial = target.with_name(f"{target.name}.part")
        try:
            partial.write_bytes(payload)
            partial.replace(target)
        finally:
            partial.unlink(missing_ok=True)

    requested_paths = tuple(root / name for name in names)
    return _manifest_for_paths(root, requested_paths)


def inspect_parallel_source(directory: str | os.PathLike[str]) -> ParallelSourceManifest:
    """Fingerprint direct-child *.par files in a local CATSS parallel directory.

    Discovery is deliberately non-recursive so an accidentally broad path does
    not silently pull unrelated CATSS collections into the parser input.
    """

    root = pathlib.Path(directory)
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

    return _manifest_for_paths(root, tuple(paths))


def _manifest_for_paths(
    root: pathlib.Path, paths: tuple[pathlib.Path, ...]
) -> ParallelSourceManifest:
    files = tuple(
        SourceFileFingerprint(
            relative_path=path.relative_to(root).as_posix(),
            size_bytes=path.stat().st_size,
            sha256=_sha256(path),
        )
        for path in paths
    )
    return ParallelSourceManifest(files=files)


def _validate_filename(name: str) -> None:
    if not name.endswith(".par") or "/" in name or "\\" in name or pathlib.Path(name).name != name:
        raise SourceDownloadError(f"invalid CATSS parallel filename: {name!r}")


def _fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "CATSS-TF/0.0.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return typing.cast(bytes, response.read())


def _sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
