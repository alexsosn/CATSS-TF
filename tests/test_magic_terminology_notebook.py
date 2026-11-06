"""Offline RED-first notebook preflight and alignment-join tests."""

import ast
import json
import os
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, cast

import pytest

NOTEBOOK = Path(__file__).resolve().parents[1] / "docs/case-studies/magic-terminology.ipynb"


def _function(name: str, **extra: Any) -> Callable[..., Any]:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        for node in ast.parse("".join(cell["source"])).body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                ns: dict[str, Any] = {"Path": Path, "os": os, "defaultdict": defaultdict, **extra}
                exec(compile(ast.Module(body=[node], type_ignores=[]), str(NOTEBOOK), "exec"), ns)
                return cast(Callable[..., Any], ns[name])
    pytest.fail(f"missing required notebook function: {name}")


def test_no_embedded_corpus_outputs_and_code_compiles() -> None:
    cells = json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]
    code = [c for c in cells if c["cell_type"] == "code"]
    assert len(code) >= 9
    for cell in code:
        compile("".join(cell["source"]), str(NOTEBOOK), "exec")
        assert cell["execution_count"] is None and cell["outputs"] == []


@pytest.mark.parametrize("cwd", ("repo", "other"))
def test_module_paths_are_explicit_absolute_and_cwd_independent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cwd: str
) -> None:
    lxx = tmp_path / "catss-lxx"
    bhsa = tmp_path / "catss-bhsa"
    lxx.mkdir()
    bhsa.mkdir()
    work = tmp_path / cwd
    work.mkdir()
    monkeypatch.chdir(work)
    monkeypatch.setenv("CATSS_LXX_MODULE", str(lxx))
    monkeypatch.setenv("CATSS_BHSA_MODULE", str(bhsa))
    resolve = _function("require_module_directory")
    assert resolve("CATSS_LXX_MODULE", "catss-lxx") == lxx.resolve()
    assert resolve("CATSS_BHSA_MODULE", "catss-bhsa") == bhsa.resolve()


def test_module_paths_fail_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    resolve = _function("require_module_directory")
    monkeypatch.delenv("CATSS_LXX_MODULE", raising=False)
    with pytest.raises(RuntimeError, match="CATSS_LXX_MODULE"):
        resolve("CATSS_LXX_MODULE", "catss-lxx")
    monkeypatch.setenv("CATSS_LXX_MODULE", "generated/catss-lxx")
    with pytest.raises(ValueError, match="absolute"):
        resolve("CATSS_LXX_MODULE", "catss-lxx")
    wrong = tmp_path / "wrong-lxx"
    wrong.mkdir()
    monkeypatch.setenv("CATSS_LXX_MODULE", str(wrong))
    with pytest.raises(ValueError, match="catss-lxx"):
        resolve("CATSS_LXX_MODULE", "catss-lxx")
    monkeypatch.setenv("CATSS_LXX_MODULE", str(tmp_path / "catss-lxx"))
    with pytest.raises(FileNotFoundError):
        resolve("CATSS_LXX_MODULE", "catss-lxx")


def test_source_keyed_hebrew_index_is_linear_and_deduplicated() -> None:
    calls: list[int] = []

    class Otype:
        def s(self, kind: str) -> tuple[int, ...]:
            assert kind == "word"
            return (9, 2, 6)

    evidence: dict[int, list[dict[str, str | None]]] = {
        9: [{"source": "OG", "alignment_id": "id"}, {"source": "OG", "alignment_id": "id"}],
        2: [{"source": "Th", "alignment_id": "id"}, {"source": "OG", "alignment_id": "id"}],
        6: [{"source": None, "alignment_id": "id"}],
    }

    def membership_rows(_app: object, node: int) -> list[dict[str, str | None]]:
        calls.append(node)
        return evidence[node]

    app = SimpleNamespace(api=SimpleNamespace(F=SimpleNamespace(otype=Otype())))
    build = _function("build_hebrew_alignment_index", membership_rows=membership_rows)
    index = build(app)
    assert calls == [9, 2, 6]
    assert index == {("OG", "id"): (2, 9), ("Th", "id"): (2,)}

    lookup = _function("nodes_for_alignment", HEBREW_BY_ALIGNMENT=index)
    assert lookup("OG", "id") == (2, 9)
    assert lookup("Th", "id") == (2,)
    assert lookup("other", "id") == ()
