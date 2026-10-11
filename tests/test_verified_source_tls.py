"""Regression gates for verified-only CCAT acquisition configuration."""

import io
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, cast

import pytest

from catss_tf import cli, source


def test_downloader_accepts_explicit_ca_bundle_with_verified_tls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """PEM trust must feed an SSL verification context, never CERT_NONE."""
    pem = tmp_path / "approved-chain.pem"
    pem.write_text("operator-supplied PEM", encoding="utf-8")
    observed: list[tuple[str, object]] = []
    default_create = ssl.create_default_context

    def capture_context(*, cafile: str | None = None) -> ssl.SSLContext:
        observed.append(("cafile", cafile))
        return default_create()

    class FakeOpener:
        def open(self, request: urllib.request.Request, *, timeout: int) -> io.BytesIO:
            observed.append(("url", request.full_url))
            return io.BytesIO(b"verified test payload")

    monkeypatch.setattr(ssl, "create_default_context", capture_context)
    monkeypatch.setattr(urllib.request, "build_opener", lambda *handlers: FakeOpener())
    download = cast(Any, source.download_parallel_source)
    manifest = download(
        tmp_path / "output",
        filenames=("01.Genesis.par",),
        base_url="https://verified.example.invalid/parallel",
        ca_bundle=pem,
    )
    assert observed == [
        ("cafile", str(pem)),
        ("url", "https://verified.example.invalid/parallel/01.Genesis.par"),
    ]
    assert manifest.files[0].size_bytes == len(b"verified test payload")


@pytest.mark.parametrize(
    "url",
    [
        "http://example.invalid/catss",
        "https://someone:password@example.invalid/catss",
        "https://example.invalid/catss?redirect=http://bad.invalid",
        "https://example.invalid/catss#fragment",
        "https://example.invalid/catss\nmisleading",
        "https://example.invalid:99999/catss",
    ],
)
def test_downloader_rejects_unverified_or_ambiguous_origin_before_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    def forbidden_fetch(_url: str) -> bytes:
        raise AssertionError("unverified origin reached network")

    monkeypatch.setattr(source, "_fetch_bytes", forbidden_fetch)
    with pytest.raises(source.SourceDownloadError, match="HTTPS"):
        source.download_parallel_source(tmp_path, base_url=url, filenames=("01.Genesis.par",))


def test_https_to_http_redirect_is_rejected() -> None:
    original = urllib.request.Request("https://ccat.sas.upenn.edu/start")
    handler = cast(Any, source)._HttpsOnlyRedirectHandler()
    with pytest.raises(urllib.error.URLError, match="HTTPS"):
        handler.redirect_request(
            original, None, 302, "Found", {}, "http://untrusted.example.invalid/file"
        )


def test_tls_certificate_error_has_safe_actionable_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def bad_cert(_url: str) -> bytes:
        raise urllib.error.URLError(ssl.SSLCertVerificationError("unable to get local issuer"))

    monkeypatch.setattr(source, "_fetch_bytes", bad_cert)
    with pytest.raises(source.SourceDownloadError, match=r"--ca-bundle.*--base-url"):
        source.download_parallel_source(tmp_path, filenames=("01.Genesis.par",))


def test_fetch_cli_passes_explicit_verified_options(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    recorded: list[tuple[str, str, Path]] = []

    def fake_download(
        path: str | Path, *, base_url: str, ca_bundle: str | Path
    ) -> source.ParallelSourceManifest:
        recorded.append((str(path), base_url, Path(ca_bundle)))
        return source.ParallelSourceManifest(files=())

    monkeypatch.setattr(cli, "download_parallel_source", fake_download)
    target = tmp_path / "parallel"
    cert = tmp_path / "trusted.pem"
    assert (
        cli.main(
            [
                "fetch",
                str(target),
                "--base-url",
                "https://approved.example.invalid/parallel",
                "--ca-bundle",
                str(cert),
            ]
        )
        == 0
    )
    assert recorded == [(str(target), "https://approved.example.invalid/parallel", cert)]
