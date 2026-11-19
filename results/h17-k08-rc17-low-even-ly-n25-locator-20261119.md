# Conditional K08 N25 locator from RC-17 LOW-IF-EVEN footer bits

**Status:** exploratory cross-carrier locator hypothesis; not a recovered component and not an official K06 derivation.

## Question

Does the independently derived **LOW IF EVEN** selector produce a reproducible locator when applied to the naturally paired B/C/D revision strips in RC-17 service order?

This is deliberately a target-blind probe. It does not use the K08 commitment, candidate phrase guesses, or a K04/K08 verifier result to choose the selector.

## Source basis

Pinned source files (SHA-256):

| Source | SHA-256 |
|---|---|
| `resources/evidence/procedures/RC-17-scans.txt` | `a4b649fdbb6909115fb9505133012b5c1dda42141aafc1c6ec756199ddf1fc6d` |
| `resources/evidence/procedures/document-register.log` | `20d8dc63a28bab7084b6919207c50fb5bf957054f30b71c3ced0b3b5507e7f2c` |
| `resources/evidence/archive-labels.ini` | `146fa698f44bc9b9fa7a443d8dc71a2e23ff0f883dabd01512f8ade82d3666ad` |
| `resources/evidence/crew/noticeboard-and-desk-notes.txt` | `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb` |
| `resources/evidence/print/spool-reconstruction.log` | `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` |

The service order in `archive-labels.ini` is **DRAIN, ISOLATE, PURGE, VERIFY**. RC-17 supplies B, C, and D-draft footer strips for each stage. The document register says B was issued then withdrawn, C was issued and retained, and D-draft was review-only with no issue authority. The official K06 reducer therefore remains revision C; this experiment does not change it.

The LOW-IF-EVEN operator was established independently in the K05 retry analysis and the K08 N14 bridge. The K08 milk/stores analysis separately identifies the note cycle N13 → N09 → N12 → N11 → N13.

## Frozen selector and computation

Use zero-based service-order positions, matching the explicit 0–3 ordinal convention in the recorder-side LOW-IF-EVEN work:

- even positions 0 and 2: choose the lower revision, B;
- odd positions 1 and 3: choose the higher revision, D-draft.

This freezes the pattern **B,D,B,D** before inspecting the output. Concatenate the four 4-byte footer strips in service order, take each byte's least-significant bit, and pack the first extracted bit into output bit 0.

The reproducible script is:

`agents/agent35/k08_rc17_low_even_ly_n25_sft.py`

Run:

```bash
python agents/agent35/k08_rc17_low_even_ly_n25_sft.py
```

## Result

The selected raw footer bytes are:

`D82A73E99402F11A759E0027ED607B30`

The packed bytes are:

`4C59` → ASCII **LY**.

Under conventional one-based A1Z26, L=12 and Y=25, giving the candidate locator pair **N12 / N25**.

- N12 exists in the local note stack and is part of the independently derived K08 milk/stores cycle.
- N25 is absent: the local note stack contains N01–N24 only.
- The current missing-source intake identifies N25–N36 as absent caption sidecars.
- The next ordinal spool row, PS-261003-0325, exists at 09:05 as an ACK / RECOVER / store row. Its association with N25 is only an inferred continuation of the note/job ordinal alignment, not an authenticated foreign key.

## Controls and ambiguity

| Selection | Packed bytes | Interpretation |
|---|---:|---|
| B,D,B,D — frozen zero-based LOW IF EVEN | `4C59` | `LY` |
| D,B,D,B — one-based alternative | `F2D4` | non-ASCII |
| C,C,C,C — official K06 revision | `8345` | non-ASCII |
| B,B,B,B | `FCD9` | non-ASCII |
| D,D,D,D | `4254` | `BT` |

The A1Z26 interpretation is not explicitly stated in the source. A zero-based A=0 alternative maps LY to N11/N24 instead; both are present locally. Thus **N12/N25 is a conventional but unproven decoding**, not a confirmed locator. The result is also built from withdrawn B and unissued D-draft material, so it must not be represented as an authorized K06 component.

## Assessment

- **Reproducibility of B,D,B,D → LY:** high.
- **Interpretation LY → N12/N25:** conditional, low-to-moderate confidence.
- **Recovery status:** no K08 phrase, K08 component, K04 component, or recovery key recovered.
- **Canonical state:** unchanged. No acceptance commitment, verifier, or candidate file was modified.

## Promotion gate and practical next check

This locator is **not promoted** and must not change the current K08 priority. The existing downstream factorial endpoint null is explicitly conditional on the upstream CREW4/ALOWBIT front end; it does not include the author-label permutation null or N20 source-window null and is not a calibrated full-chain significance test. Until that full-chain benchmark is complete, do not prioritize N25, add PS-0325 to the intake list, or treat the A1Z26 interpretation as a source-authenticated selector.

If a full-chain benchmark later supports the upstream route, and an independently authorized local copy of the missing caption archive is supplied, N25 can be examined as a secondary hypothesis. PS-0325 native output should be considered only if the note/job ordinal alignment is independently established. Do not treat the 16-byte spool payload itself as caption text, and do not probe protected services or reopen the closed custodian inquiry.

This file preserves a reproducible exploratory observation, not a recommended new research branch.
