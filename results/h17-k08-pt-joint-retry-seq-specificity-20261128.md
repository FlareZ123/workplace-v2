# K08 `PT` source-local locator: exact joint attempt-mask × chunk-order specificity

**Agent31 | 28 November 2026 | target-blind finite joint control, NOT recovered K08 wording.**

## Why the joint denominator matters

Agent2's original source program, `ATTEMPT TAILBIT LOW IF EVEN`, has a fully specified branch from the retained AX-7782 transfer checkpoint pairs to the two-byte word `50D4`. Removing each byte's high seven bits and checking even parity on the full bytes produces 7-bit ASCII **`PT`**, pointing through the note first-letter map to N16/N20 and their boundary phrase `do not`. The 13-word N20 semantic motif is not the author-final envelope caption; the actual K08 HMAC remains missing.

Previous controls considered source-ordered chunks under all 256 retry masks or source-selected retry mask `0xAA` under all 8! chunk orders. Those are **overlapping conditional families**. Their marginal rates cannot be multiplied: choosing a different attempt can change a chunk's 2-bit tail signature, after which reordering can sometimes restore the same exact output.

This report gives the **complete joint 4 × 256 × 8!** factorial, without assuming independence and without reading the K08 nonce, acceptance commitment or any proposed final caption.

## Exact source-preserving construction

Input is the original `resources/evidence/transfers/transfer-audit.jsonl`, SHA256 `32970ad4431a9d610cc12dcca2813f39dd8fd2e396f9e748dc94b5932cb69adf`. Enumerate all four transfer IDs, exactly eight sequences 0..7 per transfer and both retained attempt1 and attempt2 2-byte checkpoint values. For each transfer, choose any of **256** attempt masks and then any of **8! = 40,320** permutations of the eight *labeled* two-byte chunks. Take the low bit of each byte in concatenation order, pack the first into bit0, and decode the two 8-bit values using the original **even-parity, seven-bit uppercase-A-through-X** character rule. Count exact `PT` (packed bytes `50D4`). This preserves the checkpoint-pair boundary and the canonical LSB bit order; reversing bytes and bit order belongs to a separate earlier control.

The source-required original order is `seq0..7`; the proposed mixed retry operation's deterministic mask is `0xAA` (attempt1 on even seq, attempt2 on odd seq). It is **not** the official K07 receipt's greatest-attempt mask `0xFF`; those two rules must not be conflated.

## Combinatorial reduction, complete enumeration and controls

`50D4` splits into eight successive 2-bit chunk signatures in first-byte-first/LSB-first order. The target multiset has **three 00, zero 01, four 10, and one 11**. For a fixed transfer/attempt mask, an arbitrary permutation can yield exact `PT` **iff** the eight chosen chunks have precisely this multiset. For every such mask, exactly **3! × 4! × 1! = 144** permutations of eight individually labeled source chunks produce the required ordered `PT` signature (duplicate pair signatures account for multiplicity).

Enumerating all 256 actual binary attempt-choice masks for each transfer gives:

| Original transfer | Compatible masks / 256 | Exact PT outcomes among 256 × 40,320 |
| --- | ---: | ---: |
| AX-7778 | 0 | 0 |
| AX-7781 | 0 | 0 |
| **AX-7782** | **16** | **2,304** |
| AX-7783 | 0 | 0 |
| **Total** | **16 of 1,024** | **2,304 of 41,287,680** |

Thus the exact joint frequency is **1/4,480** conditional on AX-7782, or **1/17,920** across the full four-transfer/attempt/order factorial. This is a *combinatorial fraction of the specified counterfactual search space*, **not** an unconditional probability of Emily writing any particular final phrase. The multiset and exact mask counts provide a fast algebraic proof equivalent to explicitly iterating 41,287,680 cases.

The source-selected original `AX-7782, mask0xAA, seq0..7` is among these 2,304 hits. All three transfer controls yield zero. Earlier separate families independently found exact `PT` in **8/256** masks with the source sequence, and **144/40,320** sequences with mask0xAA. Multiplying those marginals would imply 1/8,960 conditional on AX-7782, which is **wrong by a factor of two**: the exact joint count is 1/4,480.

A source-only, SHA-pinned portable implementation with these frozen assertions, both marginal audits, and all four transfer controls is at [`agents/agent31/k08_pt_selector_multiplicity_sft.py`](../agents/agent31/k08_pt_selector_multiplicity_sft.py), committed in [`91518fc6`](https://github.com/FlareZ123/workplace-v2/commit/91518fc6cdfafc7e1b775fdd106aaa4776982dd3). The original bytes, K08 target, nonce, verifier and candidate are neither modified nor used for this count.

## Interpretation and required next result

This is evidence of a selectively structured **source-local locator** under an explicitly stated conditional operator family, not evidence of a particular historical text emitter. It rules out treating the two conditional control rates as independent. It also does not resolve whether the retrospective `ATTEMPT TAILBIT LOW IF EVEN` interpretation was historically intended. All possible output words from this route are **two uppercase note addresses**, not an author-final 10–20-word inscription. No accepted K08 component is gained.

The actionable missing operation remains a **complete deterministic source-authored editor** that emits precisely the envelope caption, plus an unchanged original K08 HMAC+SHA acceptance hit. Additional PT locator refinements are lower priority than that terminal recovery.
