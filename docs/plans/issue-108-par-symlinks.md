# Plan — #108 direct-child CATSS source symlink safety

1. Establish explicit fixture tests in `tests/test_source.py`: inspection rejects in-root and escaping symlinks plus broken links; downloader rejects a symlink with/without overwrite while preserving its referent; a later-name symlink fails before the first network request; ordinary file tests stay green. Observe intentional pytest failures (RED) on unmodified production code.
2. In `download_parallel_source`, preflight all requested filenames (validity and `Path.is_symlink()`) before the per-file acquisition loop. Reject with `SourceDownloadError`. Keep atomic named temporary file staging.
3. In `inspect_parallel_source`, reject all direct-child `*.par` symlinks before `is_file()` filtering, including dangling symlinks. Raise `SourceInspectionError`; keep nonrecursive discovery and sorted manifest output.
4. Describe the explicit local-source policy in README and source docstring, including the allowed symlinked **root** and the concurrent-mutation limitation.
5. Validate exact-head pytest and static checks for Python 3.11/3.12/3.13, release smoke, and existing 46-file source/canonical TF readback. Independently re-review the exact diff and data/provenance invariants; new defects require another RED/GREEN cycle before merge. Close #108 only after verified merge.
