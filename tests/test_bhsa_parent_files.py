"""RED-first BHSA parent raw-feature identity tests for issue #121."""

from __future__ import annotations

import hashlib
import os
import pathlib

import pytest

from catss_tf.bhsa_parent_files import (
    BhsaParentFingerprintError,
    verify_bhsa_parent_feature_blobs,
)
from catss_tf.bhsa_schema import BHSA_FEATURE_BLOB_SHAS

_SAMPLE = {
    feature: (b"@edge\n\n" if feature == "oslots" else b"@node\n@valueType=str\n\n")
    + (feature + "\tvalue\n").encode("utf-8")
    for feature in BHSA_FEATURE_BLOB_SHAS
}


def _expected(data: dict[str, bytes]) -> dict[str, str]:
    # Deliberately independent Git blob-ID calculation, not the production helper.
    return {
        name: hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\0" + blob).hexdigest()
        for name, blob in data.items()
    }


def _parent(root: pathlib.Path, data: dict[str, bytes] | None = None) -> pathlib.Path:
    root.mkdir()
    for name, blob in (data or _SAMPLE).items():
        (root / f"{name}.tf").write_bytes(blob)
    return root


def test_valid_pinned_shape_streams_exact_git_blob_ids(tmp_path: pathlib.Path) -> None:
    parent = _parent(tmp_path / "parent")
    expected = _expected(_SAMPLE)
    original = {p.name: p.read_bytes() for p in parent.iterdir()}
    found = verify_bhsa_parent_feature_blobs(
        parent, parent_version="2021", expected_blob_shas=expected
    )
    assert found == expected
    assert found["otype"] != hashlib.sha1(_SAMPLE["otype"]).hexdigest()
    assert {p.name: p.read_bytes() for p in parent.iterdir()} == original


def test_real_bhsa_profile_does_not_accept_forged_synthetic_parent(
    tmp_path: pathlib.Path,
) -> None:
    parent = _parent(tmp_path / "parent")
    with pytest.raises(BhsaParentFingerprintError, match="otype|oslots|mismatch"):
        verify_bhsa_parent_feature_blobs(parent, parent_version="2021")


@pytest.mark.parametrize("version", ["", "2020", "1935", "2021/other"])
def test_wrong_or_unspecified_parent_version_rejected_before_read(
    version: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    parent = _parent(tmp_path / "parent")

    def no_open(*args: object, **kwargs: object) -> None:
        raise AssertionError("invalid version must fail before reading parent")

    monkeypatch.setattr(os, "open", no_open)
    with pytest.raises(BhsaParentFingerprintError, match="2021"):
        verify_bhsa_parent_feature_blobs(parent, parent_version=version)


def test_missing_required_feature_is_fail_closed(tmp_path: pathlib.Path) -> None:
    data = dict(_SAMPLE)
    data.pop("g_cons_utf8")
    parent = _parent(tmp_path / "parent", data)
    with pytest.raises(BhsaParentFingerprintError, match="g_cons_utf8"):
        verify_bhsa_parent_feature_blobs(
            parent, parent_version="2021", expected_blob_shas=_expected(_SAMPLE)
        )


def test_mutated_mapping_feature_fails_with_pinned_expectation(tmp_path: pathlib.Path) -> None:
    parent = _parent(tmp_path / "parent")
    (parent / "qere_utf8.tf").write_bytes(b"@node\n@valueType=str\n\n1\ttampered\n")
    with pytest.raises(BhsaParentFingerprintError, match="qere_utf8"):
        verify_bhsa_parent_feature_blobs(
            parent, parent_version="2021", expected_blob_shas=_expected(_SAMPLE)
        )


def test_parent_symlink_is_rejected(tmp_path: pathlib.Path) -> None:
    real = _parent(tmp_path / "parent")
    alias = tmp_path / "alias"
    alias.symlink_to(real, target_is_directory=True)
    with pytest.raises(BhsaParentFingerprintError, match="symlink|real"):
        verify_bhsa_parent_feature_blobs(
            alias, parent_version="2021", expected_blob_shas=_expected(_SAMPLE)
        )


def test_required_feature_symlink_is_rejected(tmp_path: pathlib.Path) -> None:
    parent = _parent(tmp_path / "parent")
    feature = parent / "book.tf"
    feature.unlink()
    feature.symlink_to(parent / "chapter.tf")
    with pytest.raises(BhsaParentFingerprintError, match="book"):
        verify_bhsa_parent_feature_blobs(
            parent, parent_version="2021", expected_blob_shas=_expected(_SAMPLE)
        )


def test_directory_cannot_masquerade_as_feature(tmp_path: pathlib.Path) -> None:
    parent = _parent(tmp_path / "parent")
    (parent / "verse.tf").unlink()
    (parent / "verse.tf").mkdir()
    with pytest.raises(BhsaParentFingerprintError, match="verse"):
        verify_bhsa_parent_feature_blobs(
            parent, parent_version="2021", expected_blob_shas=_expected(_SAMPLE)
        )


def test_invalid_expected_fingerprint_rejected_before_any_parent_read(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    parent = _parent(tmp_path / "parent")

    def no_open(*args: object, **kwargs: object) -> None:
        raise AssertionError("malformed fingerprint should fail before reads")

    monkeypatch.setattr(os, "open", no_open)
    with pytest.raises((BhsaParentFingerprintError, ValueError), match="fingerprint|sha"):
        verify_bhsa_parent_feature_blobs(
            parent, parent_version="2021", expected_blob_shas={"otype": "garbage"}
        )


def test_verifier_uses_bounded_reads_not_path_read_bytes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    parent = _parent(tmp_path / "parent")

    def no_read_bytes(_self: pathlib.Path) -> bytes:
        raise AssertionError("unbounded Path.read_bytes forbidden")

    monkeypatch.setattr(pathlib.Path, "read_bytes", no_read_bytes)
    assert verify_bhsa_parent_feature_blobs(
        parent, parent_version="2021", expected_blob_shas=_expected(_SAMPLE)
    ) == _expected(_SAMPLE)


def test_parent_file_modified_during_streaming_is_rejected(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    parent = _parent(tmp_path / "parent")
    original_read = os.read
    changed = False

    def mutating_read(fd: int, size: int) -> bytes:
        nonlocal changed
        chunk = original_read(fd, size)
        if chunk and not changed:
            changed = True
            (parent / "otype.tf").write_bytes(b"@node\nCHANGED IN PLACE")
        return chunk

    monkeypatch.setattr(os, "read", mutating_read)
    with pytest.raises(BhsaParentFingerprintError, match="otype|changed|mismatch"):
        verify_bhsa_parent_feature_blobs(
            parent, parent_version="2021", expected_blob_shas=_expected(_SAMPLE)
        )


def test_verification_never_creates_or_modifies_parent_files(tmp_path: pathlib.Path) -> None:
    parent = _parent(tmp_path / "parent")
    before = {p.name: (p.stat().st_mtime_ns, p.read_bytes()) for p in parent.iterdir()}
    verify_bhsa_parent_feature_blobs(
        parent, parent_version="2021", expected_blob_shas=_expected(_SAMPLE)
    )
    after = {p.name: (p.stat().st_mtime_ns, p.read_bytes()) for p in parent.iterdir()}
    assert after == before
