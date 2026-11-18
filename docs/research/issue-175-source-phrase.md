# #175 — source-header-local lexical phrase search research

Baseline `main` at `7d0034c43b7cf16e71f29dcdce596ab6426cc0d8` (2026-11-19).

## Verified code and data model

- Canonical `_compile_graph` assigns `alignment` slots in source-document → verse-record → alignment-row order. `_add_detail_nodes` creates `mt_element` and `lxx_element` under exactly one alignment, preserving per-group `catss_index`. The 46-file CI asserts 349,670 alignments and 546,020 Greek elements on a loaded TF API. Slot numbers are local to a corpus build. Stable `catss_alignment_id` is for source provenance.
- Public `find_groups_with_ordered_forms` deliberately stops at a single alignment (as documented in `docs/libronix-coverage.md`). It cannot answer whether adjacent source-side lexical forms occur across two consecutive editorial alignment rows.
- The CATSS source headers `book/chapter/verse` are not guaranteed Greek destination coordinates. Greek references and variants are separate annotations. A scoped source-header-local lexical sequence is a narrower, defensible feature than a complete Libronix running-text index.
- MT column B is reconstructed/editorial and must not be inserted into MT-A lexical sequence. A source-side zero-token row contributes no lexical position and does not automatically break the displayed sequence. Users must be warned that this does not prove uninterrupted manuscript text or a cross-language word link.
- Repository tests build synthetic `.par` files, reload native TF and check actual source element order. The full 46-file job already reloads the canonical warp and can assert a source-parsed independent positional oracle with no licensed row output.

## Decision / scope

Implement a single streaming public `find_source_phrase_matches` for exact, case-sensitive **two-or-more** source-side spellings (one side per call), within consecutive identical `source, book, chapter, verse` slot runs. Return stable per-token `alignment_id` and 1-based `catss_index` plus the source/header, never cross-warp numeric pointers. Adjacent lexical tokens can cross alignment slots but not source/verse boundaries. Overlap and repeated spellings are supported. Explicitly fail if required native TF features are not loaded or inputs are invalid. Document product-limitation distinctions and do not claim lemma search, Libronix parity, reconstructive word links or cross-verse phrase continuity. No new query engine, index, CI workflow or proprietary fixtures.
