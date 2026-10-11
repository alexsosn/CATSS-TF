# R96-12 — remove unbounded DFS frontier allocations in joint candidate audit

## Grounding (2026-10-11)

Current main `ece5fe5e3932facd03ba6546c61ef59106f14483`, `src/catss_tf/reference_surface_audit.py::_classify_joint_intervals`, uses a LIFO list `pending` of `(index, selected_intervals)`. On each popped state, before enforcing its next `max_states` check, it **appends one tuple per compatible candidate** at the next level. For a large list of candidate interval alternatives this front-loads the entire branch width and duplicates the selected interval prefix in every queued tuple. `max_states=1` still materializes all root children before reporting `indeterminate`. This contradicts the practical memory-bound inference a caller might make from `max_states`.

The exact pinned 46-CATSS-file and pinned CenterBLC/LXX run 38138723953 classified 671 Greek-reference groups (326 unique, 70 multiple, 19 conditionally impossible, 256 incomplete, zero budget-indeterminate), and 6,218 scalar references with 108 unavoidable/124 optional local overlap. These must remain unchanged. Existing RED/GREEN cases lock in behavior at budgets 1, 2, 3, multi-task impossible groups, and duplicate-source fail-closed.

## Proposed behavior

Replace eager branching with **iterative depth-first search using an iterator frame per active depth** and one mutable list of the currently selected candidate intervals. Keep exactly the same task ordering by `(candidate_count, alignment_id)` and candidate ordering lexicographically ascending; reject intersecting half-open intervals, allow adjacency. Count one visited state on entering root, and count a further visit exactly when entering an admissible child. If an unvisited child would exceed `max_states`, classify `indeterminate` (unless two solutions were already proven); when stack exhausts, 0 solutions => impossible, 1 => unique, 2 => multiple. A complete assignment selects one candidate per alignment. No recursive Python call depth.

The state/frame memory is `O(depth)` on top of the already existing `O(sum candidate counts)` deterministic sorted candidate tuples. The original caller inputs and candidate sort are not fundamentally memory bounded; document this distinction precisely. There is no raw source text, parent IDs, publication of provenance or semantic `catss_reference_target` mapping.

## RED fixture criteria

- Use `tracemalloc` **only inside a bounded unit test** after creating a one-task input containing ~80,000 distinct candidate offsets. At `max_states=1`, result must be `indeterminate` **without >4MB transient allocations**. Pre-change LIFO expansion builds ~80,000 eager `pending` tuple entries, violating this ceiling. New iterator DFS retains only sorted references and iterator frame.
- A reference small-tree oracle separately exhausts 0/1/2 solutions, including overlapping intervals, adjacent endpoints, mandatory conflict, mixed branching, and exact budget thresholds. This prevents a green memory improvement from silently changing classifications.
- A linear chain of >1,000 distinct disjoint candidates is unique without recursion overflow when enough visits are allowed. The previous implementation is also iterative; test preserves that guarantee.
- R96-12 must still pass all exact-head Python 3.11-3.13 Ruff/mypy/pytest, release smoke, pinned 46-file audit and full canonical Text-Fabric build/readback. Record observed counts, not forecasts.

## Interpretation

This is a pure performance/stability patch. The categories remain **conditional lexical candidate feasibility**, not proven Greek reference semantics. Issue #96 remains OPEN for source notation and implicit/nonreferenced alignment research.

## RED evidence

The preimplementation CI head `400a0e5008a0e3b8f4224e6fe7e94e5c08155394` reached pytest after successful Ruff, formatting and mypy on Python 3.13, [run 38143281953, test job 114481373664](https://github.com/alexsosn/CATSS-TF/actions/runs/38143281953). **1 expected failure, 490 passing tests**. The RED memory fixture measured **14,152,656 transient bytes** from the pre-change eager DFS with 80,000 one-word alternatives and `max_states=1`, versus the intended 4,000,000-byte peak ceiling. This is Python `tracemalloc` transient memory **after test input construction**, not total program RSS or parent corpus size. The other bounded-search parity and long-chain regression fixtures were already green on the pre-change solver.
