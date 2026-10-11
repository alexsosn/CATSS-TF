"""Standalone CATSS corpus adapter for Agora's precreated empty staging output.

The native CATSS corpus writer requires an *absent* output path; Agora
creates a real empty staging directory before invoking a materializer.
Keep native validation and atomic build unchanged, and copy no corpora.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import shutil

from catss_tf.canonical_materializer import materialize_corpus

_PRIVATE_ARTIFACT = ".catss-agora-native-artifact"
_REQUIRED_NATIVE = frozenset(
    {
        "otype.tf",
        "oslots.tf",
        "otext.tf",
        "catss_alignment_id.tf",
        "catss-alignments.tsv",
        "catss-sources.tsv",
    }
)


def _check_inputs(source: pathlib.Path, output: pathlib.Path) -> None:
    if output.is_symlink() or not output.is_dir():
        raise ValueError("Agora CATSS output must be an existing real staging directory")
    if any(output.iterdir()):
        raise ValueError("Agora CATSS staging output must be empty")
    if source.is_symlink() or not source.is_dir():
        raise ValueError("CATSS source must be a real directory, not a symlink")
    source_real = source.resolve(strict=True)
    output_real = output.resolve(strict=True)
    if (
        source_real == output_real
        or source_real in output_real.parents
        or output_real in source_real.parents
    ):
        raise ValueError("CATSS source/output directories overlap")


def _validate_native(native: pathlib.Path) -> tuple[pathlib.Path, ...]:
    if native.is_symlink() or not native.is_dir():
        raise ValueError("native CATSS artifact must be a real directory")
    entries = tuple(sorted(native.iterdir(), key=lambda item: item.name))
    names = {entry.name for entry in entries}
    missing = _REQUIRED_NATIVE - names
    if missing:
        raise ValueError(f"native CATSS corpus missing required artifacts: {sorted(missing)}")
    for entry in entries:
        if entry.is_symlink() or not entry.is_file():
            raise ValueError(f"native CATSS artifact contains symlink or non-file: {entry.name}")
        if entry.suffix not in {".tf", ".tsv"}:
            raise ValueError(f"native CATSS artifact contains unexpected file: {entry.name}")
    return entries


def main(argv: list[str] | None = None) -> int:
    """Build one standalone corpus from a user-local source into Agora staging.

    Agora owns final promotion and network-denied sandboxing; native
    CATSS-TF remains authoritative for parsing, features and provenance.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        metavar="CODE",
        help="explicitly acknowledge a known CATSS parser diagnostic code; repeatable",
    )
    args = parser.parse_args(argv)

    source: pathlib.Path = args.source
    output: pathlib.Path = args.output
    _check_inputs(source, output)
    native = output / _PRIVATE_ARTIFACT
    published: list[pathlib.Path] = []
    try:
        # Native writer must see a missing destination, and will atomically
        # promote to its own private child of Agora's writable staging dir.
        if args.allow:
            materialize_corpus(source, native, allowed_validation_codes=set(args.allow))
        else:
            # Keep native's strict default for direct invocations.
            materialize_corpus(source, native)
        entries = _validate_native(native)
        for entry in entries:
            target = output / entry.name
            # No replacement: os.link fails if the host or a concurrent
            # writer created a destination after the empty-output precheck.
            os.link(entry, target, follow_symlinks=False)
            published.append(target)
        return 0
    except BaseException:
        for target in published:
            target.unlink(missing_ok=True)
        raise
    finally:
        if native.is_symlink():
            native.unlink()
        elif native.is_dir():
            shutil.rmtree(native)


if __name__ == "__main__":
    raise SystemExit(main())
