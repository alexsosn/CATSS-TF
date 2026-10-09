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
