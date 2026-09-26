import pathlib
import subprocess

import pytest

from catss_tf import browser


def _write_feature(
    directory: pathlib.Path,
    *,
    projection: str,
    parent_repo: str,
    parent_version: str,
    parent_release: str,
    parent_commit: str,
    name: str = "catss_alignment_id.tf",
) -> pathlib.Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(
        "\n".join(
            (
                "@node",
                "@valueType=str",
                "@catssSchema=1",
                f"@catssProjection={projection}",
                "@catssSourceKind=catss-parallel",
                "@writtenBy=CATSS-TF",
                f"@parentRepo={parent_repo}",
                f"@parentVersion={parent_version}",
                f"@parentRelease={parent_release}",
                f"@parentCommit={parent_commit}",
                "",
                "1\tcatss:01.Genesis.par:test",
                "",
            )
        ),
        encoding="utf-8",
    )
    return path


def _bhsa_bundle(tmp_path: pathlib.Path) -> pathlib.Path:
    module = tmp_path / "catss-bhsa"
    _write_feature(
        module,
        projection="bhsa",
        parent_repo="ETCBC/bhsa",
        parent_version="2021",
        parent_release="v1.8.1",
        parent_commit="b112c161cfd21eae403d51a2733740d8743460e7",
    )
    return module


def _lxx_bundle(tmp_path: pathlib.Path) -> pathlib.Path:
    module = tmp_path / "catss-lxx"
    _write_feature(
        module,
        projection="lxx",
        parent_repo="CenterBLC/LXX",
        parent_version="1935",
        parent_release="v1.0.1",
        parent_commit="4829f3746c84d75576702498e75a68856358f289",
    )
    return module


def test_bhsa_browser_command_uses_exact_parent_app_and_local_module(
    tmp_path: pathlib.Path,
) -> None:
    module = _bhsa_bundle(tmp_path)

    spec = browser.build_browser_launch("bhsa", module)

    assert spec.argv == (
        "tf",
        "ETCBC/bhsa:v1.8.1",
        "--checkout=v1.8.1",
        "--version=2021",
        f"--locations={tmp_path}",
        "--modules=catss-bhsa",
    )
    assert spec.module_path == module.resolve()


def test_lxx_browser_command_uses_exact_parent_app(tmp_path: pathlib.Path) -> None:
    module = _lxx_bundle(tmp_path)

    spec = browser.build_browser_launch("lxx", module, noweb=True)

    assert spec.argv == (
        "tf",
        "CenterBLC/LXX:v1.0.1",
        "--checkout=v1.0.1",
        "--version=1935",
        f"--locations={tmp_path}",
        "--modules=catss-lxx",
        "-noweb",
    )


def test_path_with_spaces_remains_one_argv_element(tmp_path: pathlib.Path) -> None:
    parent = tmp_path / "modules with spaces"
    module = _bhsa_bundle(parent)

    spec = browser.build_browser_launch("bhsa", module)

    location_arg = next(arg for arg in spec.argv if arg.startswith("--locations="))
    assert location_arg == f"--locations={parent.resolve()}"
    assert spec.argv.count(location_arg) == 1


def test_bundle_projection_mismatch_is_rejected(tmp_path: pathlib.Path) -> None:
    module = _lxx_bundle(tmp_path)

    with pytest.raises(browser.BrowserLaunchError, match="projection mismatch"):
        browser.build_browser_launch("bhsa", module)


def test_bundle_parent_version_mismatch_is_rejected(tmp_path: pathlib.Path) -> None:
    module = tmp_path / "catss-bhsa"
    _write_feature(
        module,
        projection="bhsa",
        parent_repo="ETCBC/bhsa",
        parent_version="future",
        parent_release="v1.8.1",
        parent_commit="b112c161cfd21eae403d51a2733740d8743460e7",
    )

    with pytest.raises(browser.BrowserLaunchError, match="parentVersion"):
        browser.build_browser_launch("bhsa", module)


def test_mixed_feature_metadata_is_rejected(tmp_path: pathlib.Path) -> None:
    module = _bhsa_bundle(tmp_path)
    _write_feature(
        module,
        projection="lxx",
        parent_repo="CenterBLC/LXX",
        parent_version="1935",
        parent_release="v1.0.1",
        parent_commit="4829f3746c84d75576702498e75a68856358f289",
        name="catss_mt_n.tf",
    )

    with pytest.raises(browser.BrowserLaunchError, match="inconsistent CATSS TF metadata"):
        browser.build_browser_launch("bhsa", module)


def test_bundle_with_warp_feature_is_rejected(tmp_path: pathlib.Path) -> None:
    module = _bhsa_bundle(tmp_path)
    (module / "otype.tf").write_text("@node\n", encoding="utf-8")

    with pytest.raises(browser.BrowserLaunchError, match="warp"):
        browser.build_browser_launch("bhsa", module)


def test_empty_or_missing_bundle_is_rejected(tmp_path: pathlib.Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()

    with pytest.raises(browser.BrowserLaunchError, match="no catss_.*\.tf"):
        browser.build_browser_launch("bhsa", empty)

    with pytest.raises(browser.BrowserLaunchError, match="does not exist"):
        browser.build_browser_launch("bhsa", tmp_path / "missing")


def test_launch_browser_invokes_standard_tf_without_shell(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _bhsa_bundle(tmp_path)
    calls: list[tuple[tuple[str, ...], bool]] = []

    def fake_run(argv: tuple[str, ...], *, check: bool) -> subprocess.CompletedProcess[str]:
        calls.append((argv, check))
        return subprocess.CompletedProcess(argv, 7)

    monkeypatch.setattr(browser.subprocess, "run", fake_run)

    result = browser.launch_browser("bhsa", module)

    assert result == 7
    assert calls == [(browser.build_browser_launch("bhsa", module).argv, False)]


def test_missing_tf_executable_is_reported(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _bhsa_bundle(tmp_path)

    def fake_run(argv: tuple[str, ...], *, check: bool) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError(argv[0])

    monkeypatch.setattr(browser.subprocess, "run", fake_run)

    with pytest.raises(browser.BrowserLaunchError, match="Text-Fabric executable"):
        browser.launch_browser("bhsa", module)


def test_bundle_with_non_catss_tf_feature_is_rejected(tmp_path: pathlib.Path) -> None:
    module = _bhsa_bundle(tmp_path)
    (module / "foreign_annotation.tf").write_text(
        "@node\n@valueType=int\n\n1\t1\n",
        encoding="utf-8",
    )

    with pytest.raises(browser.BrowserLaunchError, match="non-CATSS TF feature"):
        browser.build_browser_launch("bhsa", module)
