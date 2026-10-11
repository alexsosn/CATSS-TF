"""CATSS parallel-source acquisition and deterministic source inspection."""

import collections.abc
import dataclasses
import hashlib
import os
import pathlib
import ssl
import tempfile
import typing
import urllib.error
import urllib.parse
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
    ca_bundle: str | os.PathLike[str] | None = None,
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

    upstream = _verified_https_base_url(base_url)
    if ca_bundle is not None and not pathlib.Path(ca_bundle).is_file():
        raise SourceDownloadError(f"verified CA bundle must be an existing PEM file: {ca_bundle}")
    for name in names:
        _validate_filename(name)
        target = root / name
        if target.is_file() and target.stat().st_size > 0 and not overwrite:
            continue

        url = f"{upstream}/{name}"
        try:
            if ca_bundle is None:
                payload = _fetch_bytes(url)
            else:
                payload = _fetch_bytes(url, ca_bundle=ca_bundle)
        except Exception as exc:
            reason = exc.reason if isinstance(exc, urllib.error.URLError) else exc
            if isinstance(reason, ssl.SSLCertVerificationError):
                raise SourceDownloadError(
                    f"TLS certificate validation failed for {url}: {reason}. "
                    "Use an independently verified CA chain with --ca-bundle PATH, "
                    "an explicitly authenticated HTTPS origin via --base-url HTTPS_URL, "
                    "or an already-downloaded local CATSS source directory. "
                    "Do not disable certificate verification."
                ) from exc
            raise SourceDownloadError(f"failed to download {url}: {exc}") from exc
        if not payload:
            raise SourceDownloadError(f"empty response while downloading {url}")

        # Allocate an exclusive, unique sibling instead of reusing a fixed
        # '.part' name: Path.write_bytes follows pre-existing symlinks.
        # Atomic replacement on this filesystem must not touch anyone
        # else's stale partial file.
        partial: pathlib.Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=root,
                prefix=f".{target.name}.",
                suffix=".tmp",
                delete=False,
            ) as staged:
                partial = pathlib.Path(staged.name)
                staged.write(payload)
            os.replace(partial, target)
        finally:
            if partial is not None:
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


def _verified_https_base_url(value: str) -> str:
    """Reject ambiguous or insecure origins before any network I/O."""
    if _url_contains_controls(value):
        raise SourceDownloadError("CATSS source requires an HTTPS base URL without controls")
    try:
        parts = urllib.parse.urlsplit(value)
        hostname = parts.hostname
        port = parts.port
    except ValueError as exc:
        raise SourceDownloadError("CATSS source requires a syntactically valid HTTPS URL") from exc
    if (
        (port is not None and port == 0)
        or value != value.strip()
        or parts.scheme != "https"
        or not hostname
        or parts.username is not None
        or parts.password is not None
        or "?" in value
        or "#" in value
    ):
        raise SourceDownloadError(
            "CATSS source requires an HTTPS base URL without credentials, query or fragment"
        )
    return value.rstrip("/")


def _url_contains_controls(value: str) -> bool:
    return any(ord(character) < 32 or ord(character) == 127 for character in value)


class _HttpsOnlyRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Never let a verified initial request downgrade or change its origin."""

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: typing.Any,
        code: int,
        msg: str,
        headers: typing.Any,
        newurl: str,
    ) -> urllib.request.Request | None:
        if _url_contains_controls(newurl):
            raise urllib.error.URLError("HTTPS redirects may not contain control characters")
        before = urllib.parse.urlsplit(req.full_url)
        after = urllib.parse.urlsplit(newurl)
        if (
            after.scheme != "https"
            or not after.hostname
            or after.username is not None
            or after.password is not None
            or (after.hostname, after.port) != (before.hostname, before.port)
        ):
            raise urllib.error.URLError(
                "HTTPS redirect to a different origin or insecure protocol is forbidden"
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _fetch_bytes(url: str, *, ca_bundle: str | os.PathLike[str] | None = None) -> bytes:
    context = ssl.create_default_context(cafile=str(ca_bundle) if ca_bundle is not None else None)
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=context),
        _HttpsOnlyRedirectHandler(),
    )
    request = urllib.request.Request(url, headers={"User-Agent": "CATSS-TF/0.0.0"})
    with opener.open(request, timeout=60) as response:
        return typing.cast(bytes, response.read())


def _sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
