"""Standard Text-Fabric browser launch integration for CATSS modules."""

import dataclasses
import pathlib
import subprocess
import typing

from catss_tf.bhsa_schema import (
    BHSA_CHECKOUT_COMMIT,
    BHSA_CHECKOUT_TAG,
    BHSA_REPOSITORY,
    BHSA_VERSION,
)
from catss_tf.lxx_schema import (
    LXX_RELEASE_COMMIT,
    LXX_RELEASE_TAG,
    LXX_REPOSITORY,
    LXX_VERSION,
)
from catss_tf.tf_schema import SCHEMA_VERSION, WARP_FEATURES

BrowserProjection = typing.Literal["bhsa", "lxx"]


class BrowserLaunchError(RuntimeError):
    """Raised when a CATSS module cannot be safely loaded into its parent TF app."""


@dataclasses.dataclass(frozen=True, slots=True)
class BrowserProfile:
    """Frozen Text-Fabric app/data contract for one CATSS projection."""

    projection: BrowserProjection
    app_ref: str
    checkout: str
    version: str
    parent_repo: str
    parent_release: str
    parent_commit: str


@dataclasses.dataclass(frozen=True, slots=True)
class BrowserLaunchSpec:
    """Validated standard Text-Fabric browser process specification."""

    projection: BrowserProjection
    module_path: pathlib.Path
    argv: tuple[str, ...]


@dataclasses.dataclass(frozen=True, slots=True)
class _ModuleMetadata:
    projection: str
    parent_repo: str
    parent_version: str
    parent_release: str
    parent_commit: str
    catss_schema: str
    written_by: str


_PROFILES: dict[BrowserProjection, BrowserProfile] = {
    "bhsa": BrowserProfile(
        projection="bhsa",
        app_ref=f"{BHSA_REPOSITORY}:{BHSA_CHECKOUT_TAG}",
        checkout=BHSA_CHECKOUT_TAG,
        version=BHSA_VERSION,
        parent_repo=BHSA_REPOSITORY,
        parent_release=BHSA_CHECKOUT_TAG,
        parent_commit=BHSA_CHECKOUT_COMMIT,
    ),
    "lxx": BrowserProfile(
        projection="lxx",
        app_ref=f"{LXX_REPOSITORY}:{LXX_RELEASE_TAG}",
        checkout=LXX_RELEASE_TAG,
        version=LXX_VERSION,
        parent_repo=LXX_REPOSITORY,
        parent_release=LXX_RELEASE_TAG,
        parent_commit=LXX_RELEASE_COMMIT,
    ),
}


def build_browser_launch(
    projection: BrowserProjection,
    module_directory: str | pathlib.Path,
    *,
    tf_executable: str = "tf",
    noweb: bool = False,
) -> BrowserLaunchSpec:
    """Validate a generated module and build the standard TF browser argv."""

    profile = _PROFILES[projection]
    module_path = pathlib.Path(module_directory)
    if not module_path.exists():
        raise BrowserLaunchError(f"CATSS module directory does not exist: {module_path}")
    if not module_path.is_dir():
        raise BrowserLaunchError(f"CATSS module path is not a directory: {module_path}")

    module_path = module_path.resolve()
    _reject_newline_path(module_path)

    warp_files = tuple(
        sorted(name for name in WARP_FEATURES if (module_path / f"{name}.tf").exists())
    )
    if warp_files:
        raise BrowserLaunchError(
            "CATSS module contains forbidden warp feature file(s): " + ", ".join(warp_files)
        )

    all_tf_files = tuple(sorted(path for path in module_path.glob("*.tf") if path.is_file()))
    feature_files = tuple(path for path in all_tf_files if path.name.startswith("catss_"))
    foreign_tf_files = tuple(
        path.name for path in all_tf_files if not path.name.startswith("catss_")
    )
    if foreign_tf_files:
        raise BrowserLaunchError(
            "CATSS browser bundle contains non-CATSS TF feature file(s): "
            + ", ".join(foreign_tf_files)
        )
    if not feature_files:
        raise BrowserLaunchError(f"CATSS module has no catss_*.tf feature files: {module_path}")

    metadata = tuple(_read_module_metadata(path) for path in feature_files)
    first = metadata[0]
    if any(item != first for item in metadata[1:]):
        raise BrowserLaunchError("inconsistent CATSS TF metadata across module feature files")

    _validate_metadata(profile, first)

    location = module_path.parent
    module_name = module_path.name
    if not module_name:
        raise BrowserLaunchError("CATSS module directory must have a non-empty name")

    argv = [
        tf_executable,
        profile.app_ref,
        f"--checkout={profile.checkout}",
        f"--version={profile.version}",
        f"--locations={location}",
        f"--modules={module_name}",
    ]
    if noweb:
        argv.append("-noweb")

    return BrowserLaunchSpec(
        projection=projection,
        module_path=module_path,
        argv=tuple(argv),
    )


def launch_browser(
    projection: BrowserProjection,
    module_directory: str | pathlib.Path,
    *,
    tf_executable: str = "tf",
    noweb: bool = False,
) -> int:
    """Launch the normal Text-Fabric browser with a local CATSS module."""

    spec = build_browser_launch(
        projection,
        module_directory,
        tf_executable=tf_executable,
        noweb=noweb,
    )
    try:
        completed = subprocess.run(spec.argv, check=False)
    except FileNotFoundError as exc:
        raise BrowserLaunchError(f"Text-Fabric executable {tf_executable!r} was not found") from exc
    return completed.returncode


def _read_module_metadata(path: pathlib.Path) -> _ModuleMetadata:
    headers: dict[str, str] = {}
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n\r")
            if not line:
                break
            if not line.startswith("@") or "=" not in line:
                continue
            key, value = line[1:].split("=", 1)
            headers[key] = value

    required = {
        "catssProjection": "projection",
        "parentRepo": "parent repository",
        "parentVersion": "parent version",
        "parentRelease": "parent release",
        "parentCommit": "parent commit",
        "catssSchema": "CATSS schema",
        "writtenBy": "writer identity",
    }
    missing = tuple(key for key in required if key not in headers)
    if missing:
        raise BrowserLaunchError(f"{path.name} is missing CATSS TF metadata: {', '.join(missing)}")

    return _ModuleMetadata(
        projection=headers["catssProjection"],
        parent_repo=headers["parentRepo"],
        parent_version=headers["parentVersion"],
        parent_release=headers["parentRelease"],
        parent_commit=headers["parentCommit"],
        catss_schema=headers["catssSchema"],
        written_by=headers["writtenBy"],
    )


def _validate_metadata(profile: BrowserProfile, metadata: _ModuleMetadata) -> None:
    expected = {
        "catssProjection": profile.projection,
        "parentRepo": profile.parent_repo,
        "parentVersion": profile.version,
        "parentRelease": profile.parent_release,
        "parentCommit": profile.parent_commit,
        "catssSchema": SCHEMA_VERSION,
        "writtenBy": "CATSS-TF",
    }
    actual = {
        "catssProjection": metadata.projection,
        "parentRepo": metadata.parent_repo,
        "parentVersion": metadata.parent_version,
        "parentRelease": metadata.parent_release,
        "parentCommit": metadata.parent_commit,
        "catssSchema": metadata.catss_schema,
        "writtenBy": metadata.written_by,
    }
    for key, expected_value in expected.items():
        actual_value = actual[key]
        if actual_value != expected_value:
            label = "projection mismatch" if key == "catssProjection" else f"{key} mismatch"
            raise BrowserLaunchError(f"{label}: expected {expected_value!r}, got {actual_value!r}")


def _reject_newline_path(path: pathlib.Path) -> None:
    rendered = str(path)
    if "\n" in rendered or "\r" in rendered:
        raise BrowserLaunchError("CATSS module path must not contain newline characters")
