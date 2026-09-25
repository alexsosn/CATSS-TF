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
