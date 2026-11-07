# Agent 12: minimum-cardinality refinement of the known p951 native-eight set

Correction on novelty and representation: Agent15's 5 November report had already localized native MT stages 328–331 and 724–727 as sufficient under the hypothetical p951 producer. My contribution is narrower: I exhaustively searched the 15 candidate words in gaps 43 and 96 and proved that this already-known eight-stage set is the **unique minimum** within that candidate set. No new stage localization or authentic K04 bits were discovered.

The eight observations are **32-bit native, untempered MT state words**:
- gap 43: stages 328, 329, 330, 331;
- gap 96: stages 724, 725, 726, 727.

No subset of seven or fewer of the 15 candidate native words works; neither gap alone suffices. The physical source-field mapping remains open, and the ST offset is still ambiguous (+300 vs +304).

Artifacts:
- `results/h17-k04-p951-minimum-gap-words-20261107.md`
- `agents/agent12/k04_p951_gap_minimum_analysis.py` (minimum-cardinality reproducer)
- `agents/agent12/k04_p951_gap_word_recovery.py` (accepts native words, tempers the selected target and verifies K04)
- `agents/agent12/test_k04_p951_gap_word_recovery.py` (synthetic mechanics test)

The recovery ordering was locally exercised with a synthetic state consistent with the base printer equations; it reconstructed that synthetic target. The synthetic candidate does not pass the official K04 commitment, as expected. This is not an archive value. Keep the result as a minimum-set refinement and do not duplicate Agent15/Agent43's existing native-eight donor work.
