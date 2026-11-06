# #134 — Scope-correct Sirach lexical elements

## Evidence
Real 46-file CCAT CI run 39384195281 (2026-10-20, PR #133) detected 8,119 typed Sirach witness markers across 7,565 alignments. 7,868 marker occurrences belong to MT-A, and the existing `row.mt_tokens` contains the exact marker spelling for **all 7,868**. A synthetic source row containing `[..] 7` produced a lexical token `7`, unlike a standalone `[..]` lacuna. The parser independently recognizes standalone witness labels (1–10) and lacking-in-witness `>n` as annotations but passes the same markup through `_mt_lexical_readings`.

The entire behavior is rooted in `_build_alignment` calling `_mt_lexical_readings(mt_col_a)` without Sirach/source context. The generic lexical reader skips known plus/minus/continuation/dot sigla but not the 1–10 witness labels or exact `>n` forms. Changing a generic regular expression across all books would silently lose real token evidence.

## Minimal design and fail-closed boundaries
- Only when the **canonical source** is `27.Sirach.par` and verse header is `Sir`, skip exact **whitespace-delimited** MT-A lexical tokens `1..10` and `>1..>10`. Do not globally strip bare numerals; do not remove embedded/ambiguous forms without their own researched source grammar.
- Continue decoding every witness and absence marker as a typed alignment annotation with raw spelling and original column scope. Keep all physical source lines, alignment IDs, `mt_raw`, `mt_col_a`, `mt_col_b`, witness annotations and source hashes unchanged.
- Do **not** reinterpret zero-MT rows automatically as additions. Existing exact Sirach `[..]` witness-lacuna rule may become applicable after genuine empty MT-A is exposed; other zero-side shapes remain unclassified unless independently justified.
- No word-specific witness links or inferred manuscript hands.
- Do not modify `mt_b` reconstruction, LXX lexical decoding, Qere/Ketiv, non-Sirach text, or source format source repairs.

## Gates
1. RED-first synthetic fixture for manuscript digits, `>n`, multi-label groups, lacuna and MT-B preservation, plus explicit non-Sirach negative control.
2. Minimal source-aware MT-A lexical filtering, leaving manuscript annotation decoder intact.
3. Focused parser/TF readback and technique tests (including previously known #52 and #60 shapes), then full Python matrix.
4. Re-audit ephemeral 27.Sirach.par against previous 8,119/7,868 witness counts; calculate after-fix marker leakage, zero-MT classes, and independently verify canonical lexical nodes. Update the 46-file gate only where before/after numbers are grounded in the real corpus, not by weakening assertions.
5. Exact-head release/CI + adversarial review challenging accidental numeric deletions, reference-marker collisions, unresolved zero-side transitions and source provenance. Merge only if all green.

## Research exclusions
The source `>12` partial-match risk is separately auditable: existing `_extract_annotations` matches `>1` inside `>12` because it lacks a digit boundary. This ticket does not grant permission to discard unvalidated attached or out-of-range notation. Keep such material visible and address it only with explicit RED coverage and source evidence.

## Empirical GREEN audit (full CCAT snapshot, 2026-10-20)

The first complete 46-file run after the source-sensitive lexical fix (PR #135,
CI 39386302504, head `a81a50d`) recorded **14,106** Sirach alignments,
**8,119** typed witness markers, unchanged manuscript counts (7,868 MT-A
and 251 MT-B), and **zero** witness label spellings retained in MT lexical
tokens (down from 7,868). The number of witness-bearing groups reporting
multiple MT tokens dropped from **7,312** to **1,293**. Groups with zero MT
tokens rose from **46** to **117**.

The same CI deliberately failed its historical full-corpus assertion:
unclassified translation-technique rows increased **31 → 102**. A separate
real-source transition comparison established the causal breakdown across
**7,396** alignments with changed lexical counts: **7,324** remain classified,
**43** become unclassified as Hebrew-empty/Greek-present, **28** become
unclassified because an LXX-minus marker has no surviving lexical MT, and
**one** remains an unresolved Sirach witness-lacuna conflict. The **net
increase of 71** is precisely 43 + 28, not 71 Greek additions.

All 71 newly unresolved technique judgments must stay visible rather than
being silently assigned `LXX+`, omission or lacuna. Full CI pins the
per-category transition counts and compares native `mt_element` totals
with an independently parsed source-to-TF count, replacing the obsolete
pre-repair count. Their textual-critical explanation remains research
issue #136; witness-to-reading links remain #132.

The newly unclassified groups preserve the stable source-derived
`catss_alignment_id`, MT-A raw text, annotation nodes and raw physical
line provenance. The unrelated unmarked empty MT row at Sir 19:14 is still
tracked in #60, and witness-to-reading links remain unverified under #132.
No original CATSS text or generated TF artifacts are stored here.
