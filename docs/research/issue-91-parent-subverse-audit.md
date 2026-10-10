# Research — issue #91 real CenterBLC subverse hierarchy

## Actual failure

On PR #89 a pinned-parent audit of JoshB 9:2 range `[[9.2a-2f]]` reports:

```
[provider.get_span('Josh', 9, 2, label) for label in 'abcdef']
=> [None, None, None, None, None, None]
```

The actual parent is `CenterBLC/LXX`, `tf/1935`, commit
`f32a98eddf7eb239aa73ab863d70381e416d5076`.

The `otype.tf` blob categorizes distinct `subverse` nodes
`624943..655361`. The `subverse.tf` feature is sparse.
The production `TextFabricLxxProvider.get_span` currently filters candidate
word slots using `F.subverse.v(word) == label` and then seeks an upward
`subverse` node.

## Open factual questions

- What are the actual `subverse` parent nodes embedded in Josh 9:2, and
  what labels live on them?
- Are the letters `a..f` represented in the pinned parent at all?
- Is filtering the `subverse` feature on word slots valid for this dataset,
  or must it be read on `subverse` nodes?
- If the requested targets cannot be found, can structured CATSS semantics
  still be kept in canonical TF while the LXX projection fails closed?

## First gate

Use exact pinned parent from GitHub, not fixtures. Print the true TF
node hierarchy and features for Josh 9:2, but make no production changes
until the observed evidence supports a matching algorithm.

## Reproducible result — exact pinned-parent CI (2026-10-09)

CI run [38003177249](https://github.com/alexsosn/CATSS-TF/actions/runs/38003177249)
completed successfully against `CenterBLC/LXX@f32a98eddf7eb239aa73ab863d70381e416d5076`.
The real Text-Fabric API reported:

- `T.nodeFromSection(('Josh', 9, 2)) == 661339` (verse node);
- `L.d(661339, otype='word')` contains **191** word slots, `128883..129073`;
- `L.d(661339, otype='subverse') == (630920,)` — exactly **one** subverse node;
- `F.subverse.v(630920) == ''`, and `F.subverse.v(word) == ''` on every one of the 191 words;
- every word has `L.u(word, otype='subverse') == (630920,)`;
- `provider.get_span('Josh', 9, 2, label) is None` for every `label` in `abcdef`.

The CATSS range `[[9.2a-2f]]` is meaningful *in the CCAT source* but cannot
be mapped injectively to six LXX parent subverse nodes in this pinned edition.
This is **not** a bug in the provider's word-vs-subverse feature lookup:
the actual parent has no six labeled subverse nodes. Splitting the 191-word
subverse by ordinal or reusing node 630920 six times would fabricate source
semantics and corrupt query results.

**Decision P91-1:** preserve the typed range with raw spelling and provenance in
the canonical CATSS TF corpus. LXX projection must return the typed
`missing_lxx_reference_range_member` failure with zero memberships for this
alignment; never publish a partial or fabricated LXX module. A future parent
edition with explicit a–f structure can be supported after separately pinning
and revalidating that release.
