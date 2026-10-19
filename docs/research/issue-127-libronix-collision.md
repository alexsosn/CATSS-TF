# Issue #127 — Libronix / Sirach notation collision

## Evidence and RED prediction

The owner's two 2003 CATSS Libronix introductions share the same glossary. In the general glossary, `*` signifies an asterisked passage, and `[..]` denotes unreadable Greek characters or Greek addition. In the Sirach section, the same spellings instead denote uncertain/fragmentary letters and a manuscript lacuna. These are book-sensitive, not two alternative labels for the same claim.

At `main@050ad956` the decoder in `src/catss_tf/notation.py` handles both meanings by `book`. But `documented_specs() -> {**_GENERAL, **_SIRACH}` has only one value per raw glyph, and `tf_schema._make_feature_specs` builds the list of declared semantic TF fields using only those values. The generic asterisk/lacuna meanings are consequently missing from `FEATURE_SPECS`. Full-source parser validation with zero unknown annotations does not test whether the projection's declared feature catalogue preserves every semantics.

## Plan and limits

A single schema-inventory regression enumerates all glossary raw keys under both `Ge` and `Sir`, checks unsuffixed / scoped / two-lane names, and thus requires both interpretations of the two collisions. Keep `documented_specs`'s by-glyph API unchanged; introduce a by-kind union dedicated to TF schema construction. Do not touch the parser, raw CATSS data, parent nodes or verse mapping. Re-run ordinary tests, full-corpus checks and an independent exact-head review before merge. #126 tracks the much broader end-to-end Libronix interface comparison.
