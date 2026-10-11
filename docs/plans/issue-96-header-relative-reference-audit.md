# R96-15 plan — own-header-relative Greek scalar reference counts

1. **Ground research:** compare Kingham's `Gen 23:5 → [6]` documentation with `GreekReference`, source `ParallelVerse` and the existing 46-source numeric inventory. Record the secondary-source limit and the exact three-way diagnostic classes *before implementation*. No request for unknown CATSS source semantics is promoted to a target.
2. **RED first:** extend `tests/test_reference_audit.py` with per-occurrence fixtures for same numeric, changed verse, changed explicit chapter (with and without a changed verse), subverse non-promotion, a contextual range excluded from scalar counts and repeated references. Assertions must fail at runtime against previous report contract. Keep original numeric-candidate checks.
3. **GREEN minimal:** add three report fields `same_header_numeric`, `different_verse_same_chapter`, `different_chapter` to `GreekReferenceAudit` and increment only inside the existing scalar loop. Validate partition equality; avoid changing corpus writers/resolvers and leave all old report fields untouched.
4. **Full snapshot:** in `.github/workflows/ci.yml`, assert `same+verse+chapter==6218` and preserve existing source/pinned-parent snapshot counters; report measured 46-source numbers. Only then pin actual numbers (never invent predictions). Validate the exact-head Python 3.11/3.12/3.13 pytest/Ruff/mypy, release smoke and full 46 CATSS source → canonical TF round-trip.
5. **Researcher docs:** add a concise source-only explanation and real counts to `docs/canonical-corpus.md`. Explicitly warn that source-header *coincidence* or *displacement* is not verified lexical mapping.
6. **Independent adversarial review:** at exact head, challenge counting a range as scalar, explicit chapter 0 being swallowed, double-counting chapter+verse difference, conflating source-local header match with *any* file header match, and source/corpus leakage. If a finding requires behavior change, record a RED test before fixing it, then re-run checks and re-review.
7. **Merge gating:** merge only after all five jobs green on reviewed commit; preserve #96 open and zero `catss_reference_target` edges.

## Observed corpus fixture

On pinned complete-source green run 38164945447, the new fields were exactly 24 / 6,188 / 6. The old numeric counts remained 1,749 / 4,433 / 36; use these as exact CI assertions in the final PR head. RED pytest, final exact-head matrix and logically independent adversarial review remain separate gates.
