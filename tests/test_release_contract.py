import importlib.metadata
import pathlib
import tomllib

import pytest

import catss_tf
from catss_tf import cli

ROOT = pathlib.Path(__file__).parents[1]
RELEASE_VERSION = "0.1.0"


def test_package_and_distribution_versions_are_release_version() -> None:
    assert catss_tf.__version__ == RELEASE_VERSION
    assert importlib.metadata.version("catss-tf") == RELEASE_VERSION

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pyproject["project"]["version"] == RELEASE_VERSION

    assert (ROOT / "release" / "VERSION").read_text(encoding="utf-8").strip() == RELEASE_VERSION


def test_release_public_api_is_importable_from_package_root() -> None:
    assert callable(catss_tf.materialize_bhsa)
    assert callable(catss_tf.materialize_lxx)
    assert callable(catss_tf.compare_projection_bundles)
    assert catss_tf.TextFabricBhsaProvider.__name__ == "TextFabricBhsaProvider"
    assert catss_tf.TextFabricLxxProvider.__name__ == "TextFabricLxxProvider"


def test_cli_version_flag_reports_installed_version(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])

    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == f"catss-tf {RELEASE_VERSION}"


def test_text_fabric_is_an_explicit_optional_extra() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    extras = pyproject["project"]["optional-dependencies"]

    assert extras["tf"] == ["text-fabric>=13.1,<14"]
    assert "text-fabric>=13.1,<14" in extras["dev"]


def test_release_notes_and_changelog_name_the_release() -> None:
    assert "0.1.0" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "0.1.0" in (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")
