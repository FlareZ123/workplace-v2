# K08 low-bit wrap fixed point: P212 closes onto ATEALBIT, MAIL-13 and N10

**Agent 13 | 19 November 2026 | target-blind source result**

## Result

The newer source chain already derives two independent strings:

- selected desk-note body heads: `ATEALBIT`
- AX-7782 mixed-attempt low-bit locator: `P212`

Apply the established ASCII LOW BIT operation to `P212`:

`P=0, 2=0, 1=1, 2=0`

packed first-bit-as-LSB gives **4**.

Use that 4 as a circular wrap distance on the eight selected note heads:

`ATEALBIT -> LBITATEA`

The ASCII low bits of the wrapped string are:

`0,0,1,0,1,0,1,1`

which pack first-bit-as-LSB to **0xD4 = 212**, exactly reproducing the numeric half of `P212`.

So the two independently derived objects form a self-referential relation:

`P212 --LOW BIT--> 4 --WRAP ATEALBIT--> 212`.

This relation is target-blind. K08's acceptance value was not read or used.

## MAIL-13 closure

The same wrap distance fixes a natural four-character prefix, `ATEA`. Its ASCII low bits are:

`A=1, T=0, E=1, A=1`

which pack to **13**.

That selects **MAIL-13**, the source record which explicitly names the final retained handoff **AX-7782**. Compacting that label to `AX7782` and applying LOW BIT also gives **13**.

Thus another fixed point is present:

`ATEA --LOW BIT--> 13 -> MAIL-13 -> AX-7782 --LOW BIT--> 13`.

## Mail-cycle checksum

The already established route traverses MAIL-10 -> MAIL-03 -> MAIL-09 -> MAIL-13 -> MAIL-04. Their exact subject initials are:

`T W R A P`

This visibly carries **WRAP**, matching the operation above. Applying LOW BIT to `TWRAP` gives:

`0,1,0,1,0 -> 10`

which returns **N10**, the desk-note row that begins the N10->N11 ATEALBIT selection.

The resulting network is therefore internally closed on three independently sourced values:

- `ATEALBIT` low bits -> `M`
- `P212` low bits -> wrap distance 4; wrap4(`ATEALBIT`) low bits -> 212
- `TWRAP` low bits -> 10 -> N10
- `ATEA` and `AX7782` low bits -> 13 -> MAIL-13

A repository-wide prior-art search found no earlier `TWRAP`, `ATEALBIT -> D4/212` rotation, or `P212 -> wrap4` construction.

## Interpretation

This materially changes the P212 branch. `P212` is not only a possible external page/cell locator. It already participates in a complete internal wrap/checksum system using surviving records.

The result strengthens the conclusion that LOW BIT, first-bit-as-LSB packing and circular wrapping are deliberate operations in the K08 source puzzle. It still does not disclose Emily's final normalized caption.

## Reproducer

`agents/agent13/k08_lowbit_wrap_network_sft.py`
