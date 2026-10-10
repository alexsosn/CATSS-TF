# Research — issue #59: column-B-only reconstruction carriers

## Source evidence and current parser contract

The current 46-file audit and issue #59 identify exactly **six** CATSS alignment records
with (i) no MT-column-A lexical `MtReading`, (ii) a non-null MT column B and
(iii) non-empty Greek lexical material:

| CATSS source | Verse | MT cell | Parser `retroversion_kind` |
| --- | --- | --- | --- |
| `12.2Sam.par` | 15:18 | `=;W/KL` | `context` |
| `12.2Sam.par` | 15:18 | `=;H/KRTY` | `context` |
| `12.2Sam.par` | 15:18 | `=;W/KL` | `context` |
| `12.2Sam.par` | 15:18 | `=;H/PLTY` | `context` |
| `17.1Esdras.par` | 9:33 | `=W/M/BNY` | `plain` |
| `44.Ezekiel.par` | 4:5 | `=v` | `vocalization` |

The *two* `=;W/KL` rows are distinct source records and must stay distinct,
not deduplicated by text. The exact neighboring contexts and equivalence to
parent lexical words have **not** yet been independently validated; issue #59
remains open for that separate analysis.

`src/catss_tf/parser.py` handles `=` by splitting column A and column B
(`_split_mt_columns`). It builds MT lexical readings using **only column A**
(`_mt_lexical_readings(mt_col_a)`) and separately sets
`retroversion_kind = _retroversion_kind(mt_col_b)`. The latter distinguishes
`;` as contextual reconstruction, `v` as vocalization and bare column B
as plain; hence `=v` cannot safely be advertised as a reconstructed Hebrew
*lexical word*. The graph writer currently allocates `mt_element` solely
from `alignment.mt_readings`, and stores column B only as a scalar
`catss_mt_col_b` on its alignment slot, with typed annotations when present.

The full 46-file canonical materialization in merged PR #47 showed
349,670 alignment slots, 350,219 genuine MT elements, 546,020 Greek elements,
and 4,305 unclassified techniques. This is correctly *lossless at the
alignment/raw-source level* but not independently queryable as a **typed
reconstruction carrier entity** when MT-A is empty.

## Design decision — typed carrier, not fabricated lexical element

Add one standalone `mt_b_carrier` node **only** for an alignment that has
`mt_count == 0`, `lxx_count > 0`, `is_lxx_plus == False`, and
a non-null `mt_col_b`. Greek-empty carrier/placeholder groups and
already-typed LXX-plus reconstructions are deliberately excluded. It receives the same single
`oslots` alignment slot, the **verbatim** column-B payload as
`catss_mt_b_raw`, and the parser's `catss_retro_kind`. It is not named
`mt_element`, has no `catss_text` pretending `=v` is a Hebrew word, and
does not map to a BHSA parent word or an LXX word. This isolates all six
source-grounded carriers as separate query-native entities. The original
group-level raw and status features remain unchanged.

All other (MT-A-bearing) column-B annotations remain scalar on their
alignment slots; this issue does **not** globally tokenize or reinterpret
column B. Individual lexical segmentation and counterpart relations require
separate upstream study and evidence, not a generic whitespace or prefix
stripper. Existing `derive_alignment_technique` remains strict; no
LXX-plus/addition/omission is inferred from a zero-MT count.

A plain TF node feature exposes raw and type without JSON or provenance
sidecar lookup; TF `L.u(slot, otype='mt_b_carrier')` reaches that node.

## Upstream/data boundaries

The source records above are present in issue #59; no whole CATSS text,
generated TF corpus, or third-party parent data is copied into this repo.
Normal CI uses small fragments only, and opt-in complete-CATSS CI must
assert exactly six carrier nodes, with their source distribution and
nonlexical status. The output remains a user-local derivative.

## R59-2 — real-data adversarial failure of an overbroad predicate

The first GREEN implementation included all MT-A-empty alignments with non-null
column B. Running the full 46-file audit on PR #97 at `b58829c`
reported **8,887** such nodes instead of the issue's six, which is
strong evidence that column B can occur on Greek-empty carriers too.
Therefore the first implementation must **not** be merged.

After adding a Greek-empty synthetic `=;W/KL\t---` RED regression on
`774f111`, Python 3.13 CI logged 416 passed / one intentional failure:
it emitted `mt_b_carrier` node 5 when none should exist.
The corrected scoped predicate requires non-empty *Greek lexical tokens*
(`lxx_count > 0`). The real snapshot still needs to establish that
this narrower criterion corresponds to the six issue-grounded rows;
do not assume it does until complete CI is green.

## R59-3 — explicit LXX-plus is a second distinct population

The second live 46-file gate at `56fdb712`, after requiring `lxx_count>0`,
still produced **8,879** carrier nodes, not the six exceptional rows.
The parser explicitly marks ordinary Greek-addition rows with
`is_lxx_plus=True` whenever MT column A begins `--+`, `-+`
or `---+`. Those rows can also have nonempty reconstruction column B;
their addition semantics are *already* query-native at alignment level
and must not be counted as exceptional unmarked reconstruction carriers.

The RED counterexample `Gen 1:1\n--+ =;W/KL\tLOGOS\n` was
committed as `5dbb2b3`. Its first exact-head Python 3.11 CI run
reported **417 passed and one intentional failure**, because the existing
writer created an unwanted `mt_b_carrier` on this LXX-plus row.
The corrected predicate therefore excludes `alignment.is_lxx_plus`.
No new Hebrew word or LXX-addition judgment is inferred by this change;
the actual source distribution must still be proven by the 46-file audit.
