# H-17 K04: genuine NumPy MT19937 seed-pool recovery across 4,103 later startup offsets

**Agent 30 | 5 November 2026 | Full original source gate; zero authentic K04 recovery.**

## Previously untested reconstruction path

The preserved printer spool contains 132 complete original 16-byte source packets outside the untrusted selected 18:02 RECOVER ACK2 copy. Prior NumPy `SeedSequence` work (Agent33) tested a four-pool seed initializer in the **first output cycle** using a five-pair state inverse. This investigation extends the same **genuine NumPy producer class** over **4,103 additional startup offsets 393 through 4,495 inclusive**. It reconstructs exact candidate initialized-state pool words from the original intact source's partial MT19937 state. A valid model would have predicted the entire selected 16-byte print payload independently and supplied a full K04 component through the original unchanged XOR mask and SHA256 commitment.

The original source evidence does not establish NumPy software, the particular p951 printer-stage chronology, actual prior draw count, or physical copy integrity. Consequently this is a complete exclusion *within this producer-and-chronology family*, with no claim about other generators.

## Exact source and producer constraints

- Original printer file SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; exactly 133 16-byte packets; source inference removes selected row129 **before byte decoding**.
- Surviving 132 intact packets impose 15,365 independent native-MT binary constraints under the existing conditional p951 packet-index schedule. The initialized register is reanchored at each genuine **prior raw output count** k; a cyclic register rotation is never substituted for a real generator startup offset.
- Genuine NumPy default four-word seed-pool initialization has `INIT_B=8B51F9DD`, `MULT_B=58F38DED` and for initialized word i>0, `S[i]=v XOR (v>>16)`, where `v=(pool[i%4] XOR (INIT_B*MULT_B^i))*INIT_B*MULT_B^(i+1) mod2^32`. NumPy sets `S[0]=80000000`. The original source bits of each `S[i]` are projected independently from the intact packet source.
- An initialized state word with all 32 bits fixed supplies one complete pool-lane inverse. A 31-bit-known word supplies two possibilities. For a later more weakly constrained word with at most 20 missing bits, invert **every** possible missing-bit completion, then reject pool values inconsistent with *all other source-fixed bits in that lane*. This is source-only algebra with deterministic finite completions, not a seed dictionary.
- To accept a pool when all four lanes survive, construct a genuine NumPy MT19937 complete output stream, verify **132/132 original 16-byte packets**, then derive `K04=selected_coupon XOR 8556C8CB6140A7F9A5123AC7571BEE1C` and require full original SHA256 `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

A genuine NumPy `SeedSequence` seeded from an independent synthetic 128-bit integer was tested at each pilot offset, and synthetic source reconstruction retained the true four pool words. The same seeded model passes partial-bit inversions for supported stages including offset4368 despite the lack of any fully determined initialized state word.

## Complete original-source executions

| Source-only regime | Genuine output startup offsets k | Offsets tested | Valid complete NumPy pool/132-packet model |
| --- | --- | ---: | ---: |
| Full or 31-bit-fixed initialized-state lane inversion | 393..3119 | **2,727** | **0** |
| Partially observed state words, exact missing-bit pool inversions | 3120..4495 | **1,376** | **0** |
| **Continuous additional startup range** | **393..4495 inclusive** | **4,103** | **0** |

The first range was split across 32 disjoint GitHub Actions shards. Initial run [42075413581](https://github.com/FlareZ123/workplace-v2/actions/runs/42075413581) completed 26 jobs with zero source-compatible models; six late-range shards originally failed because a *synthetic test* incorrectly required all four pool lanes to be source-visible. After correcting that overstrong positive-control assertion, the six exact failed shards 26..31 were rerun in [42076216033](https://github.com/FlareZ123/workplace-v2/actions/runs/42076216033) with **6/6 success** and zero complete models. The last six offsets 3114..3119 have insufficient near-complete state words; all six were separately resolved and excluded by the partial-word inverse in [42077593197](https://github.com/FlareZ123/workplace-v2/actions/runs/42077593197). The 32-shard full partial inversion [42076520028](https://github.com/FlareZ123/workplace-v2/actions/runs/42076520028) completed **32/32 success** and rejected every offset3120..4495 using real source contradictions, without requiring a full state reconstruction.

An illustrative previously unavailable direct constraint is **offset4368**, with only **160 initialized-register bits individually determined** and zero complete initialized state words: inverse per-lane best-word unknown-bit counts are 16,20,15,20, and all four reconstructed source-compatible pool sets are empty. A real seeded synthetic NumPy stream at the same offset supplies its true pool value in each corresponding inverse set (of cardinalities 2,1,2,8), validating the exact partial-bit computation.

All successful source scans show **zero fully constructed pool models matching 132/132 source packets** and **zero original K04 SHA256 hits**. Synthetic positives establish the code handles genuine seeded histories and reconstructable complete original K04 masked coupons; they do not certify the physical original.

## Separate, genuinely distinct larger-pool tests

The official NumPy SeedSequence also accepts nondefault pool sizes. A different exact initialized-state model with periodic `pool[i%size]` was evaluated for **pool size 8, 16, 32** and **actual prior output offsets k=0,624,2496**: nine complete source-gated model configurations. All nine genuine seeded NumPy controls verify the entire 624-word initialized register and emitted source packet layout. Every historical configuration contains at least one source-incompatible pool lane before a complete original K04 coupon can be constructed. Execution: [42077645818](https://github.com/FlareZ123/workplace-v2/actions/runs/42077645818), **9/9 success**, original accepted models **0/9**.

At k2496 the 31-bit source gate still observes only 5/8, 6/16 and 7/32 lanes; each family is excluded because **at least one of those independently observed lane candidate sets is empty**, rather than a false claim to know all pool values. The result does not extrapolate to other pool sizes or offsets.

## Reproduction and scope

- [True-output-startup CPython source control](../agents/agent30/k04_cpython_long_startup_phase_sft.py), [run 42073592156](https://github.com/FlareZ123/workplace-v2/actions/runs/42073592156), separately tests six previously unscreened later CPython startup offsets against actual integer-seed key-term constraints. Five of the six reject short n1..4 seeds; at offset2496 source fixed-bit density is insufficient to exclude them. This is a different producer than NumPy.
- [NumPy default pool4 complete-word pilot](../agents/agent30/k04_numpy_pool4_long_startup_sft.py), [initial pool4 32-shard scan](../agents/agent30/k04_numpy_pool4_phase_393_3119_sft.py), [partial-word inverse](../agents/agent30/k04_numpy_pool4_partialword_inversion_sft.py), [later complete scan](../agents/agent30/k04_numpy_pool4_partialphase_3120_4495_sft.py), and [nondefault NumPy pool-width SFT](../agents/agent30/k04_numpy_poolwidth_multilane_sft.py). All use the original source unchanged and source-pinned geometry.
- The original K04 selected copied ACK buffer is omitted from all source fitting, as are the K04 commitment and mask until full-candidate checking. Neither official `candidate.json`, `acceptance.json` nor `verify.py` was changed.
- The still-untrusted p951 stage chronology, genuine printer provenance and physical selected coupon remain crucial missing documentary facts. None of these tests yields an authentic K04 bit or a K08 exact word, and they do not justify reconstructing the full recovery key. K01/K02/K03/K05/K06/K07 remain accepted, K04/K08 missing, combined REC8 INCOMPLETE.

**Next high-value discriminator:** an original printer firmware/initializer record or an independently authenticated selected-coupon copy. Extending this one source-incompatible NumPy producer to arbitrary seed guesses without new evidence offers little additional progress.
