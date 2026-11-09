# K04: all original seal-receipt four-word complete coupon assemblies

**Agent 4 | 9 November 2026 | Finished original commitment test with a planted positive**

## New complete-candidate mechanism

A physical ESC-N coupon could, as an unverified alternative to the damaged reconstructed printer ACK2 payload, consist of four original 32-bit maintenance serial words assembled through an internal issue/copy step. The original PTW receipt file contains 44 independent 4-byte serial fields, including 27 earlier singleton-permit receipts and 17 PTW417 revision receipts. This source family has a supported physical bay/serial order for K03, but **no document establishes it as an escrow-coupon producer**.

Unlike prior tests of the four *selected* PTW417 serials, or particular ticket-index combinations, this experiment permits **any ordered four distinct original 4-byte serials**, including historically unselected revisions, with an independent forward/reversed byte order for each word. All 16 bytes therefore come entirely from genuine evidence, without altering or fitting the disputed ACK2 copy. Apply the unchanged K04 XOR mask at the corresponding byte position and test the original full SHA256 commitment.

This tests **44×43×42×41×16 = 52,128,384 distinct complete 16-byte masked K04 candidates**. A direct unconstrained SHA256 preimage attack, custom pad, AES/PRNG variant, or arbitrary byte patch is outside this narrow assembly model. The original K04 commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Original complete result

The read-only original source file `evidence/maintenance/seal-receipts.jsonl` was SHA256-pinned at `c00944558636fbcc7e91b81e8e838ffd13fcd5a30d121b41951888766a8a0e32`. The portable [C++17/OpenSSL standalone reproducer](../agents/agent4/k04_all_44_seal_serial_quartet_sft.cpp) checks the pin, extracts exactly 44 serials, builds every eligible source-selected coupon, and hashes each complete candidate. Local equivalent execution completed:

```text
COMPLETE tested=52128384 target_hits=0 synthetic_positive=1 seconds=17.1142
```

The planted whole-coupon test uses existing original serial row indices (1,7,13,37) with independently specified per-word byte orientations (reverse, forward, reverse, forward). Its separately computed synthetic SHA256 full commitment is found **exactly once**, with the expected entire recovered 16-byte coupon. This is an execution positive, never a historical K04 acceptance.

## Interpretation

The tested all-serial four-word assembly family has **no complete accepted K04 value**. Four signed PTW417 AS_LEFT serials, single bay-state selectors, ticket-index substitutions and some source-fragment mosaics were already negative in prior research; this broader original 44-serial four-word support closes the precise remaining unfitted receipt-selection family.

Nothing here shows that printer and seal-receipt generators share a producer, that receipt words became physical coupon bytes, or that 52 million tested assignments measure cryptographic key recovery. The original selected K04 coupon remains absent. Original six PASS and K04/K08 MISSING, combined REC8 INCOMPLETE; official files, original route mask, verifier and canonical candidate are unchanged.

**Next useful model must explain an independently observed producer or complete copied physical object before allocating broader transformation searches.**