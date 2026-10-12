"""Agora's standalone native CATSS adapter: real tiny Text-Fabric round-trip and failure gates."""

import json
import os
import pathlib
import subprocess
import sys

import pytest
from tf.fabric import Fabric  # type: ignore[import-untyped]

from catss_tf import agora_adapter
from catss_tf.canonical_materializer import CanonicalMaterializationError

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _source(root: pathlib.Path) -> pathlib.Path:
    root.mkdir(parents=True)
    (root / "01.Genesis.par").write_text("Gen 1:1\n)B\tQEOS\n--+\tLOGOS\n", encoding="utf-8")
    return root


def _run(source: pathlib.Path, output: pathlib.Path) -> int:
    return agora_adapter.main([str(source), "--output", str(output)])


def test_agora_manifest_is_standalone_user_local_network_denied() -> None:
    manifest = json.loads((ROOT / "agora.materializer.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    assert manifest["plugin"]["id"] == "catss-tf"
    assert manifest["plugin"]["version"] == "0.1.0"
    assert manifest["plugin"]["repository"] == "alexsosn/CATSS-TF"
    assert len(manifest["materializers"]) == 1
    item = manifest["materializers"][0]
    assert item["id"] == "catss-canonical"
    assert item["acquisition"] == [
        {
            "type": "user-local",
            "path_type": "directory",
            "prompt": item["acquisition"][0]["prompt"],
        }
    ]
    assert "CATSS" in item["acquisition"][0]["prompt"]
    assert item["input"] == {
        "type": "directory",
        "required_globs": ["*.par"],
        "allow_symlinks": False,
    }
    assert "parent_input" not in item
    assert item["execution"] == {
        "type": "python-module",
        "module": "catss_tf.agora_adapter",
        "args": [
            "{source}",
            "--output",
            "{output}",
            "--allow",
            "invalid_lxx_reference",
            "--allow",
            "malformed_continuation",
            "--allow",
            "unsplit_row",
        ],
        "network": "deny",
    }
    assert item["output"]["format"] == "text-fabric"
    assert set(item["output"]["required_paths"]) == {
        "otype.tf",
        "oslots.tf",
        "otext.tf",
        "catss_alignment_id.tf",
    }
    assert "composition" not in item["output"]


def test_precreated_agora_output_produces_real_standalone_text_fabric(
    tmp_path: pathlib.Path,
) -> None:
    source = _source(tmp_path / "source")
    output = tmp_path / "staging"
    output.mkdir()  # Agora's actual host contract: preexisting empty directory.
    assert _run(source, output) == 0
    assert (output / "otype.tf").is_file()
    assert (output / "oslots.tf").is_file()
    assert (output / "otext.tf").is_file()
    assert (output / "catss_alignment_id.tf").is_file()
    assert any(file.suffix == ".tsv" for file in output.iterdir())
    assert all(file.is_file() and not file.is_symlink() for file in output.iterdir())
    assert not (output / ".catss-agora-native-artifact").exists()
    api = Fabric(locations=[str(output)], modules=[""], silent="deep").loadAll(silent="deep")
    assert api is not None
    assert api.F.otype.slotType == "alignment"
    assert api.F.otype.maxSlot == 2
    assert all(api.F.catss_alignment_id.v(n) for n in (1, 2))
    assert api.F.catss_lxx_plus.v(2) == 1


@pytest.mark.parametrize("variant", ["absent", "occupied", "symlink"])
def test_agora_output_must_be_real_precreated_empty_directory(
    variant: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _source(tmp_path / "source")
    output = tmp_path / "output"
    if variant == "occupied":
        output.mkdir()
        (output / "foreign.tf").write_text("user's data")
    elif variant == "symlink":
        outside = tmp_path / "outside"
        outside.mkdir()
        output.symlink_to(outside, target_is_directory=True)

    def _unexpected(*args: object, **kwargs: object) -> None:
        raise AssertionError("native materializer must not run")

    monkeypatch.setattr(agora_adapter, "materialize_corpus", _unexpected)
    with pytest.raises(ValueError, match="empty|real|staging"):
        _run(source, output)
    if variant == "occupied":
        assert (output / "foreign.tf").read_text() == "user's data"


@pytest.mark.parametrize("variant", ["same", "source-parent", "source-child", "source-symlink"])
def test_agora_rejects_source_output_overlap_and_source_symlinks(
    variant: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "root"
    source = _source(root / "input")
    if variant == "same":
        output = source
    elif variant == "source-parent":
        output = root
    elif variant == "source-child":
        output = source / "child"
        output.mkdir()
    else:
        link = root / "source-symlink"
        link.symlink_to(source, target_is_directory=True)
        source = link
        output = root / "staging"
        output.mkdir()

    def _unexpected(*args: object, **kwargs: object) -> None:
        raise AssertionError("native materializer must not run")

    monkeypatch.setattr(agora_adapter, "materialize_corpus", _unexpected)
    with pytest.raises(ValueError, match="overlap|symlink|empty"):
        _run(source, output)
    if variant == "source-child":
        assert list(output.iterdir()) == []


def test_agora_native_validation_failure_does_not_publish_partial_bundle(
    tmp_path: pathlib.Path,
) -> None:
    source = _source(tmp_path / "source")
    (source / "01.Genesis.par").write_text("Gen 1:1\nHB\tLOGOS {zzUNKNOWN}\n")
    output = tmp_path / "staging"
    output.mkdir()
    with pytest.raises(CanonicalMaterializationError, match="validation failed"):
        _run(source, output)
    assert list(output.iterdir()) == []


@pytest.mark.parametrize("forged", ["oslots-only", "symlink", "nested", "extra"])
def test_agora_rejects_forged_native_outputs_and_cleans_up(
    forged: str,
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _source(tmp_path / "source")
    output = tmp_path / "staging"
    output.mkdir()

    def malicious(_source: pathlib.Path, target: pathlib.Path) -> None:
        target.mkdir()
        (target / "otype.tf").write_text("otype")
        (target / "oslots.tf").write_text("oslots")
        (target / "otext.tf").write_text("otext")
        (target / "catss_alignment_id.tf").write_text("ids")
        (target / "catss-alignments.tsv").write_text("aligned")
        (target / "catss-sources.tsv").write_text("source")
        if forged == "oslots-only":
            (target / "otext.tf").unlink()
        elif forged == "symlink":
            (target / "escape.tf").symlink_to(source / "01.Genesis.par")
        elif forged == "nested":
            (target / "nested").mkdir()
        else:
            (target / "unexpected.bin").write_text("foreign")

    monkeypatch.setattr(agora_adapter, "materialize_corpus", malicious)
    with pytest.raises(ValueError, match="missing|symlink|unexpected"):
        _run(source, output)
    assert list(output.iterdir()) == []


def test_agora_partial_hardlink_failure_rolls_back_without_touching_source(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _source(tmp_path / "source")
    original = (source / "01.Genesis.par").read_bytes()
    output = tmp_path / "staging"
    output.mkdir()
    original_link = os.link
    count = 0

    def fail_second(
        source_file: os.PathLike[str] | str,
        target_file: os.PathLike[str] | str,
        *,
        follow_symlinks: bool = True,
    ) -> None:
        nonlocal count
        count += 1
        if count == 2:
            raise OSError("injected link failure")
        original_link(source_file, target_file, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(os, "link", fail_second)
    with pytest.raises(OSError, match="injected link failure"):
        _run(source, output)
    assert list(output.iterdir()) == []
    assert (source / "01.Genesis.par").read_bytes() == original


def test_agora_module_executable_entrypoint_exists() -> None:
    assert callable(agora_adapter.main)


def test_agora_python_module_subprocess_entrypoint(
    tmp_path: pathlib.Path,
) -> None:
    source = _source(tmp_path / "source")
    output = tmp_path / "staging"
    output.mkdir()
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "catss_tf.agora_adapter",
            str(source),
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, run.stderr
    assert (output / "otype.tf").is_file()
    assert (output / "catss_alignment_id.tf").is_file()
    assert not (output / ".catss-agora-native-artifact").exists()


def test_agora_no_replace_if_other_writer_claims_destination(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = _source(tmp_path / "source")
    output = tmp_path / "staging"
    output.mkdir()
    claimed: pathlib.Path | None = None

    def concurrent_claim(
        source_file: os.PathLike[str] | str,
        target_file: os.PathLike[str] | str,
        *,
        follow_symlinks: bool = True,
    ) -> None:
        nonlocal claimed
        claimed = pathlib.Path(target_file)
        claimed.write_text("FOREIGN")
        raise FileExistsError("concurrent claim")

    monkeypatch.setattr(os, "link", concurrent_claim)
    with pytest.raises(FileExistsError, match="concurrent claim"):
        _run(source, output)
    assert claimed is not None
    assert claimed.read_text() == "FOREIGN"
    assert sorted(output.iterdir()) == [claimed]


def test_agora_diagnostics_are_strict_by_default_and_explicitly_opt_in(
    tmp_path: pathlib.Path,
) -> None:
    source = _source(tmp_path / "source")
    # A physically unsplit row is a parser diagnostic, not an unknown
    # semantic siglum. The earlier [6x7] fixture had BOTH diagnostics,
    # correctly refusing to publish when only one was acknowledged.
    (source / "01.Genesis.par").write_text("Gen 1:1\nHBONLY\n", encoding="utf-8")
    output = tmp_path / "staging"
    output.mkdir()
    with pytest.raises(CanonicalMaterializationError, match="unsplit_row"):
        _run(source, output)
    assert list(output.iterdir()) == []

    assert (
        agora_adapter.main(
            [
                str(source),
                "--output",
                str(output),
                "--allow",
                "unsplit_row",
            ]
        )
        == 0
    )
    diagnostics = (output / "catss-diagnostics.tsv").read_text(encoding="utf-8")
    assert "unsplit_row" in diagnostics


def test_agora_known_diagnostic_allowance_does_not_mask_unknown_annotations(
    tmp_path: pathlib.Path,
) -> None:
    source = _source(tmp_path / "source")
    (source / "01.Genesis.par").write_text("Gen 1:1\nHB\tLOGOS {zzUNKNOWN}\n", encoding="utf-8")
    output = tmp_path / "staging"
    output.mkdir()
    with pytest.raises(CanonicalMaterializationError, match="validation failed"):
        agora_adapter.main(
            [
                str(source),
                "--output",
                str(output),
                "--allow",
                "invalid_lxx_reference",
                "--allow",
                "malformed_continuation",
                "--allow",
                "unsplit_row",
            ]
        )
    assert list(output.iterdir()) == []
