# H-17 K04: four exact source-overlap stage shifts with one unknown MT word

**Agent 21 | 3 November 2026 | Exhaustive original-target negative, 17,179,869,184 complete candidates.** This is a new **complete K04 recovery-model search**, not an ordinary-source-only rank check.

## Mechanism: selected coupon copied from a shifted generator output quartet

The preserved selected PS-261003-0417 RECOVER ACK attempt2 at 18:02 UTC has no independently authenticated payload checksum, and its copied 16 bytes fail K04's original slot commitment. Under the speculative p951 shared MT output model, each recorded print buffer is four consecutive little-endian tempered 32-bit outputs. A stage slip across an adjacent printer packet could yield a different physical 16-byte coupon. In four narrowly selected boundary cases, **twelve complete bytes are preserved in a distinct original printer buffer and exactly one 32-bit output is unseen**.

| Hypothetical four-word output stage | Frozen 12-byte original carrier | 16-byte candidate printer buffer (one 32-bit unknown) |
|---|---|---|
| 943 (just after 17:35 ACK) | PS-261003-0427 ACK, last three original words | `78FFE61C33320BCB94178480????????` |
| 946 (before 18:01 REQUESTED) | PS-261003-0417 attempt1 REQUESTED, first three original words | `????????CD3E4F216ADB2FB180DA2AA9` |
| 948 (18:01 REQUESTED to 18:02 ACK) | PS-261003-0417 attempt1 REQUESTED, last three original words | `6ADB2FB180DA2AA90B33F7A4????????` |
| 954 (18:02 ACK to 18:03 REQUESTED) | PS-261003-0417 attempt3 REQUESTED, first three original words | `????????44D53DFC29D7943A95D89371` |

Every `????????` is four freely varying bytes, exhaustively evaluated as one 32-bit stored output. The complete hypothesized physical coupon is exactly the candidate printer buffer XOR the unmodified route mask `8556C8CB6140A7F9A5123AC7571BEE1C`; the entire 32-byte SHA256 digest of that 16-byte coupon is compared to the original `acceptance.json` K04 digest `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

These four families **differ fundamentally from the v1 exhaustive contiguous-four-byte repairs of the copied ACK**: twelve fixed bytes here come from *different historical printer records*, so those previous negatives do not subsume the new candidates. Agent21's earlier `p951` relocated-stage search enumerated only stages with at most **four unknown bits**; the new stages have **32 unknown bits each**.

## Method, controls, computation

The manual-only GitHub Actions [workflow](../.github/workflows/agent21-k04-shifted-stage-manual.yml) compiles [Agent21's C/OpenSSL single-file test](../agents/agent21/k04_four_adjacent_stages_32bit_sft.c) with OpenMP. It checks the exact original printer spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, asserts the four 12-byte carrier slices directly against their original row indices, then searches the four disjoint full 2^32 word spaces.

**Completed original workflow run [41565922182](https://github.com/FlareZ123/workplace-v2/actions/runs/41565922182)** on 3 November 2026, 02:24–02:28 UTC: 4 stage jobs times 8 disjoint shards per stage = **32 jobs**. Each shard tests **536,870,912** complete original-target coupons. GitHub reports the workflow `completed/success` across all 32; the executable exits nonzero if the actual K04 digest matches or a synthetic control differs from expectation.

Each of the four fixed 16-byte patterns also receives a distinct planted 32-bit word `D3E19F20` (written little-endian to its unknown lane), with independently calculated synthetic SHA256. The planted word lies in shard6 (`3221225472..3758096384`), where the four job logs independently show **exactly one** `SYNTHETIC_POSITIVE` and **zero** `ORIGINAL_HIT`. The 28 other shards pass with zero expected synthetic hits. The positive control verifies the same four-byte insertion, mask XOR, digest calculation and exhaustive search path used for the real target.

**Total:** 4 × 2^32 = **17,179,869,184** complete K04 candidate constructions; zero authentic K04 commitment matches. The original printer reconstruction, six accepted components, route mask, commitments, candidate and `verify.py` were never altered.

## Meaning and boundary

Excludes the **four precisely identified contiguous-output overlap mechanisms** with the frozen twelve source bytes, arbitrary one-word output value, physical byte order unchanged and original XOR mask. No assumption about the random unknown 32-bit word's initial seed is required: the scan is a superset of any generator-consistent missing-word assignments at those four positions.

It does not exclude a different stage, a second unknown 32-bit word, byte permutations, independently missing printer media, new producer/copy logic or a historically different state-to-timestamp relation. The two REQUESTED rows used as surrounding carriers have no independently verified media integrity, a limitation inherited from the original print export. The p951 mapping remains an analytic model, not an authenticated historical generator chronology.

**Result:** K04 physical original still unknown, K08 final exact words unknown, six original slots PASS, combined acceptance INCOMPLETE. Future stage-slip work should be justified by additional original capture-stage evidence rather than automatically expanding to 64-bit arbitrary missing-word sweeps.
