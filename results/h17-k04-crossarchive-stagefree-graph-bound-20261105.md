# K04 crossarchive stage-free MT graph: conditional selected start 940..971

**Agent 17, 5 November 2026 | Source-pinned stage-index constraint; original K04 remains unknown.**

## Target-facing result

The original 132 intact printer source records excluding the selected 18:02 ESC-N ACK2 were interpreted as four native MT19937 output words each, in little-endian native-word order with inverse tempering. Agent13's 42 source-unindexed 31-bit predecessor-blind MT twist equations independently constrain 133 event starts, yielding 83 connected weighted components and a **conditional selected-row start interval 917..971** relative to the first printer record. The selected copied ACK payload is never decoded or admitted to these equations.

A separately retained *original* 16-halfword transfer **AX-7778** supplies a four-checkpoint match across printer source rows 34 and 64: original byte-swapped checkpoint halfwords `35AE 78FE 42DD FD35` at transfer positions 11..14 each match one of two source-derived tempered high16 predecessor possibilities for the corresponding printer lanes 0..3. From the exact MT predecessor identity this implies, **if the crossarchive link is a common continuous native-state emitter**, `s[64]-s[34]=227`. Inserting this one independently held source-to-source equation into the stage-free event graph eliminates 23 of its original 55 selected index choices, producing **selected start 940..971 inclusive (32 choices)**. Weighted components fall from 83 to82.

This is a nontrivial **stage bound**, with neither original physical selected coupon bits nor a recovered K04 component. It is stronger than testing the old p951 mapping against AX-7778 after presuming the stage indices, because the *entire event-index graph is re-solved from source-discovered relations with the extra crossarchive edge*. Prior work by Agent22 already independently identified the same original four AX checkpoints and row34/64 precursor correspondence; the new contribution is the conditional reduction of the event-index solution space, not a claim of newly acquired AX source.

## Additional original control cross-record graph relationships

A source-unindexed search considers 180 independent four-byte original CRC-good recorder CONTROL/AUX or RC-17 printed footer fields, four endian/native-tempered interpretations, and every ordered two-word printer pair drawn from distinct nonselected copied packets. For an unknown hidden earlier predecessor MSB, the 31-bit MT recurrence identifies a potential native-index separation of 227 between any paired middle/future full words, with their within-record lane offsets correcting the packet-start difference. Exactly eight original 31-bit source assignments survive the min-four-words-per-intervening-event chronology, collapsing to **four unique packet-start equalities**:

| Nonprinter original witness | First intact printer row | Later intact printer row | Exact proposed start difference |
| --- | ---: | ---: | ---: |
| TRP2 node50 seq70 CONTROL | 7 | 38 | 230 |
| TRP2 node49 seq201/990 CONTROL (alternate readings) | 9 | 40 | 229 |
| TRP2 node49 seq203/992/993 CONTROL (alternate readings) | 10 | 41 | 227 |
| RC-17 rev B VERIFY/PURGE footers | 28 | 59 | 226 |

Adding all four original relationships to the stage-free graph reduces connected weighted components **83→80**, but does *not* narrow its selected index interval. Inserting these four and the AX link jointly yields **79 components**, with **940..971** unchanged. The original RC-17 rev B and recorder value coincidences overlap prior Agent4 original cross-carrier MT studies, so reusing them as graph edges is a deductive synthesis of known original sources, rather than independent new numerical records.

The original nonselected spool SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Original transfer SHA256 `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`. For recorder fields the source CRC is checked on each record before accepting controls. Original selected ACK2, K04 mask, K04 SHA256, K08 nonce/caption, original verifier and candidate are never read in these graph computations.

## Reproducer and limits

**Committed original-source SFT:** [`agents/agent17/k04_crossarchive_stagegraph_sft.py`](../agents/agent17/k04_crossarchive_stagegraph_sft.py). It imports Agent13's existing source-unindexed 42-relation graph helper, parses the original evidence and independently recreates the AX four-halfword and 180-field wholeword source correlations before extending the weighted graph. It asserts the exact results:

```
printer_only=(917,971,83)
with_4byte_controls=(917,971,80)
with_AX=(940,971,82)
joint=(940,971,79)
```

[GitHub Actions original-data run 42092088856](https://github.com/FlareZ123/workplace-v2/actions/runs/42092088856) **completed SUCCESS on 5 November 19:15 UTC**, running exactly the committed SFT with no original evidence mutation. Local equivalent on the independently supplied unchanged ZIP material generated the same counts.

**The essential historical limitation:** the matching 31-bit predecessor identity was selected by searching many source fields and word pairs. Four AX high-halfword agreements are more specific than an isolated 31-bit match, and are consistent with an existing hypothetical p951 printer chronology, but no archived producer specification proves the printer emitted AX-7778 checkpoint values. Source timestamps and the AX drill's historical context do not establish a continuous stream. The 32 indices are feasible under **this necessary-equation graph**, not certified globally valid full-MT/copy-stage histories. Many different full native source states and physical paper coupons remain compatible with the selected location. In particular the original p951 generator source basis leaves the entire 128-bit selected quartet unobserved, and the AX-7778 halfword equations add **zero** source-to-target quotient rank (Agent32 prior). The new narrowed index alone does not fix a coupon byte or enable unqualified substitution into the K04 commitment.

Next mechanism should pair this narrowed index range with an independently indexed original *post-target* high-width donor, source-observed initializer or an event-specific copy-stage witness. An ordinary late-row copier buffer or another ordinary pretarget metadata correlation is not such a bridge.

**Recovery remains K01/K02/K03/K05/K06/K07 individually PASS; K04 and K08 MISSING; combined REC8/1 INCOMPLETE.**
