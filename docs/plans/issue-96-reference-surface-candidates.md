# R96-7 plan — candidate triage, not canonical destination edges

1. Source/code research and explicit non-mapping boundary:
   [research](../research/issue-96-reference-surface-candidates.md).
2. RED commit: fake pinned-provider tests for exact unique/multiple/zero
   Greek surface occurrences, missing/unsupported/unknown parents,
   Greek-empty references, and provider identity/subverse and fingerprint
   spoofing. Confirm pytest fails at deliberate stub after lint/mypy.
3. Implement read-only aggregate API in
   `src/catss_tf/reference_surface_audit.py`; call exact existing Greek
   surface normalizers, honor parent source-profile chapter offsets,
   cache repeated keys, reject inconsistent provider data; no mappings.
4. Add researcher-facing documentation and an opt-in complete 46-file
   snapshot gate using the existing exact pinned CenterBLC/LXX parent.
   Record observed counts, not guessed category frequencies; assert a
   disjoint partition totaling 6,218 references.
5. GREEN exact-head ruff check+format, mypy, 3.11–3.13 pytest, release
   smoke, whole 46-file Text-Fabric materialization/readback.
6. Independent adversarial review: test a unique token in a wrong parent,
   a repeated token, a malformed LXX word, a lettered reference absent
   in the parent, source/child aliasing, overlap/contextual-reference
   ambiguity. Any blocker returns to RED-first and then exact-head CI.
   Merge only as a research milestone; #96 remains open.
