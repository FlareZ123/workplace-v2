# K08: exact 13-word source-length editor from N01/N06 plus two P20 motif-word insertions

**Agent 1 | 28 November 2026 | 107,986,944 complete original K08 checks | 0 original matches**

## Source-selected operands and the genuinely new constructor

The independent `MHI` head of N20 selects original notes N13/N08/N09; the already-established body-word and heading LOW BIT routes select **N06**, Emily's labelled *Second desk draft*, and **N01**, Jason's empty-bench photograph. See [MHI -> N01/N06](../h17-k08-mhi-n06-n01-fixed-editor-20261128.md). The independent AT/MT/ET/PT source program fixes a **13-word** N20 editorial motif payload, P20, whose SHA-256 is `4b3350e5b34e40cc9dd1ba53d926ef0455888aa056aac4ba7da141569664e95c`. See [fixed payload](../h17-k08-crosscarrier-fixed-payload-20261128.md).

Both selected N01 and N06 body rows normalize to **exactly 11 words**. The current experiment tests a specific *length-matching editorial hypothesis*: a final 13-word caption retained one literal 11-word position-aligned crossover between N01 and N06 and gained the **two remaining words by insertion from P20**. The fixed 13-versus-11 source width motivates the number of insertions. This does **not** establish that Emily actually composed the caption this way; the 11 crossover choices, two insertion sites, and two motif-word identities remain uncalibrated.

This is a different complete-output domain from Agent14's four-source equal-width 13-word aligned crossover, Agent11's P20-only permutations and source `room` extension, and our own [zero/one-word N01/N06/P20 editor](../h17-k08-n01-n06-p20-single-edit-complete-20261128.md).

## Exact enumerable domain

- Choose the N01 or N06 token independently at each of the **11 corresponding word positions**: `2^11 = 2048` masks.
- Consider four whole-source orientations, corresponding to neither selected row reversed, only N01 reversed, only N06 reversed, or both reversed. N07's calibrated reversal suggests why these four orientations merit exposing, but does not establish an actual source revision.
- Choose two *distinct final caption insertion sites* from the 13 resulting positions: `C(13,2)=78`.
- At each insertion site independently insert one of the **13 source-position tokens** in the fixed P20 motif, in final position order: `13^2 = 169` assignments. Repeated occurrences of `the` produce duplicate normalized outputs; no uniqueness claim is made.

**Total: 4 × 2048 × 78 × 169 = 107,986,944 complete normalized-caption assignment checks.** No unsourced extra vocabulary, other source rows, deletion, replacement, word order rearrangement beyond whole-row reversal, or fabricated joiners are allowed.

All candidates use the **unaltered** original K08 HMAC-SHA256 desk nonce, first 16 output bytes, then full SHA256 original slot commitment. The existing original source note, route, acceptance files and canonical candidate were not modified.

## Executed original-source results

The C++17/OpenSSL/OpenMP [source-pinned reproducer](../../agents/agent1/k08_n01_n06_p20_two_insertions_sft.cpp) asserts three original SHA pins (notes, route, acceptance), all source token counts, the P20 payload digest, the unique N20 first-three-byte `MHI` emission, and the historical independent N02 HMAC16 fixture. It plants a separate 13-word *in-family* positive with a known source mask and two P20 insertions; the run recovers this positive in the first shard.

Actual unchanged-source local executions, three disjoint half-open mask ranges (all four orientations and all 13,182 two-word insertion assignments in each mask):

```text
start=0    stop=128  checked=6749184  original_hits=0 planted_hits=15
start=128  stop=1024 checked=47244288 original_hits=0 planted_hits=0
start=1024 stop=2048 checked=53993472 original_hits=0 planted_hits=0
---------------------------------------------------------------------
total masks=2048; total checked=107986944; original_hits=0
```

The synthetic positive repeats across equivalent crossover masks and orientations, so its hit count of 15 is **not** an independence or uniqueness measure. The first shard verifies that the full source->candidate->HMAC16->SHA256 path recovers an intentionally planted valid 13-word member. Later disjoint masks do not include that positive and correctly do not require their own identical positive.

Run from the repository root on the immutable unpacked archive:

```sh
g++ -O3 -std=c++17 -fopenmp agents/agent1/k08_n01_n06_p20_two_insertions_sft.cpp -lcrypto -o /tmp/k08_two_inserts
OMP_NUM_THREADS=4 /tmp/k08_two_inserts resources 0 128
OMP_NUM_THREADS=4 /tmp/k08_two_inserts resources 128 1024
OMP_NUM_THREADS=4 /tmp/k08_two_inserts resources 1024 2048
```

No original target digest, nonce, candidate phrase, component bytes, or synthetic selected words are printed by the source-pinned runner. It reads no restricted source, PDF, or external network.

## Precise consequence

**K08 is not in this complete 107,986,944-assignment literal two-insertion authoring family**, even though the number of inserted source motif words matches the 13/11 length gap. This closes one coherent way for the strongly selected second-draft/photograph carrier pair to grow into the exactly source-fixed editorial motif length; it does **not** prove the historical keeper-envelope inscription had thirteen words, was a literal crossover, used either input caption, or included any specific P20 word. It does not generalize to arbitrary two-word additions, other edits, or unseen final margin content.

Given this model's complete failure and prior single-edit failure, a next K08 attempt needs a **genuinely different source-defined terminal version/edit operation** rather than automatic escalation to three insertions or arbitrary extra palette words. The original REC8/1 status remains six PASS, K04 and K08 MISSING, combined INCOMPLETE.
