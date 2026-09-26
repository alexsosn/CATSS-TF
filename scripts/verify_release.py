"""Verify that all software-release version surfaces agree."""

import importlib.metadata
import pathlib
import tomllib

import catss_tf

ROOT = pathlib.Path(__file__).parents[1]


def main() -> None:
    release_version = (ROOT / "release" / "VERSION").read_text(encoding="utf-8").strip()
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project_version = pyproject["project"]["version"]
    installed_version = importlib.metadata.version("catss-tf")

    versions = {
        "release/VERSION": release_version,
        "pyproject.toml": project_version,
        "catss_tf.__version__": catss_tf.__version__,
        "installed distribution": installed_version,
    }
    if len(set(versions.values())) != 1:
        details = ", ".join(f"{name}={value!r}" for name, value in versions.items())
        raise SystemExit(f"release version mismatch: {details}")

    tag = f"v{release_version}"
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    notes = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")
    if release_version not in changelog:
        raise SystemExit(f"CHANGELOG.md does not mention {release_version}")
    if release_version not in notes:
        raise SystemExit(f"RELEASE_NOTES.md does not mention {release_version}")

    print(f"release_version={release_version}")
    print(f"release_tag={tag}")


if __name__ == "__main__":
    main()
