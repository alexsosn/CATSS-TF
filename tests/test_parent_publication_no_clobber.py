"""Filesystem adversarial regression for BHSA/LXX native TF module publication."""

from __future__ import annotations

import importlib
import pathlib

import pytest

from catss_tf.tf_schema import TfModuleMetadata


@pytest.mark.parametrize("projection", ["bhsa", "lxx"])
@pytest.mark.parametrize("competitor", ["empty-directory", "dangling-symlink"])
def test_parent_module_publisher_refuses_late_competing_destination(
    projection: str,
    competitor: str,
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Do not overwrite a destination created after initial preflight."""
    materializer = importlib.import_module(f"catss_tf.{projection}_materializer")
    destination = tmp_path / f"catss-{projection}"
    outside = tmp_path / "no-target"
    claimed_inodes: list[int] = []

    def inject_claim_after_staging(
        staging: pathlib.Path,
        features: dict[str, dict[int, int | str]],
        *,
        metadata: TfModuleMetadata,
        max_node: int,
    ) -> None:
        # Only serialize a placeholder TF file. Keep the actual filesystem
        # stage, TSV writer, rename/publish and failure cleanup under test.
        (staging / "otype.tf").write_text("staged", encoding="utf-8")
        if competitor == "empty-directory":
            destination.mkdir()
        else:
            destination.symlink_to(outside, target_is_directory=True)
        claimed_inodes.append(destination.lstat().st_ino)

    monkeypatch.setattr(materializer, "write_tf_module", inject_claim_after_staging)
    metadata = TfModuleMetadata(
        projection=projection,  # type: ignore[arg-type]
        parent_repo="parent",
        parent_version="test",
        parent_release=None,
        parent_commit=None,
        software_version="test",
    )

    with pytest.raises(FileExistsError):
        materializer._publish_bundle(destination, features={}, metadata=metadata, sidecars={})

    # The rival path must have the *same* identity and no added material.
    assert destination.lstat().st_ino == claimed_inodes[0]
    if competitor == "empty-directory":
        assert destination.is_dir()
        assert tuple(destination.iterdir()) == ()
    else:
        assert destination.is_symlink()
        assert destination.readlink() == outside
        assert not outside.exists()
    assert not tuple(tmp_path.glob(f".catss-{projection}.tmp-*"))
