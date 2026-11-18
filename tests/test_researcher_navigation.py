"""A new researcher must find the runnable paths without implementation knowledge."""

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "docs/index.md"


def test_researcher_landing_page_is_discoverable_and_complete() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "[Researcher guide](docs/index.md)" in readme
    content = LANDING.read_text(encoding="utf-8")
    for required in (
        "canonical_research_walkthrough.py",
        "annotation_evidence_walkthrough.py",
        "unclassified_evidence_walkthrough.py",
        "catss-bhsa",
        "catss-lxx",
        "46-file",
        "Libronix",
        "not yet",
        "licensed",
        "synthetic",
        "source",
        "provenance",
    ):
        assert required in content, required


def test_researcher_landing_local_links_resolve() -> None:
    content = LANDING.read_text(encoding="utf-8")
    links = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", content)
    assert len(links) >= 9
    for link in links:
        if link.startswith(("https://", "http://", "mailto:")):
            continue
        path, _, anchor = unquote(link).partition("#")
        target = (LANDING.parent / path).resolve() if path else LANDING
        assert target.is_relative_to(ROOT), f"link escapes repository: {link}"
        assert target.is_file(), f"broken local link: {link}"
        if anchor:
            headings = re.findall(r"^#{1,6} +(.+)$", target.read_text(encoding="utf-8"), re.M)
            slugs = {
                re.sub(r"[^\w -]", "", h.lower()).strip().replace(" ", "-")
                for h in headings
            }
            assert anchor in slugs, f"missing heading anchor: {link}"
