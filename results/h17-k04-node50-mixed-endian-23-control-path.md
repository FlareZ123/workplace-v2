# H-17: a whole-state 23-control bridge with three hypothetical byte-order changes

**Agent 7, 3 November 2026.** This is an original-source **exploratory model construction**, not authentication of a recorder/printer writer or recovery of K04. [Read-only reproducible SFT](../agents/agent7/k04_node50_mixed_endian_stage_path_sft.py).

## New model and why it matters

[The two original full32 anchor falsifier](h17-k04-node50-two-anchor-stage-stratum-falsifier.md) shows no path through node50 seq25..41 using **identical** original CONTROL uint32 interpretation for all 17 records at monotone stage gaps4..40, including simultaneous original-printer GF2 consistency for consecutive values.

An alternative emitter/serialization theory interprets each record's **original CRC-valid CONTROL bytes unchanged** but allows the 32-bit value fed into hypothetical MT-state matching to be either its ordinary little-endian interpretation or the four-byte-reversed value. This introduces a discrete hidden serialization selector per record. No original record documents this switch. The objective of the test is to find out whether the earlier negative actually applies to this distinct architecture, and whether a restored full source-state bridge touches the missing printer coupon.

## Original-source exact result

Freeze original p951 hypothetical MT19937 printer timeline, with selected original 0417/ACK2 spool row129 omitted entirely. The 132 intact source packets fix rank **15365** of 19968 native state bits. Independent original recorder node50 anchors seq25 CONTROL at native index **−677** and seq41 at **−568** are both 32/32 already source-fixed.

An exact bounded-stage dynamic program, each original seq26..40 CONTROL allowed direct or byte-reversed views, returns:

| Allowed consecutive native stage gaps | Minimum reversed intermediate controls needed |
| --- | --- |
| 4..11 | No path |
| 4..13 | No path |
| 4..14 | **3** |
| 4..20 | **3** |
| 4..40 | **3** |

A full path at 4..14 uses exactly **seq28, seq34, seq35** in reversed byte order; every other original seq25..41 retains direct parsing. The concrete stage sequence (seq25..41) is:

`-677,-673,-666,-658,-652,-646,-640,-634,-630,-623,-609,-605,-598,-594,-585,-576,-568`.

Append the independent recently source-consistent **direct** seq42..47 positions `-563,-552,-545,-540,-531,-523`. A single exact full GF(2) source state accommodates all **23 original CRC-valid CONTROL values**, using the stated three reversed input interpretations, at joint rank **15927**. That is **562** equations beyond the intact printer basis, with zero contradictions.

**Target-facing outcome:** adding the entire 128-bit native selected coupon at p951..954 increases joint rank by **127**, leaving **127 free target bits**. The sole individually fixed native selected bit is `S[951].bit30`, the same conditional bit already identified by Agent49 from the hypothetical seq47 stage −523. This construction therefore recovers **zero independently authenticated original K04 bits**. It finds no complete K04 coupon and never checks the original K04 commitment.

The SFT verifies the original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, recorder SHA256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba`, all original node50 CRCs, minimal reversal count, exact joint rank and exact selected-bit quotient. It inherits a planted original-source whole-state no-reversal positive from the earlier bridge SFT.

## Why this remains exploratory

All chosen intermediate original stage positions are **retrospectively fit to their observed CONTROL values**. A per-record byte-order switch is an additional flexible parameter that increases model fit without a historical writer specification. The source recorder binary format is homogeneous and its individual CRCs are valid, so the reversals are an **interpretation of a hypothetical upstream emitter**, not observed byte corruption. Its credibility must be challenged against independently withheld source values and a concrete emitter/copy rationale. Published adjacent-stage recorder metadata rules already fail on some later records under their own CPython producer assumptions.

This experiment narrows exactly what the earlier uniform-direct contradiction establishes. It does **not** supersede it, independently select seq47 stage −523, prove a common historical generator, or raise the official 6/8 recovery count. A future writer theory should explain the three specific exceptional orientations without selecting them from the values being matched, then test unexamined historical records. K08's final original author words remain absent; combined REC8 acceptance is incomplete.
