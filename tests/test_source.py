from pathlib import Path

import pytest

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
