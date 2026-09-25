from pathlib import Path

import pytest

from catss_tf import source
from catss_tf.source import SourceInspectionError, inspect_parallel_source

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "catss_parallel_synthetic"


def test_inspect_parallel_source_fingerprints_direct_par_files() -> None:
    manifest = inspect_parallel_source(FIXTURE_DIR)

    assert manifest.source_kind == "catss-parallel"
    assert [(item.relative_path, item.size_bytes, item.sha256) for item in manifest.files] == [
        (
            "99.Synthetic.par",
            70,
            "8b5e85be3140f008025fd49bbbd5454d01d75e7e5f76f68cd72aafff8a46d9e0",
        )
    ]


def test_inspect_parallel_source_is_non_recursive_and_sorted(tmp_path: Path) -> None:
    (tmp_path / "20.Second.par").write_text("second", encoding="utf-8")
    (tmp_path / "01.First.par").write_text("first", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "02.Hidden.par").write_text("hidden", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignored", encoding="utf-8")

    manifest = inspect_parallel_source(tmp_path)

    assert [item.relative_path for item in manifest.files] == [
        "01.First.par",
        "20.Second.par",
    ]


def test_inspect_parallel_source_rejects_missing_directory(tmp_path: Path) -> None:
    with pytest.raises(SourceInspectionError, match="does not exist"):
        inspect_parallel_source(tmp_path / "missing")


def test_inspect_parallel_source_rejects_directory_without_par_files(tmp_path: Path) -> None:
    (tmp_path / "readme.txt").write_text("no corpus here", encoding="utf-8")

    with pytest.raises(SourceInspectionError, match=r"no direct-child \.par files"):
        inspect_parallel_source(tmp_path)


def test_download_parallel_source_fetches_directly_to_user_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen_urls: list[str] = []
    payloads = {
        "https://example.invalid/parallel/01.First.par": b"first",
        "https://example.invalid/parallel/02.Second.par": b"second",
    }

    def fake_fetch(url: str) -> bytes:
        seen_urls.append(url)
        return payloads[url]

    monkeypatch.setattr(source, "_fetch_bytes", fake_fetch)

    manifest = source.download_parallel_source(
        tmp_path / "parallel",
        base_url="https://example.invalid/parallel",
        filenames=("02.Second.par", "01.First.par"),
    )

    assert seen_urls == [
        "https://example.invalid/parallel/01.First.par",
        "https://example.invalid/parallel/02.Second.par",
    ]
    assert (tmp_path / "parallel" / "01.First.par").read_bytes() == b"first"
    assert (tmp_path / "parallel" / "02.Second.par").read_bytes() == b"second"
    assert [item.relative_path for item in manifest.files] == [
        "01.First.par",
        "02.Second.par",
    ]


def test_download_parallel_source_skips_existing_nonempty_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "parallel"
    destination.mkdir()
    (destination / "01.First.par").write_bytes(b"existing")

    def unexpected_fetch(url: str) -> bytes:
        raise AssertionError(f"unexpected network fetch: {url}")

    monkeypatch.setattr(source, "_fetch_bytes", unexpected_fetch)

    manifest = source.download_parallel_source(
        destination,
        base_url="https://example.invalid/parallel",
        filenames=("01.First.par",),
    )

    assert (destination / "01.First.par").read_bytes() == b"existing"
    assert manifest.files[0].size_bytes == len(b"existing")


def test_download_parallel_source_rejects_empty_response_without_partial_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(source, "_fetch_bytes", lambda url: b"")

    with pytest.raises(source.SourceDownloadError, match="empty response"):
        source.download_parallel_source(
            tmp_path / "parallel",
            base_url="https://example.invalid/parallel",
            filenames=("01.First.par",),
        )

    assert not (tmp_path / "parallel" / "01.First.par").exists()
    assert not (tmp_path / "parallel" / "01.First.par.part").exists()
