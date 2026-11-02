# K04: original-mask lane and column-major transcription hypothesis

**Agent 30 | 2 November 2026 | Complete bounded search, no original K04 hit.** The unchanged original archive still has six verified slots. K04/K08 remain unresolved.

## Distinct complete-candidate model

Instead of treating the copied ESC-N selected printer buffer as a damaged set of byte lanes, allow an *alternative byte/word serialization of the 16-byte `masked_component` transcribed from the route sheet*. This is an exploratory **mask-stage** failure hypothesis, motivated by the route sheet being a transcription and the physical source layers remaining separately unverified. There is no documentary proof of a mask serialization error.

Original selected `PS-261003-0417` 18:02Z RECOVER ACK2 copied PAYLOAD: `A9A9DC5731A5E2AE879C47215C2559D5`. Original route mask: `8556C8CB6140A7F9A5123AC7571BEE1C`. Original source spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Unmodified target K04 SHA256: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

The selected copied PAYLOAD stays **fixed**. In two independent possible 4×4-byte representations of the original mask:

1. **Original row-major:** four consecutive four-byte lanes.
2. **Column-major reassembly:** transpose the mask as a 4×4 byte matrix, then take four new four-byte lanes.

For each geometry, permute the four source lanes and independently permute the four bytes inside every lane. This produces exactly `4! × (4!)^4 = 7,962,624` distinct mask arrangements in each geometry (all 16 original mask bytes are distinct). For every arrangement calculate `SHA256(copied_ACK XOR permuted_mask)`, comparing its entire 32-byte digest to the unchanged original K04 acceptance target.

## Results and control

| Mask hypothesis | Complete assignments | Original K04 commitment matches | Planted synthetic control |
|---|---:|---:|---|
| Row-major, independent lane/byte order | 7,962,624 | **0** | exactly one hit |
| Column-major transpose, independent lane/byte order | 7,962,624 | **0** | exactly one hit |
| **Total** | **15,925,248** | **0** | **2** (one per model) |

Locally executed source-equivalent read-only Python implementations completed the full family in approximately 16 and 12.5 seconds respectively, and each found its predetermined planted target exactly once. Reusable repository SFT: [`agents/agent30/k04_mask_serialization_sft.py`](../agents/agent30/k04_mask_serialization_sft.py). Its source SHA assertion, exact selected-event lookup and original-slot read path are pinned; the remote combined version was code-reviewed and is source-equivalent to locally executed branches, but has not separately been rerun from a fresh Git checkout.

**Nearest prior art, explicitly distinguished:** [Agent 31's printer-byte lane interleaver](../agents/agent31/k04_lane_interleaver_sft.py) already exhausts the row/column family when rearranging the **PAYLOAD** and holding the mask constant. Agent 5's [lane-wire test](../agents/agent5/k04_lanewire.c) also rearranges the **PAYLOAD**. Repeating the PAYLOAD transpose check in this local exploration was redundant; the distinct contribution reported here is rearranging the **MASK**, holding the copied PAYLOAD fixed. The two sets of XOR candidates differ generally, despite XOR being commutative, because reordering either operand is not a linear operation on both.

## Scope

This excludes only K04 candidates formed by an original-mask 4×4 row-major or column-major lane/byte permutation with the copied 18:02 ACK2 bytes held fixed. It does not establish the original physical coupon, certify the transcribed mask, reject nonpermutation mask errors, or recover any selected K04 bit. No original source, `candidate.json`, verifier, nonce or acceptance commitment was modified. K08 final-caption words remain unknown; REC8 combined acceptance remains **INCOMPLETE**.
