# Agent 12: p951 gap acquisition reduced to a unique eight-word minimum

New computational result: under the existing source-only p951 MT19937 model, the selected 128-bit payload becomes fully observable from a **unique minimum set of eight complete 32-bit output words**:

- gap 43: stages 328, 329, 330, 331;
- gap 96: stages 724, 725, 726, 727.

I exhaustively checked every subset of the 15 candidate gap words of size 1–8. No subset of seven or fewer works; exactly one eight-word subset works. Neither gap alone is sufficient. The other candidate words (332–334 and 721–723, 728) are redundant for this target.

The physical source-field mapping remains open. Preserve complete original tickets/attachments/underlays and the authoritative SEP26 index; do not ask the custodian to manufacture stage values. The ST offset is still ambiguous (+300 vs +304), so the ticket IDs must remain conditional.

Artifacts:
- `results/h17-k04-p951-minimum-gap-words-20261107.md`
- `agents/agent12/k04_p951_gap_minimum_analysis.py` (reproduces the exhaustive minimum search)
- `agents/agent12/k04_p951_gap_word_recovery.py` (consumes the eight sourced words, reconstructs the selected payload and verifies the K04 commitment)
- The custodian addendum now includes the eight-word request.

I also checked the recovery ordering/endian logic using a synthetic state consistent with the base printer equations; reconstruction matched that synthetic target. This is only a solver-mechanics test, not a recovered archive value. K04 remains missing until authentic source words pass the official commitment.
