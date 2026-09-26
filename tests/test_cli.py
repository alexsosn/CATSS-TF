from pathlib import Path

import pytest

from catss_tf import cli
from catss_tf.source import ParallelSourceManifest


def test_fetch_command_invokes_downloader(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    destination = tmp_path / "parallel"
    seen: list[Path] = []

    def fake_download(path: str | Path) -> ParallelSourceManifest:
        seen.append(Path(path))
        return ParallelSourceManifest(files=())

    monkeypatch.setattr(cli, "download_parallel_source", fake_download)

    assert cli.main(["fetch", str(destination)]) == 0
    assert seen == [destination]
    assert "CATSS parallel source ready" in capsys.readouterr().out


def test_validate_command_reports_scalar_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "01.First.par").write_text("Test 1:1\nHB\tGR\n", encoding="utf-8")
    (tmp_path / "02.Second.par").write_text("Test 1:1\nHB2\tGR2\n", encoding="utf-8")

    assert cli.main(["validate", str(tmp_path)]) == 0

    output = capsys.readouterr().out
    assert "source_files=2" in output
    assert "alignments=2" in output
    assert "error_count=0" in output
    assert "unresolved_count=0" in output
    assert "ignored_count=0" in output


def test_validate_command_fails_on_unresolved_markup(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "01.First.par").write_text(
        "Test 1:1\nHB {zzUNKNOWN}\tGR\n",
        encoding="utf-8",
    )

    assert cli.main(["validate", str(tmp_path)]) == 1

    output = capsys.readouterr().out
    assert "unresolved_count=1" in output
    assert "unresolved unknown_annotation 01.First.par:2 raw={zzUNKNOWN!r}" in output


def test_validate_command_can_explicitly_allow_a_finding_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "01.First.par").write_text(
        "Test 1:1\nHB {zzUNKNOWN}\tGR\n",
        encoding="utf-8",
    )

    assert (
        cli.main(
            [
                "validate",
                str(tmp_path),
                "--allow",
                "unknown_annotation",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "unresolved_count=0" in output
    assert "ignored_count=1" in output
    assert "ignored unknown_annotation 01.First.par:2" in output


def test_browse_command_forwards_projection_module_and_noweb(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = tmp_path / "catss-bhsa"
    module.mkdir()
    seen: list[tuple[str, Path, bool]] = []

    def fake_launch(projection: str, module_path: str | Path, *, noweb: bool = False) -> int:
        seen.append((projection, Path(module_path), noweb))
        return 9

    monkeypatch.setattr(cli, "launch_browser", fake_launch)

    assert cli.main(["browse", "bhsa", str(module), "--noweb"]) == 9
    assert seen == [("bhsa", module, True)]


def test_validate_complete_rejects_partial_snapshot(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "01.Genesis.par").write_text("Gen 1:1\nHB\tGR\n", encoding="utf-8")

    assert cli.main(["validate", str(tmp_path), "--complete"]) == 2

    output = capsys.readouterr().out
    assert "complete_snapshot=false" in output
    assert "missing_source_files=" in output
