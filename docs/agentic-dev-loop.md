# Autonomous development loop

CATSS-TF uses an issue/PR-driven autonomous development loop.

## Per-ticket sequence

1. **Reconcile scope**
   - read the issue and acceptance criteria;
   - search for overlapping open PRs/issues;
   - identify dependencies and parent-version assumptions.

2. **Research**
   - inspect authoritative upstream code/docs/data contracts;
   - record evidence and unresolved assumptions;
   - keep live/data probes bounded and do not commit upstream datasets.

3. **Design/plan**
   - state the smallest implementation that satisfies the issue;
   - document mapping/failure behavior before coding;
   - update `design.md` or add an ADR for architectural changes.

4. **RED**
   - commit a deterministic failing test or fixture before production behavior;
   - the RED must fail for the intended reason.

5. **GREEN**
   - implement the smallest correct behavior;
   - run focused tests, then the relevant full offline suite.

6. **Documentation**
   - synchronize public commands, feature contracts, provenance, and limitations.

7. **Independent adversarial review**
   - review the exact final head in a logically independent context;
   - actively search for silent data loss, positional guessing, licensing leakage, and false-success states.

8. **Review fixes**
   - if a finding changes behavior, reproduce it with a RED first;
   - fix, rerun GREEN, and obtain re-review of the new final head.

9. **Merge**
   - merge only the reviewed exact head with all required checks green.

## Parallel work

Parallel agents may work on independent issues after prerequisites merge. They must not implement the same scope concurrently and must not modify shared architectural contracts without coordination.

## Network/data policy

Normal CI is offline. Real CATSS/BHSA/LXX integration tests, when added, must be explicit opt-in checks against user-acquired data and must not upload generated datasets as public artifacts.
