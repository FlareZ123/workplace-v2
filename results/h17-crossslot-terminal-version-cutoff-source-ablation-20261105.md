# H-17 cross-slot terminal-version capture: event-time cutoff and blind-latest falsifiers

**Priority correction (22:02 UTC):** Agent48's earlier 21:46 UTC broadcast, communications/broadcast/20261105T2146Z_agent48-terminal-version-ablation.md, had already falsified generic last-version deletion and naive latest-selection using K02/K03/K05/K06/K07, and independently identified the distinct missing K04-copy versus K08-text states. Credit this as **prior art**; the incremental source observation here is the *strict event-time cutoff contradiction* using explicitly normalized K02 time-zone offsets and the four matching 0x00000100 recorder CRC syndromes. No shared target recovery is claimed. The report was authored before I reviewed Agent48's broadcast.

**Agent18 | 5 November 2026 | Original source-only causal ablation.** This addresses the 20:23 Critic proposal of a possible shared final-version/capture loss at K04 and K08. The selected physical K04 coupon and Emily's author-final K08 caption are still unknown. The untouched official six accepted slots remain accepted; combined REC8/1 remains incomplete.

## Competing model and predeclared falsifiers

Model A: One shared **event-time snapshot cutoff** of the surviving export accounts for the loss of the selected ESC-N printer ACK2 at **3 Oct 2026 18:02 UTC**, with no later selected evidence available. This is a narrowly falsifiable global-clock model. An event's UTC timestamp is never presumed to equal physical random-value generation time.

Model B: One **source-agnostic latest-version dereference** recovers terminal values from their retained previous/draft versions. This differs from the original route's status-aware selectors. It must preserve independently accepted chosen objects before any missing-slot candidate is credible.

Neither model assumes that all record formats share a pseudorandom-number generator.

## Original-source decisive controls

| Object | Authentic chosen version and its surviving status | Consequence for a global rule |
| --- | --- | --- |
| K04 | PS-261003-0417, CLASS=RECOVER, ATTEMPT=2, ACK, **18:02:00Z**; copied payload A9A9DC5731A5E2AE879C47215C2559D5 **fails** original K04 commitment after the route XOR | The selected record exists as a *copy*; its physical-value integrity is unestablished |
| K02 | Eight accepted GOOD/HOLD greatest-revision DIAG_WORD readings, seq0..7, **21:13:40Z through 21:13:47Z**, 3 Oct; genuine prehash E1A5E474BAD7E853A2E8C71D3317D507, accepted reduced value 0D7E3AB56FB75DA3EB0E2E06786D239E | Actual selected, intact values **over three hours after** the K04 event survive the export |
| K05 | Four accepted CRC-valid node49/event82 seq300..303, all timestamped **21:14:02Z**, 3 Oct; authentic selected prehash FF8B78200A56E8586DCDA00EF01E4572 | Another four physically later selected values survive, independently of K02 |
| K06 | Revision C authorized, four SERVICE_ORDER strips **5DBF40EE52FAAED9A536D3326CF0D95A**; the later D-draft remains unissued | Blind latest revision would substitute the wrong object |
| K07 | Gabriel's signed COMMIT dry_run=false transfer **AX-7782**, prehash 8947CEDCB9CC73BAB7E87BE63302C5C9; later AX-7783 stopped before handoff | Blind greatest transfer identifier would substitute the wrong object |
| K08 | N02 and N06 are drafts; N17 and N18 are other-envelope labels; N23 and MAIL11/20 refer to Emily's final margin **without reproducing the chosen words** | The final record is an *unquoted text original*, with no independent timestamp or complete literal available for recovery |

**UTC control:** Four odd-numbered K02 seq records are encoded with local offsets, e.g. seq1 at 22:13:41+01:00, equal to 21:13:41Z. Parsing offsets is necessary; lexical timestamp sorting would incorrectly remove half the accepted K02 sequence.

Original evidence SHA256s:
- printer spool: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
- recorder: 5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba
- crew/desk notes: 13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb

The independent K02 and K05 source reducers remain reproducible under the unchanged original recovery-routing.json. These full selected inputs are already accepted by the unchanged original checker.

## New integrity detail and its limit

All four K05 CRC-bad records, exactly node49/event82 seq900..903 at 21:14:02Z, have the same retained checksum syndrome: **CRC32(record first20) XOR stored CRC32 = 0x00000100**. Each of the other 84 recorder rows has zero syndrome. The four stored CRCs differ from their recalculated checksums by exactly bit8 of the checksum field. This is consistent with a checksum-only taint, but does not authenticate the CONTROL data or identify the reason the bit was altered. Two of the bad-CRC controls already match 32/32 predicted MT source bits in Agent6's pre-existing node49 lattice (seq901 at native -320, seq903 at -314). The native matches are **prior art** and add no selected K04 information here.

## Decision

A single event-time cutoff before 18:02Z contradicts the preserved accepted K02 and K05 originals at 21:13 and 21:14Z. A universal naive latest-version substitution contradicts surviving accepted K06 and K07 objects. Therefore these two **specified source-wide export mechanisms are falsified** by independently authenticated later versions.

A narrower, media-specific handoff or stale-index operator remains possible, though no source yet determines it. K04's unverified copied bytes and K08's unquoted final words occupy different evidentiary failure states. Treating them as the same mechanism without an externally tested *whole-object* prediction would be retrospective pattern matching. Absent a new source-bound selection/copy law, move research toward distinct original physical coupon/capture provenance and the independently authenticated final caption source.

This is a causal-model decision only: it yields **no full K04 coupon** and **no verbatim K08 final caption**. No source, accepted candidate, mask, nonce, commitment or checker was modified.
