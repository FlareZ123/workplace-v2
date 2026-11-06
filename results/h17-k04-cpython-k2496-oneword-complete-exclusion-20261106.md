# K04 long-startup CPython single-word seed: complete source-only exclusion

**Agent47 | 6 November 2026 | conditional original-source result.** Original REC8/1 remains six PASS, K04/K08 missing, combined INCOMPLETE. The selected original coupon has **zero** authenticated physical bytes from this test.

## Novelty and historical limits

Agent30's 5 November genuine CPython long-startup source analysis at actual MT output origin **k2496** left key-array lengths 1..4 undecided by its limited full-initialized-word necessary checks. Agent37 identified the missing **joint short-key initialized-register inversion** as a concrete target-bearing frontier (6 November, 20:26 UTC). Here the one-word integer-key case **n=1** is exhaustively closed using a stricter exact two-word source constraint and all 2^32 integer seeds. This is not the old early-origin n=1 exclusion, not a source-blind seed dictionary, and not a test of a NumPy producer.

All conclusions are conditional on **the hypothetical p951 schedule** mapping the original 133 printer packets onto native MT outputs and a CPython `random.Random` true startup after 2,496 earlier native output words. The original material does not attest that the printer ran CPython, this schedule, or this origin.

## Source-only reconstruction and derivation

- Historical original printer file `resources/evidence/print/spool-reconstruction.log`, immutable SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- The 18:02 UTC selected ESC-N RECOVER ACK2 copied packet **row129 is excluded from all fitting**. The remaining **132** full packets establish **15,365** independent linear MT constraints in the p951 geometry.
- The independent source-projector `agents/agent28/k04_cpython_real_output_offset_sft.py` maps those equations to CPython's 624-word initialized register at genuine offset **2496**. Its original-source partial-bit projection **fully fixes initialized S[6] = E403BB7D, S[7] = 1F7B301F**. New portable source wrapper `agents/agent47/k04_cpython_k2496_n1_source.py` pins the exact spool and checks both words. A separately genuine CPython seeded stream sampled at k2496 supplies every source-constrained original-register bit exactly and passes both-word recovery.
- For CPython's actual `init_by_array` with a **single unsigned 32-bit key word** `x`, define first-loop states `G[0]=19650218`, `G[i]=(1812433253*(G[i−1] XOR (G[i−1]>>30))+i) mod 2^32`, `A[0]=G[0]`, `A[i]=(G[i] XOR 1664525*(A[i−1] XOR (A[i−1]>>30)) + x) mod 2^32` for i=1..7. With no wrap before i=7, both CPython initialization passes give `A[7]=((S[7]+7) mod 2^32) XOR (1566083941*(S[6] XOR (S[6]>>30)) mod 2^32)`.
- Source-forced first-pass value is `A[7]=2AED5290`. The C++17/OpenMP SFT `agents/agent47/k04_cpython_k2496_n1_fullseed_sft.cpp` computes `A[7]` for every unsigned 32-bit x, checking the exact necessary equality, then executes the **full CPython initialization** for any survivor and checks the source `S6/S7` words.

## Measured complete integer-seed domain

Executed locally with compiled OpenMP C++17 code and exactly **4,294,967,296** seeds:

```text
CPYTHON_SEED_POSITIVE_CONTROLS=5 PASS
A7_SURVIVOR seed=548F97E6 predicted_S6=E9EC74CA predicted_S7=FD2664D6 full=0
COMPLETE_32BIT_DOMAIN=4294967296 A7_SURVIVORS=1 HISTORICAL_PAIR_MATCHES=0
```

Five authentic CPython reference seeds (0,1,8131,0x12345678,0xFFFFFFFF) test the exact initialization and intermediate arithmetic; a separate genuine seeded full-printer-packet synthetic control recovers its true initialized register under p951 k2496. The one necessary survivor `548F97E6` fails the independent two-word original-source check. **Thus no single-word CPython integer seed can produce the original retained printer packets under this model.** The original K04 SHA256, selected copied bytes, and original XOR mask were not used to fit the seed. Re-testing the K04 target is unnecessary after a source contradiction.

## Open frontier

**n=2,3,4** key-word CPython `init_by_array` families at this genuine k2496 origin remain **unexcluded by this test**. A next attack should couple source-fixed initialized words across the seed's modulo-n repetitions using nonlinear bit-vector inversion; it must validate genuine CPython seeded synthetic source/heldout packets and require **132/132** original whole-packet consistency before constructing any selected coupon. Expanding other seed names, offset guesses, K08 thematic paraphrases, or retry damaged bytes would repeat the existing research backlog.

No authenticated K04 coupon bit or K08 author-final phrase was recovered. Original evidence, verifier, acceptance, mask, and canonical candidate remain unmodified.
