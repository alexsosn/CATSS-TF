# Plan — issue #52 typed Sirach witness-lacuna technique

Research: [issue-52-sirach-witness-lacuna.md](../research/issue-52-sirach-witness-lacuna.md).

1. **RED-first.** Add tests using the parser's existing Sirach 2:13
   `[..]\tOU)AI\\` pattern and `27.Sirach.par`:
   - zero-MT/Greek nonempty derived with addition and omission both false;
   - direct keyword technique predicate raises on contradictions
     (MT nonempty, Greek empty, LXX-plus, apparent minus);
   - source, column-A first marker, and annotation side all required;
   - `[]`, Greek-side `[..]`, and generic Hebrew-empty remain rejected;
   - Greek LXX mapped membership exposes a *scoped* witness-lacuna semantic
     and derives technique with no addition;
   - malformed/forged projection membership remains rejected.

2. **Implement after observed intentional RED.** Wire a narrowly scoped
   `sirach_witness_lacuna` boolean into shared deterministic technique
   derivation. Derive evidence using the parser's existing first-token
   column-A state and typed MT-A annotation in the *correct* source.
   Carry the semantic across to Greek memberships via an explicit
   narrow exception; use source+scope validation in the projection
   schema's technique derivation. Preserve sidecars format, stable IDs,
   raw data, and other corpus classes.

3. **Full 46-source regression.** Assert exactly 4,278 eligible
   Sirach `[..]` alignments, that each has a derived non-addition
   technique, and no unprofiled source gains acceptance. Confirm
   expected decline of unclassified rows from prior measured 4,305
   to 27 **only if actual source counts support it**. Do not guess
   unrelated source anomalies into the class.

4. **GREEN gates.** Ruff check/format, mypy, pytest on Python
   3.11/3.12/3.13, release smoke, pinned whole-corpus materialization
   and reload, and relevant projected real-data checks.

5. **Independent adversarial code/data review.** Re-read exact final
   diff without relying on implementation assumptions; try witness
   markers in wrong book/column and combined contradiction flags.
   Confirm no 4,278 false LXX-plus declarations or BHSA anchors.
   Address any finding by returning to RED then GREEN. Merge only
   after exact-head gates and documented review.
