# Research — #96 scalar Greek references are not CATSS MT-verse targets

## Source/code audit (2026-10-10)

PR #47 at `ce974fef34965d33383334208cf568c7fb77fc71` writes one `reference` node per
`AlignmentRecord.lxx_references`. In `_add_detail_nodes()` it looks for a
`verse` node using `(source, reference.chapter or current_chapter,
reference.verse)`; if exactly one CATSS source-header verse has those numbers,
it writes a `catss_reference_target` edge to it. **The lookup ignores
`reference.subverse` and never verifies LXX text or the pinned LXX parent.**

The parser source `_GREEK_REFERENCE_VALUE` identifies scalar Greek reference
syntax (`[2]`, `[9:2a]`), while canonical `verse` nodes come from CATSS
source headers in the BHS/MT organization. Equal chapter and verse numbers are
not evidence that Greek and Hebrew textual sections coincide. An easy
counterexample is a synthetic `JoshB 9:2` with `[9:2a]`: the old writer
could attach a precise Greek *subverse* reference to the unqualified
`JoshB 9:2` header verse. It fabricates a typed relation even though the
latter carries no subverse identity.

Real-data grounding: the 46-file source audit on PR #47 (CI run
38060131630) counted 6,218 scalar Greek references and only one contextual
reference *range*. For Joshua B, CCAT places MT 8:30–35 at Greek 9:2a–f; the
pinned CenterBLC/LXX parent has no separately labeled subverse nodes a–f.
The code path above is independent of that pinned parent. Numeric
source-header lookup is therefore not a verified Greek destination resolver.

## Decision R96-1 — fail closed on semantic targets

Preserve the complete `reference` node, raw spelling,
`catss_ref_chapter`, `catss_ref_verse`, `catss_ref_subverse`, alignment
slot membership and source provenance. **Do not emit
`catss_reference_target` based only on matching a CATSS source-header number.**
This applies to all scalar references, including those lacking subverse
suffixes. Retaining the latter would still guess equivalence of two
different versification systems.

At present the canonical corpus does not know a uniquely grounded target
CATSS Greek-verse node. The code must have no fallback to an arbitrary MT
verse or to the Greek word nodes of a *different parent warp*. In this draft
canonical schema the edge was provisional and is not part of any published
release; omitting it is safer than publishing a false scholarly relation.
Query-native reference information and reference/alignment relations through
`oslots` remain available.

A future explicit resolver may add a separately documented
`catss_reference_target` relation only when its target identity has
source-independent grounding, with reference-versification coverage and
parent pin checks. Researching such a resolver and auditing the 6,218
references remains open under #96. This change only closes the concrete
false-positive edge writer on #47, not all of #96.

## Alternative rejected

Renaming the numeric coincidence to a 'reference target' of any kind would
mislead users into joining a Greek ref to a Hebrew source section. Numeric
lookup can be a **diagnostic candidate** in a future research report; it
must not be silently promoted into a semantic TF edge.

## Distribution

No CATSS, BHSA or LXX data are stored in the Git repository. Real-data
checks run only on user-acquired or ephemeral opt-in CI inputs.
