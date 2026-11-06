# R96-11 — fail closed on duplicate CATSS source filenames in Greek reference audit

## Grounding in live code and pinned data (2026-10-11)

On main `00e0a898e8f56bdf68b34ef8e5259deb1850c50c`, `src/catss_tf/reference_surface_audit.py` consumes an arbitrary `Iterable[ParallelDocument]`. Its interval and candidate-task scopes are `(document.source_name, exact LXX book, chapter, verse, subverse)`. It increments `source_files` once per document, but does not check whether each `source_name` uniquely identifies one input document. A different document bearing the same filename can therefore contribute references to the *same* group, producing ungrounded overlap or an erroneously impossible conditional assignment. Passing the same document twice also doubles scalar reference counters while group candidate intervals are deduplicated by stable alignment IDs: a false consistent-looking report.

The parser `parse_parallel_text` canonicalizes `source_name` to a filename with `pathlib.Path(source_name).name`; `alignment_id_for` combines source, verse header, source lines and raw lines. Different contents with the same source name can have different alignment IDs but still merge into the same audit group; identical contents can have exactly repeated IDs and be silently collapsed.

On the fully verified pinned 46-source snapshot ([run 38131308003](https://github.com/alexsosn/CATSS-TF/actions/runs/38131308003)), each of the 46 source names is one input file, and the 6,218 scalar reference outcomes partition correctly. Group outcomes are 326 unique, 70 multiple, 19 impossible, 256 incomplete, 0 indeterminate = 671. This milestone must not change these counts, canonical TF materialization, or the pinned-parent rules.

## Decision

Reject duplicate `document.source_name` values with a clear `ValueError` **before processing any references from the second occurrence**, irrespective of whether the source is supported, unknown, has lexical rows, or is empty. Use an `O(number of documents)` set of filenames while streaming the iterable. Do not auto-rename duplicates or treat each document as a distinct scientific source, because neither approach provides a reliable provenance contract for the existing public group key. Preserve the ability to audit any number of **distinct** source filenames, including two CATSS traditions sharing the same Greek parent reference (e.g. Ezra/Neh).

A duplicated source name is ambiguous provenance, not a Greek lexical normalization or placement problem, so raise rather than mark some groups incomplete. The error may mention the duplicate filename but must not include Greek source text or parent word IDs. The current audit's LXX parent fingerprint validation must still run before the provider is queried.

## RED-first and review gates

1. Two separate texts parsed with the *same filename* but different Greek strings targeting one pinned parent reference must raise; old code silently coalesces them.
2. Repeating the very same parsed document via an iterable generator must raise; old code doubles `scalar_references` and merges the identical task.
3. Even two empty documents with the same source name must raise; detection is per input document, not per explicit lexical alignment.
4. Two different filenames sharing the same LXX parent key remain two distinct groups; keep the existing Ezra/Neh test.
5. Confirm real full 46-source pinned audit and all existing R96-8..R96-10 counters unchanged, three Python matrices, Ruff, mypy, release smoke, canonical TF materialization/readback.

This deliberately does not implement verified CATSS reference destinations and leaves umbrella issue #96 OPEN. Avoid distributing upstream corpora.
