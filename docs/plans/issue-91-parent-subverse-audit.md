# Plan — issue #91 pinned-parent subverse mapping

1. Research actual Josh 9:2 TF verse node; list nested `subverse` nodes
   and their `F.subverse.v(node)` values, associated `word` slots and
   `orig_order`. Also inspect `F.subverse` values of those words.
2. Check whether the reference labels `a..f` are represented, and whether
   their mappings are unique. Record evidence or lack thereof.
3. If supported, add RED tests to `TextFabricLxxProvider` using parent-shaped
   fake TF API (feature on subverse nodes, not words), followed by a minimal
   implementation. Guard against duplicate/missing labels.
4. If unsupported, make the unresolved status explicit: keep raw structured
   range in canonical TF; return a typed missing-parent failure instead of
   inventing six memberships. Add a pinned-parent negative test.
5. Run all Python versions, complete 46-file audit and pinned parent on the
   **exact final head**, then conduct an independent adversarial review before
   any merge. Do not merge PR #89 on synthetic-only evidence.
