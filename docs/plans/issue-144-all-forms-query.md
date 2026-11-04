# #144 — Multi-form canonical alignment query plan

1. **Behavioral RED:** create `tests/test_query_all_forms.py` with materialized+reloaded TF and independently exhaustive oracle; prove new public import/query is missing on test-only branch.
2. **Minimal GREEN:** add read-only `find_groups_with_all_forms` to `query.py`, export via `__init__.py`. Keep existing `find_aligned_groups` signature/behavior unchanged.
3. **Integration:** in existing full 46-file native TF step, use in-memory candidate lexical forms (no source text in logs) to compare against independent exhaustive corpus scan, then update docs.
4. **Gates:** exact-head Python matrix, complete 46-file source/TF/Agora, Context-Fabric, release smoke and separate failure-oriented review on final head. No inference of 1:1 correspondences or MT-B lexical identity.
