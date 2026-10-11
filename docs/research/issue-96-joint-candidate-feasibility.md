# R96-10 — bounded global feasibility of explicit Greek-reference surface candidates

## Grounded baseline

At main `f77436430648358eab7d78aeb861d2b9d47828a5`, `reference_surface_audit.audit_lxx_reference_surface_candidates` queries the exact CenterBLC/LXX parent span for each scalar `GreekReference`, normalizes Greek tokens and records half-open candidate word intervals. The complete 46-file pinned run in [38129496270](https://github.com/alexsosn/CATSS-TF/actions/runs/38129496270) reports 6,218 references, 4,349 single local occurrences, 232 of which overlap some other explicitly referenced alignment; 108 are pairwise unavoidable under *conditional* joint placement, while 124 have only optional pairwise overlap. Another 4,117 singles have no pairwise overlap. No semantic `catss_reference_target` edges are produced.

`lxx_resolver._solve_unique_assignment` already explores assignments for resolved mapping tasks but has distinct transposition-carrier semantics and operates on its own stricter per-document validated tasks. The diagnostic cannot copy its result as verified reference destinations: CATSS scalar reference syntax may be contextual, the diagnostic omits unreferenced rows and treats exact surface similarity as only candidate evidence.

## Scope: complete explicit-reference *candidate* groups

A group key is the CATSS `source_name` plus **exact pinned Greek parent** `(book, chapter, verse, subverse)`. Include every scalar reference from a supported CATSS source, even if the parent is missing or the tokens do not match, and deduplicate tasks only by alignment ID within that group (repeated scalar references still count separately in existing reference counters). Group outcome is:

- **incomplete** if *any* explicit-reference alignment in that group has no valid candidate interval because of missing/empty parent, no Greek lexical tokens, CATSS/parent normalization errors, or no exact surface match. Never relabel such a group `impossible` merely because a task was not validly modeled.
- **unique** if every alignment has candidates and exactly one complete, pairwise non-overlapping assignment is found by **exhaustive** bounded search.
- **multiple** if at least two distinct assignments are found (proof of ambiguity even if search is truncated).
- **impossible** if all tasks have candidates and exhaustive search finds no disjoint full assignment.
- **indeterminate** if a finite search budget is exhausted before two assignments or proof of exhaustion. Never equate a found singleton solution with unique if search was interrupted.

The group counts form an exact disjoint partition of `reference_groups`. Use deterministic task/candidate iteration, with a strict cap of 10,000 DFS states **per group**. A state is one recursive call; check the limit before exploring that state; if at least two solutions appear, stop early and report `multiple`. Count assignments over **one candidate per distinct alignment ID**. Overlap means `a.start < b.stop and b.start < a.stop`; adjacent words do not conflict. Multiple Greek references in one row to different keys are separate groups; same-key repeated refs deduplicate the task. Root groups with no actual matches are incomplete, not zero-task successes. Parent pin/metadata and no-subverse-fallback behavior are unchanged.

## Scientific limitations / integration

This is *conditional feasibility if all explicitly referenced candidate alignments in that group must be placed*; it does not incorporate implicit/default CATSS alignments, transposition exceptions, contextual reference meaning, cross-group constraints, or any CATSS↔LXX verified destination. Even `unique` is not proof of a semantic mapping. No parent word IDs, lexical texts or corpus copies are reported or committed. CI reads all 46 opt-in source files and pinned CenterBLC parent; record observed counts only after real run. Next #96 work must examine source semantics and a globally complete task model, not blindly map `unique` groups.

## Expected RED evidence

Synthetic pinned-provider fixtures: one local unique plus another same-key unique on disjoint words -> group unique; competing unique/unique same word -> impossible; locally ambiguous alternative that permits multiple global placements -> multiple; locally ambiguous alternatives all colliding with another unique -> impossible; valid tasks plus one missing/non-normalizable candidate -> incomplete; repeated scalar refs on one alignment not two tasks; sibling Greek parent subverse or distinct CATSS source remain separate; a very low search budget must return indeterminate rather than claiming unique/impossible. Test cap through a pure helper without creating massive corpora. Preserve 6,218 outer counts and 108+124=232 at pinned parent.
