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

## R96-2 — make the 6,218-reference inventory independently reproducible

After merged PR #47, the `catss` warp correctly preserves **6,218** scalar
Greek-reference nodes and **zero** speculative `catss_reference_target`
edges. A candidate lookup by chapter/verse can still be useful as an
*audited diagnostic*, but cannot be called a resolved Greek destination.

The existing parser IR exposes `GreekReference(chapter: int|None,
verse: int, subverse: str|None, raw: str)` and the source `ParallelVerse`
header chapter/verse. Comparing these labels is a *comparison of numbers
from different source organizations*, not a proof of corresponding text.
In particular:

- `[2]` inherits its *source header's* chapter for a diagnostic comparison;
- `[9:2a]` carries explicit chapter and Greek subverse, but the
  `JoshB 9:2` MT-header section cannot validate Greek `2a`;
- duplicates of MT-header chapter/verse across distinct physical headers
  are not distinct Greek destinations.

A **read-only reference inventory** should report the number of scalar
references, explicit chapters, subverse suffixes, and zero/one/multiple
numeric MT-header candidates per source. It must retain the distinction
between a *numeric candidate* and a verified LXX verse identity. This is
not permission to create `catss_reference_target` edges. The report
must contain only counts/distributions and no raw CATSS-derived corpus,
LXX text, or projected node IDs. It must accept user-local CATSS files,
require no default upstream network fetch, and work without BHSA/LXX.

The next, separate research step is to compare candidate cases with a
pinned Greek parent where full versification identity can be proven.
Given absent subverse nodes and changed numbering, some references will
remain unresolved. Fail closed, without fabricating subverses or marking
numeric matches as semantically validated.

## R96-3 — diagnostic API boundary

`catss_tf.reference_audit.audit_greek_references` accepts an iterable of
already parsed `ParallelDocument` objects, with no network or parent
corpus access. For each scalar Greek reference, it counts **physical**
CATSS source headers having the same chapter/verse label (using the current
source-header chapter for `[2]`, and an explicitly supplied chapter for
`[9:2a]`). It reports zero/one/multiple *numeric MT-header candidates*
plus counts of explicit chapter notation, subverse suffixes, and per-source
references.

A unique numeric candidate is **not** a verified Greek textual target:
the function creates no edges and never maps subverse suffixes onto
unnumbered CATSS section nodes. Counts are read-only research evidence
that can guide future pinned CenterBLC/LXX validation.
