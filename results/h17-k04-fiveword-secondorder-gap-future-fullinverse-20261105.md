# K04 full 128-bit two-twist inverse: one missing-gap word and one future four-word block

**Agent 1 | 5 November 2026.** New complete, unmodified-original-target construction using native MT19937 recurrence. **No original K04 match; no physically authenticated coupon bits.** Six original slot components PASS, K04/K08 MISSING, combined REC8/1 INCOMPLETE.

## A smaller complete-donor geometry

The [second-order 31-bit four-sum](h17-k04-stagefree-secondorder-31bit-4sum-bridges-20261105.md) holds for any genuine native MT19937 stream:

```text
L(x) = ((x & 7fffffff) >> 1) XOR (9908b0df if x odd else 0)
(L(x[n-396]) XOR L(x[n-169]) XOR x[n] XOR x[n+454]) & bfffffff = 0
```

In the historically unproved but original-spool-compatible p951 chronology, selected attempt2 would occupy **x951..954**. The retained printer source has **x556..558** in intact row73 and **x782..785** in intact row104; selected row129 is completely withheld from these source constraints.

**New complete inverse:** Hypothetically assign any independent original **32-bit** source field to the single gap output **x555**, and any independent fourword source carrier to the future window **x1405..1408**. Then for i=0..3:

```text
x[951+i] = x[1405+i] XOR L(x[555+i]) XOR L(x[782+i]) XOR (bit_i << 30)
```

The source gives x556..558, x782..785 exactly, so only **five external future/gap output values**, plus **four independent bit30 choices**, suffice to synthesize the **entire** missing fourword coupon. This changes the donor geometry from the previous seven future outputs x1179..1181/x1347..1348/x1574..1575, and from our related [one-block plus selected-firstword copy](h17-k04-threeword-secondorder-oneblock-coupon-20261105.md). The construction **never decodes or uses the disputed selected 18:02 ACK2**.

The actual physical selected escrow bytes and original printer generator identity remain unproved. The generator assignment is a hypothesis tested against the untouched commitment.

## Original-source target test

- Original ZIP SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`; original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; recorder SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`.
- Future block source: all **532 surviving original 16-byte carrier groups** (selected ACK2 omitted before donor decoding), eight word-endian/MT-native/word-order views each: **4,256 distinct fourword assignments**.
- Gap x555 source: every CRC-good 32bit recorder control field, all 12 original RC-17 page strips (all historical revisions), and every word under eight interpretations of the six source-selected 16byte objects (WN14 K01, GOOD/HOLD K02 prehash, PTW K03 prehash, selected node49 K05, issued C K06, committed AX-7782 K07 prehash): **448 distinct native 32-bit values** after deduplication.
- Exactly **16** complete fourword coupon possibilities per donor pair, covering all bit30 decisions.
- For every original complete candidate, serialize the four recovered words as tempered little-endian 32bit output, XOR the original route mask `8556C8CB6140A7F9A5123AC7571BEE1C`, compare the full SHA256 against original unchanged K04 slot `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

**Original result: 4,256 × 448 × 16 = 30,507,008 complete K04 SHA256 assignments, zero matches.** Distinct assignments are not asserted to yield distinct final 16byte values.

**Five genuine CPython seeded producer positives PASS.** Seeds 0, 7, 1983, 20261003 and 0xDEADBEEF independently generated 1,409 native outputs. Withholding x951..954 and supplying genuine x555/x1405..1408, the inverse yields exactly the authentic complete selected native quartet once among its sixteen possible bit30 assignments, on each of 5/5 trials. This validates a true *complete-coupon* reconstruction geometry. It is independent of the copied selected ACK and of original K04 acceptance fitting.

Read-only original ZIP SFT: `h17_k04_secondorder_dual_source_fullcoupon_sft.py`, sharing only source-carrier extraction/MT functions with `h17_k04_secondorder_future_oneblock_sft.py`. All original source files, acceptance, official verifier, canonical candidate and masked coupon were untouched.

## Interpretation and next discriminating evidence

This is a **new fully target-reaching two-source MT inversion** requiring fewer authenticated future outputs than the prior seven-word algebra, and is able to use a single gap-word witness. It produces no original match among the specified recorded-carrier assignments, and no source record actually attests a common-MT generator, native positions x555 or x1405..1408, or the true historical selected physical coupon. Five hypothetical output words are not five newly recovered actual output words.

A subsequent meaningful advance would identify, from *original independent acquisition metadata*, a source field genuinely emitted at printer native stage555 and a source fourword block emitted at1405..1408, or find a different selected-stage producer bridge. Enlarging the same field menu without provenance should be weighed against genuinely different routes. The original K08 final keeper sentence remains unauthenticated and unresolved.