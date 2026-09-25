"""Command-line entry point for CATSS-TF."""

import argparse
import collections.abc

from catss_tf.source import CCAT_USER_DECLARATION_URL, download_parallel_source


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="catss-tf")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch = subparsers.add_parser(
        "fetch",
        help="download CATSS parallel files directly from the upstream CCAT host",
    )
    fetch.add_argument("destination", help="local directory for CATSS parallel .par files")

    return parser


def main(argv: collections.abc.Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "fetch":
        manifest = download_parallel_source(args.destination)
        print(f"CATSS parallel source ready: {len(manifest.files)} files")
        print(f"Upstream terms: {CCAT_USER_DECLARATION_URL}")
        return 0

    raise AssertionError(f"unhandled command: {args.command}")
