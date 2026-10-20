# Agent 29: H-17 missing-component research

Claimed 2026-10-20 13:08 UTC. This identity is in **normal research mode**. The target is REC8/1 historical archive reconstruction. The verified six slots and original-source inventories already exist; avoid repeating them.

## Priority and frontier

- Exact original source archive `h17-archive-dump.zip` is identical in file content to the repository source, including the four office-supplement files; all earlier source/ZIP/PDF/carrier checks and six-slot acceptance were already completed.
- K04 retained ACK payload for PS-261003-0417 attempt 2 is `A9A9DC5731A5E2AE879C47215C2559D5`; XOR mask yields `2CFF149C50E54557228E7DE60B3EB7C9`, which does not pass the untouched K04 commitment. The exact original coupon has not been observed. V1's three-byte, contiguous-four-byte and lane-XOR exhaustive exclusions, original-source MT chronology and causal 128-dimensional nullspace make repeating familiar repair/PRNG-state enumeration poor priorities.
- K08 Emily's exact final margin not quoted in N02/N06/N10/N13/N20/N23, MAIL-11/14/20; broad source spans and source-free paraphrase sweeps are prior art. Source-only editorial rule cannot yet force a normalized word.
- Latest relevant Critic directive: `communications/broadcast/20261020T1231Z_Critic_restore_closed-export-cracking-lane.md`; aim for a new original-source anchored producer with a blinded intact prediction and actual K04 quotient improvement, or a source-evidenced K08 finite editorial rule. Source intake tracked by v2 Issue #1 (assigned maintainer, not documented actual historical-custodian receipt). Do not access privileged systems.
 
## New bounded local tests, 20 Oct ~13:12-13:19 UTC

Independently evaluated two *previously unlisted* reversible 64-bit raw-output producer families on the **128 intact regular spool records** PS-261003-0300 through 0427. Original ACK row PS-261003-0417 ATTEMPT=2 was fully withheld. Each 16-byte intact payload was interpreted as two consecutive u64 outputs, in each of four orientations: little/big endian and original/reversed 8-byte half ordering.

1. **SplitMix64** (published mix multipliers `BF58476D1CE4E5B9` and `94D049BB133111EB`, increment `9E3779B97F4A7C15`): invert each output's two multiplications modulo 2^64 and the three xor-right-shifts to derive successive internal states; demand the states differ by the canonical increment inside each payload. For all four orientations, **0 of 128 intact rows** satisfied the required transition. The 128 observed state differences were unique in each orientation. Source-independent algorithm checked with the same invertible arithmetic. This strongly falsifies an unmodified two-output-per-payload SplitMix64 source. It does not test altered mixers, different draw spacing or upstream postprocessing.
2. **Raw full-state 64-bit affine generator** `y = a*x + c (mod 2^64)` with globally constant but *unknown* multiplier and increment. Fit `a,c` on two early intact row-pairs whose first halves differed by odd parity, then predict the withheld **next 120 regular rows**. Across four orientations the trained law fit only its two calibration rows and **0/120 heldout rows**. Fitted multipliers were distinct across orientations; no affine-consecutive model survived.

Both are narrow **negative producer tests**, not evidence of a new target witness or a cryptographic recovery; no K04 coupon bits, K08 final words or extra PASS values resulted. They are secondary in importance to the already observed MT-style recurrence and not worth an independent top-level result. Do not expand these into unsourced variant sweeps.

## Useful next action

Look for an **actual new source-implied predictor** instead of seeking arbitrary generators compatible with a few outputs. The source's broad 128-row + Z-retry construction provides an intact holdout for any proposed printer producer but still lacks authenticated selected coupon bytes. For K08, only an original final margin/caption or exact witnessed edit rule can justify a decisive phrase family. Avoid claiming source insufficiency as an unconditional proof of puzzle impossibility. Keep any useful new work traceable to specific original bytes and the original acceptances.
