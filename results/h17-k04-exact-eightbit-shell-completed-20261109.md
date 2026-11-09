# K04: completed exact-eight copied-ACK correction shell, original commitment negative

**9 November 2026, Agent 20, audit of Agent 15's pre-existing exhaustive computation. No new K04 component.**

## Original source and precise candidate family

The selected incident-date route is ESC-N, `PS-261003-0417`, 18:02 UTC, RECOVER ACK attempt 2. Original copied payload `A9A9DC5731A5E2AE879C47215C2559D5` XOR original immutable mask `8556C8CB6140A7F9A5123AC7571BEE1C` yields baseline `2CFF149C50E54557228E7DE60B3EB7C9`. The original K04 full SHA256 commitment is `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

Agent 15's [source code](../agents/agent15/k04_eightbit_sharded_sft.cpp) enumerates each strictly ascending eight-distinct-bit subset of all 128 component positions, flips those eight baseline bits, then hashes all 16 resulting bytes using a one-block SHA256 transform. These are precisely all corrections of Hamming weight eight under the copied-buffer plus unchanged-mask interpretation. Their original 64-shard [GitHub Actions run 42551030785](https://github.com/FlareZ123/workplace-v2/actions/runs/42551030785) used pinned original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` and original acceptance SHA256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`.

## Independent completion audit, not a repeat search

I retrieved the actual run metadata **and the terminal `COMPLETE` line of every one of the 64 original shard job logs** through GitHub Actions, and separately inspected the self-test log and committed C++ source:

- Workflow original commit: `dd2d38b04205b45757bf59038a728a98e18167f0`. All **65/65** workflow jobs report success (64 search shards plus source-pinned planted self-test). Every shard ID **0 through 63** appears exactly once.
- Every shard reports `checked=expected`, with `original_hits=0` and `planted_hits=expected_plant`. Exactly **one** planted eight-bit positive occurs, in shard **49**. The independent self-test reports `SELFTEST checks=1 original_hits=0 planted_hits=1`.
- The shard partition chooses each pair of the first two ordered bit positions `(a,b)` exactly once by `(131a+17b) mod 64`, then enumerates all remaining six later positions. The complete search therefore covers exactly `C(128,8) = 1,429,702,652,400` distinct full-16-byte components. Its per-pair and per-shard checked-count assertions independently protect against incomplete execution.
- **Original full SHA256 matches: 0 / 1,429,702,652,400.**

The original run was already completed at 03:14 UTC on 9 November. This audit supplies a compact reproducible remote-log certification of a completed predecessor experiment, with its original author and tool unchanged; no new brute-force execution or relabeled contribution is claimed.

## Decision boundary and previously completed shells

The prior [v1 exact 0–6-bit result](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-bitflip-bound.md) checked 5,699,195,233 candidates without a match. The [Agent 15 exact-seven run](h17-k04-exact-sevenbit-shell-20261109.md) checked 94,525,795,200 without a match. Therefore **all 1,529,927,642,833 candidate strings within Hamming distance at most eight** of the retained component baseline have been checked and excluded by the original acceptance commitment.

This bound is conditional on the fixed selected copied buffer and original XOR mask. It says the valid K04 component, if present, differs by at least **nine bits** from that baseline. No original physical fault-size distribution, native printed coupon or manufacturer copy-stage behavior has been authenticated. An automatic nine-bit radius expansion would repeat the same unsupported model with enormous additional cost. A different original selected-object producer/copy route is required to improve recovery odds.

**Accepted REC8/1 status:** K01, K02, K03, K05, K06 and K07 PASS. K04 and K08 still MISSING; combined INCOMPLETE. This audit did not modify original evidence, acceptance, route, verifier or canonical candidate.
