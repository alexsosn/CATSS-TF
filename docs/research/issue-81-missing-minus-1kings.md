# Research — issue #81 missing Greek-side minus at 1/3 Kgs 22:50

## Source evidence

Current CATSS source `13.1Kings.par`, 1/3 Kgs 22:50 contains this local sequence:

- `)MR -> EI)=PEN [16.28g]`;
- `)XZYHW -> --- [16.28g]`;
- `BN -> --- [16.28g]`;
- `)X)B -> [16.28g]`;
- `--+ =MLK -> O( BASILEU\\S [16.28g]`;
- `--+ =:Y&R)L -> ISRAHL [16.28g]`.

The Greek text of 3 Kgdms 16:28g has an unnamed “king of Israel” and does not contain
Ahaziah, “son”, or Ahab in that clause. Thus the MT phrase `)XZYHW BN )X)B` is absent
from Greek. CATSS already marks the first two elements as LXX-minus; only `)X)B`
lacks the expected `---`.

Primary source:
<https://ccat.sas.upenn.edu/gopher/text/religion/biblical/parallel/13.1Kings.par>

Greek comparison:
<https://theologianspress.org/bible/3kingdoms/16>

## Decision R81-1 — exact source repair

Treat the exact identity

`13.1Kings.par / 22:50 / )X)B / [16.28g]`

as semantic Greek `--- [16.28g]`.

Do not make reference-only Greek cells a generic minus spelling.

## Decision R81-2 — preserve source evidence

Keep unchanged:

- physical raw line;
- `mt_raw == ")X)B"`;
- `lxx_raw == "[16.28g]"`;
- source line(s);
- source-derived alignment id;
- typed contextual-reference annotation and payload.

Add the existing LXX-side `source_repair` provenance annotation with payload
`--- [16.28g]`.

The existing parser/technique machinery should then derive:

- `is_lxx_minus=True`;
- `mt_count=1`, `lxx_count=0`;
- `omission_vs_mt=True`;
- `addition_vs_mt=False`.

No technique exception is required.
