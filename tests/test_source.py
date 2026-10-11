import os
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


def test_download_parallel_source_manifest_excludes_unrequested_par_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "parallel"
    destination.mkdir()
    (destination / "99.Unrelated.par").write_bytes(b"unrelated")

    monkeypatch.setattr(source, "_fetch_bytes", lambda url: b"first")

    manifest = source.download_parallel_source(
        destination,
        base_url="https://example.invalid/parallel",
        filenames=("01.First.par",),
    )

    assert [item.relative_path for item in manifest.files] == ["01.First.par"]
    assert (destination / "99.Unrelated.par").exists()


def test_download_ignores_preexisting_partial_symlink_without_clobbering_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "parallel"
    destination.mkdir()
    victim = tmp_path / "unrelated-private.txt"
    victim.write_bytes(b"keep this unrelated content")
    old_partial = destination / "01.First.par.part"
    old_partial.symlink_to(victim)

    monkeypatch.setattr(source, "_fetch_bytes", lambda url: b"actual CATSS payload")
    manifest = source.download_parallel_source(
        destination,
        base_url="https://example.invalid/parallel",
        filenames=("01.First.par",),
    )

    assert victim.read_bytes() == b"keep this unrelated content"
    assert old_partial.is_symlink() and old_partial.resolve() == victim
    assert (destination / "01.First.par").read_bytes() == b"actual CATSS payload"
    assert manifest.files[0].size_bytes == len(b"actual CATSS payload")


def test_download_preserves_unrelated_stale_partial_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "parallel"
    destination.mkdir()
    old_partial = destination / "01.First.par.part"
    old_partial.write_bytes(b"stale file owned by a different operation")
    monkeypatch.setattr(source, "_fetch_bytes", lambda url: b"new verified payload")

    source.download_parallel_source(
        destination,
        base_url="https://example.invalid/parallel",
        filenames=("01.First.par",),
    )

    assert old_partial.read_bytes() == b"stale file owned by a different operation"
    assert (destination / "01.First.par").read_bytes() == b"new verified payload"


def test_download_failed_replace_cleans_only_owned_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "parallel"
    destination.mkdir()
    original = destination / "01.First.par"
    original.write_bytes(b"verified earlier payload")
    stale = destination / "01.First.par.part"
    stale.write_bytes(b"untouched stale partial")
    monkeypatch.setattr(source, "_fetch_bytes", lambda url: b"new payload")

    def reject_replace(_src: object, _dst: object) -> None:
        raise OSError("synthetic rename failure")

    monkeypatch.setattr(os, "replace", reject_replace)
    with pytest.raises(OSError, match="synthetic rename failure"):
        source.download_parallel_source(
            destination,
            base_url="https://example.invalid/parallel",
            filenames=("01.First.par",),
            overwrite=True,
        )

    assert original.read_bytes() == b"verified earlier payload"
    assert stale.read_bytes() == b"untouched stale partial"
    assert not list(destination.glob(".01.First.par.*.tmp"))


def test_interleaved_downloads_do_not_share_temporary_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    destination = tmp_path / "parallel"
    calls = iter((b"outer payload", b"inner payload"))
    monkeypatch.setattr(source, "_fetch_bytes", lambda url: next(calls))
    real_replace = os.replace
    staged: list[Path] = []

    def interleaved_replace(src: object, dst: object) -> None:
        source_path = Path(str(src))
        staged.append(source_path)
        if len(staged) == 1:
            source.download_parallel_source(
                destination,
                base_url="https://example.invalid/parallel",
                filenames=("01.First.par",),
                overwrite=True,
            )
            assert source_path.read_bytes() == b"outer payload"
        real_replace(str(src), str(dst))

    monkeypatch.setattr(os, "replace", interleaved_replace)
    source.download_parallel_source(
        destination,
        base_url="https://example.invalid/parallel",
        filenames=("01.First.par",),
        overwrite=True,
    )
    assert len(staged) == 2 and staged[0] != staged[1]
    assert (destination / "01.First.par").read_bytes() == b"outer payload"
    assert not list(destination.glob(".01.First.par.*.tmp"))


@pytest.mark.parametrize("inside_root", [False, True])
def test_inspection_rejects_par_symlinks_even_when_target_is_regular(
    tmp_path: Path, inside_root: bool
) -> None:
    root = tmp_path / "parallel"
    root.mkdir()
    actual = (root if inside_root else tmp_path) / "real-source.txt"
    actual.write_bytes(b"not authenticated as a CATSS source")
    (root / "01.Genesis.par").symlink_to(actual)

    with pytest.raises(SourceInspectionError, match="symlink"):
        inspect_parallel_source(root)


def test_inspection_rejects_dangling_par_symlink_among_regular_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "01.Genesis.par").write_bytes(b"legitimate file")
    (tmp_path / "02.Exodus.par").symlink_to(tmp_path / "missing.par")

    with pytest.raises(SourceInspectionError, match="symlink"):
        inspect_parallel_source(tmp_path)


@pytest.mark.parametrize("overwrite", [False, True])
def test_download_rejects_existing_final_par_symlink_without_touching_referent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, overwrite: bool
) -> None:
    root = tmp_path / "parallel"
    root.mkdir()
    outside = tmp_path / "unrelated.txt"
    outside.write_bytes(b"not a CATSS file")
    link = root / "01.Genesis.par"
    link.symlink_to(outside)
    fetched: list[str] = []
    monkeypatch.setattr(source, "_fetch_bytes", lambda url: fetched.append(url) or b"new bytes")

    with pytest.raises(source.SourceDownloadError, match="symlink"):
        source.download_parallel_source(
            root,
            filenames=("01.Genesis.par",),
            base_url="https://example.invalid/parallel",
            overwrite=overwrite,
        )

    assert fetched == []
    assert link.is_symlink()
    assert outside.read_bytes() == b"not a CATSS file"


def test_download_preflights_later_symlink_before_fetching_earlier_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "parallel"
    root.mkdir()
    (root / "02.Exodus.par").symlink_to(tmp_path / "missing.par")
    fetched: list[str] = []
    monkeypatch.setattr(source, "_fetch_bytes", lambda url: fetched.append(url) or b"first")

    with pytest.raises(source.SourceDownloadError, match="symlink"):
        source.download_parallel_source(
            root,
            filenames=("02.Exodus.par", "01.Genesis.par"),
            base_url="https://example.invalid/parallel",
        )

    assert fetched == []
    assert not (root / "01.Genesis.par").exists()


def test_inspection_allows_explicit_symlink_to_source_root(tmp_path: Path) -> None:
    root = tmp_path / "real-parallel"
    root.mkdir()
    (root / "01.Genesis.par").write_bytes(b"local corpus")
    alias = tmp_path / "source-root-alias"
    alias.symlink_to(root, target_is_directory=True)

    manifest = inspect_parallel_source(alias)

    assert [(item.relative_path, item.size_bytes) for item in manifest.files] == [
        ("01.Genesis.par", len(b"local corpus"))
    ]
