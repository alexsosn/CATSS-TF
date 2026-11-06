# Plan — issue #60 source-context evidence gate

1. Audit both exact source/verse pairs from the current 46-file CCAT
   snapshot using the installed parser. Confirm each physical empty
   MT-A row has no MT-B text, no transposition, no `[..]` witness marker,
   and a nonempty Greek lexical side.
2. Print the narrow local sequence of *structural* alignment metadata
   and source line numbers on either side; inspect source-level
   continuation markers and independently typed long plus/minus forms.
   Do not conflate absence of an MT word with a documented translation
   operation.
3. Compare 1 Esdras 4:25 against the long-plus documentation and
   Sirach 19:14 against #52's now pinned witness-lacuna predicate.
   Record positive and negative evidence and remaining unknowns.
4. **Research-only decision:** either leave these two rows explicitly
   unclassified with rationale, or split into separate behavior tickets
   if documentary evidence identifies defensible source semantics.
   No new permissive technique rule in this PR.
5. For each future behavior ticket: commit intentionally failing
   regression tests before production changes; run Ruff/mypy/pytest
   on 3.11–3.13, complete 46-file materialization/reload, user-facing
   docs and logically independent adversarial review before merge.
