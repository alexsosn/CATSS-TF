"""Command-line entry point for CATSS-TF."""

import argparse
import collections.abc

from catss_tf.parser import parse_parallel_file
from catss_tf.source import (
    CCAT_USER_DECLARATION_URL,
    download_parallel_source,
    inspect_parallel_source,
)
from catss_tf.validation import ValidationSummary, validate_documents


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="catss-tf")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch = subparsers.add_parser(
        "fetch",
        help="download CATSS parallel files directly from the upstream CCAT host",
    )
    fetch.add_argument("destination", help="local directory for CATSS parallel .par files")

    validate = subparsers.add_parser(
        "validate",
        help="validate local CATSS parallel files before parent-corpus mapping",
    )
    validate.add_argument("source", help="local directory containing CATSS parallel .par files")
    validate.add_argument(
        "--allow",
        action="append",
        default=[],
        metavar="CODE",
        help="explicitly allow a validation finding code; may be repeated",
    )

    return parser


def main(argv: collections.abc.Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "fetch":
        manifest = download_parallel_source(args.destination)
        print(f"CATSS parallel source ready: {len(manifest.files)} files")
        print(f"Upstream terms: {CCAT_USER_DECLARATION_URL}")
        return 0

    if args.command == "validate":
        manifest = inspect_parallel_source(args.source)
        documents = tuple(
            parse_parallel_file(f"{args.source}/{item.relative_path}") for item in manifest.files
        )
        report = validate_documents(documents, allowed_codes=set(args.allow))
        _print_validation_summary(report.summary)
        for finding in report.findings:
            location = (
                f"{finding.source_name}:{finding.line_no}"
                if finding.line_no is not None
                else finding.source_name
            )
            print(f"{finding.severity} {finding.code} {location}")
        return 0 if report.ok else 1

    raise AssertionError(f"unhandled command: {args.command}")


def _print_validation_summary(summary: ValidationSummary) -> None:
    print(f"source_files={summary.source_files}")
    print(f"verses={summary.verses}")
    print(f"alignments={summary.alignments}")
    print(f"source_data_lines={summary.source_data_lines}")
    print(f"accounted_lines={summary.accounted_lines}")
    print(f"unaccounted_lines={summary.unaccounted_lines}")
    print(f"parser_diagnostics={summary.parser_diagnostics}")
    print(f"unknown_annotations={summary.unknown_annotations}")
    print(f"invalid_alignment_ids={summary.invalid_alignment_ids}")
    print(f"duplicate_alignment_ids={summary.duplicate_alignment_ids}")
    print(f"error_count={summary.error_count}")
    print(f"unresolved_count={summary.unresolved_count}")
    print(f"ignored_count={summary.ignored_count}")
