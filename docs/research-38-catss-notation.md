# Issue 38 research — CATSS notation semantics

## Evidence

The project owner supplied the explanatory text shipped with the Libronix/Lexham edition of the CATSS Parallel Aligned Hebrew-Aramaic and Greek texts. This is documentation evidence only; CATSS data are not copied into the repository.

The documentation distinguishes MT, reconstructed Hebrew source (column B), and LXX. It explicitly warns that several abbreviations can carry context-sensitive payloads naming the words or context involved. Therefore a bare boolean flag is not a complete representation for every notation family.

## Documented notation inventory

General CATSS notation documented by the supplied glossary:

- alignment/status: `+`, `{+}`, `{+?}`, `-`, `Ap+`, `Ap-`, `App`, `??`, `lo`;
- textual/editorial: `*`, `[..]`, `[ce]`, `g`, `[z]`, `t*`;
- reconstruction/language: `abbr`, `Aram`, `C`, `C´`, `ir`, `npr`, `trl`;
- sequence/transposition: `~`, `GTran`, `HTran`, `seq`, `Tran`, `tr`;
- segmentation: `div`, `join`, `sep`, `met`;
- translation technique: `act2pas`, `pass2act`, `pa`, `Dn`, `DR`, `Ety`, `EtyA`, `<fm`, `<l>`, `om`, `R`, `V`, `{d}`, `{d}tr`, `{p}`, `{XTM}`;
- prepositions: `pr`, `Pr`, `Pr?`, `Pr~`, `prp`, `prp+`, `prp-`;
- Qere/Ketiv: `Q`, `k-`, `q-`, `LXX=K`, `LXX=Q`;
- Samaritan comparison: `sp`, `sp~`, plus apparatus references of the form `<sp...>`;
- grammatical labels used by technique notation: `ad`, `aj`, `n`, `vb`;
- infinitive-absolute family: `I`, `I:+`, `I:-`, `I:--`, `I:ad`, `I:aj`, `I:n`, `I:na`, `I:nad`, `I:nd`, `I:nd+`, `I:ndd`, `I:p`, `I:p+`, `I:pc`, `I:pd`, `I:v`;
- contextual/reference: `els`, `v`.

`LXX` and `M` are glossary terminology, not annotation events by themselves.

## Sirach profile

Sirach reuses surface symbols with manuscript-specific meanings:

- `[]`: reconstructed letters;
- `[..]`: lacuna/illegible letters;
- `{}` and `{{}}`: manuscript addition;
- `>`: reading lacking in the cited manuscript;
- `*`: uncertain/fragmentary letter;
- witnesses `1..10`: Geniza/Masada/DSS witnesses as documented by the supplied glossary.

These meanings must not be assigned globally. In particular general `*` = asterisked passage conflicts with Sirach `*` = uncertain/fragmentary letter, and general `[..]` conflicts with the Sirach lacuna meaning.

## Design consequences

1. Keep a closed, typed notation catalogue. Unknown surface notation remains an unresolved validation failure.
2. Do not implement a catch-all `other`.
3. Record semantic family, stable kind, scope, and whether a notation can carry contextual payload.
4. Parser integration must preserve exact raw source markup.
5. Context-bearing notation needs structured payload in canonical IR before materialization.
6. Element properties belong on resolved parent nodes. Relations such as transposition/repetition/distribution must not be flattened into an unrelated global boolean when endpoints can be resolved.
7. Sirach symbol decoding is selected by book/profile.
8. Corpus-wide zero-unknown is an opt-in audit against user-acquired CATSS, not an offline CI fixture claim.

## Open empirical gate

The glossary describes the Libronix representation, while CATSS-TF parses raw CATSS `.par` files. A bounded inventory of a user-acquired raw CATSS snapshot is still required to map every Libronix label to its exact raw `.par` spelling and to prove zero unknowns. Offline tests may use only synthetic fragments.


## Raw `.par` empirical encoding layer

The raw CCAT dump does not use the Libronix display labels literally. Independent inspection of
the upstream files and the open CATSS parser research identifies these raw encodings:

- local/non-local transposition uses `^` / `^^^`, with wrapper forms `{..^TEXT}` and
  `{...TEXT}`;
- `{..dTEXT}`, `{..rTEXT}`, and `{..pTEXT}` carry distributive, repetition, and
  added-preposition payloads;
- MT strategy codes `.m/.s/.j/.w/.z` encode documented metathesis/separation/join/division/
  abbreviation, while longer dot codes such as `.kb`, `.rd`, and `.dr` encode interchange
  of cited letters and must retain those letters as payload;
- raw `{!}SUFFIX` encodes the documented infinitive-absolute family (`I:...`);
- column-B `%p-`, `%p+`, and `%p` distinguish omission, addition, and a general
  preposition/particle difference; `=+` marks a number difference;
- upstream Sirach contains `{t?}`, an uncertain transliteration form absent from the supplied
  display glossary.

The independent parser research also records corrupt/export-anomaly lines in the public dump.
Those are evidence for fail-closed validation, not permission to silently normalize source data.

## Audit status

Offline CI proves the decoder contracts on synthetic fixtures. The public upstream host is
intermittently timing out from automation, so a final corpus-wide zero-unknown claim is made only
after all 46 configured files are acquired and validated as one snapshot. A partial/cache-backed
inspection is useful for discovering RED cases but is not sufficient evidence for completion.
