"""Execute documented installation commands without network access.

A shell-local pip stub records argv so these tests exercise the user's
copy/paste semantics rather than merely inspecting Markdown typography.
"""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

INSTALL_FENCES = (
    "README.md",
    "RELEASE_NOTES.md",
)


@pytest.mark.parametrize("document", INSTALL_FENCES)
def test_installation_fences_are_copy_paste_executable(document: str, tmp_path: Path) -> None:
    markdown = (ROOT / document).read_text(encoding="utf-8")
    sh_fences = re.findall(r"```sh\n(.*?)\n```", markdown, flags=re.DOTALL)
    install_commands = [
        fence for fence in sh_fences if fence.strip().startswith("pip install ")
    ]
    assert len(install_commands) == 2, f"{document}: expected two advertised installers"

    for command in install_commands:
        # There is deliberately no pip executable, download, or installed package:
        # shell expansion and argument boundaries are the entire user-facing contract.
        shell = "set -eu\npip() { printf '%s\\n' \"$@\"; }\n" + command + "\n"
        result = subprocess.run(
            ["sh", "-c", shell],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        assert result.returncode == 0, (
            f"{document}: documented installer failed as pasted:\n"
            f"{command}\n{result.stderr}"
        )
        arguments = result.stdout.splitlines()
        assert len(arguments) == 2 and arguments[0] == "install", (
            f"{document}: expected one pip install TARGET call, got {arguments!r}"
        )
        assert "CATSS-TF" in arguments[1], f"{document}: wrong install target"
