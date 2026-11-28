# K08: TAILBIT + LEN emits the first token of the independently selected N13

**Agent 5 | 28 November 2026 | target-blind emitter calibration; K08 remains unresolved**

## Question

The current frozen K08 selector reaches N09 and, from its five-word heading, sends the TAILBIT channel to N13 and the LEN channel to N23. The remaining problem is a complete text emitter. Before proposing another editor, can the already source-emitted literal operators `TAILBIT` and `LEN` demonstrably emit text that agrees with an independently selected terminal record?

## Frozen source construction

The existing K05–K07 sender union fixes the same fourteen-note set used by STOW14. Its post-label opening initials contain the literal seven-note `TAILBIT` run at N12,N13,N14,N17,N18,N20,N22.

Apply the two already-derived operators to exactly those seven records, packing the first selected record as the least-significant bit:

1. **TAILBIT:** take the ASCII low bit of each record body's final alphanumeric letter. The seven bits pack to **0x41**.
2. **LEN:** take the low bit of each complete post-label body character length. The seven bits pack to **0x74**.

Read in operator order TAILBIT then LEN, those two 7-bit ASCII outputs equal the complete first token of N13. Across all 24 source note bodies, **N13 is the only record whose first token equals that two-byte output**.

This is target-blind: the unchanged K08 nonce, HMAC and acceptance commitment are not read. N13 was already fixed independently by the frozen N09 heading calculation: its TAILBIT value is 12 and the existing LOW IF EVEN transition sends 12 to 13. Thus the emitted token was not used to choose the destination.

## What changes

This is the first direct calibration in the current N09→N13/N23 line where the source-local operator vocabulary emits literal text agreeing exactly with an independently selected destination, rather than only another note ID. It strengthens `TAILBIT`/character-`LEN` as a plausible text-emission mechanism and gives a concrete control any proposed complete emitter should preserve.

It does **not** emit the remaining author-final wording, does not establish that concatenating these operators was Emily's historical rule, and does not make the source-emitted four-word fragment a complete K08 candidate. A full deterministic emitter and terminal wording are still required.

Reproducer: [`agents/agent5/k08_tailbit_len_emitter_control_sft.py`](../agents/agent5/k08_tailbit_len_emitter_control_sft.py). It pins the original crew-note SHA, reproduces the seven-note run, verifies the two ASCII values and unique N13 first-token match, and deliberately never loads the K08 target or nonce.
