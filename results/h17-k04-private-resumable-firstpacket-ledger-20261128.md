# K04: source-private, restart-safe exact-state ledger separates PRNG inversion from coupon acceptance

**Agent37 · 28 November 2026 · implemented source-free test + CI-denied historical-source wrapper. No original component accepted.**

## Problem fixed

The active 28 November xoroshiro128++ recovery uses expensive P12-anchored SMT enumeration of complete `REQUESTED1` first-packet states, followed by cheap full-coupon XOR/SHA256 reductions and separately held-out later `REQUESTED3` replay. We previously discovered that (1) one state per SAT cube is incomplete, (2) later replay must **not** prefilter original K04 acceptance, and (3) selected ACK2 may occupy a later generator packet. Agent1 then extended the bounded selected start window to all **18 complete 16-byte pairs beginning at 64-bit generator indices 2..19**, including odd half-packet starts.

Multiple source scans were restarted when the reducer was corrected, wasting the costly producer solve. Some scans report only aggregate statuses and lose exact SAT states, making new whole-coupon tests require re-inversion. The 08:32 Critic broadcast explicitly identifies that reliability and compute-reuse bottleneck.

## Implemented reusable tools

- [Private model ledger and synthetic regression](../agents/agent37/k04_private_state_ledger_sft.py) is standard-library-only. A complete P12 cube stores an **append-only, immutable, exactly 0600 JSON attempt** with all full 128-bit SAT states and solver terminal status. Its existing **0700 root must be outside the GitHub repository**, and public CI is refused for private state access. A SHA256 namespace binds source-content digest, first-packet digest, four-way serializer, exact P12 bit positions, named PRNG, and circuit+model-blocking implementation identity. A different source or circuit yields a different namespace and cannot silently reuse old states.
- [CI-denied original-source wrapper](../agents/agent37/k04_xoropp_cached_source_local.py) has explicit **`--phase enumerate`** and **`--phase reduce`** actions. Enumeration revisits **both unvisited cubes and observed open UNKNOWN cubes** by default, skips only terminal UNSAT-sealed complete cubes, and optionally selects only previously open cubes when requested. Each completed inversion attempt is committed durably to the local private ledger independent of later target-screen policies. Reduction replays every cached SAT state against all 18 original-K04 **complete 16-byte coupon windows**, with its own original route XOR and original unchanged SHA256 commitment, **without running SMT or conditioning target acceptance on third-retry replay**. Any exact accepted value is written only to a private hit escrow, never public output.
- Retry attempt records are immutable, source-private and atomic (fsync before hard-link publication, no overwrite). Previous proven sealed cubes cannot be silently replaced; UNKNOWN is never promoted to UNSAT merely by replay. Unexpected/malformed state, wrong P12 cube, missing/changed source pins, weak path permissions, symlinks, repository paths and public-CI private-state use are rejected. Only method/count summaries print.

**Runnable local-only workflow** (paths must be created with 0700 outside any checkout):

```bash
mkdir -m 700 /tmp/h17-k04-ledger
python agents/agent37/k04_xoropp_cached_source_local.py --phase enumerate \
  --resources-root resources --private-dir /tmp/h17-k04-ledger \
  --endian little --order ab --start 0 --count 4096
python agents/agent37/k04_xoropp_cached_source_local.py --phase reduce \
  --resources-root resources --private-dir /tmp/h17-k04-ledger \
  --escrow /tmp/h17-k04-ledger/hits.jsonl \
  --endian little --order ab --start 0 --count 4096
```

The instructions assume a permitted *private local execution*. Do **not** run historical source in GitHub Actions or publish the private ledger/escrow, original state or any selected coupon.

## Executed source-free synthetic controls

The ledger regression was executed from a clean `tempfile.TemporaryDirectory` set to 0700 with the exact two distinct Agent37 collision states sharing firstpair+P12, plus one intentionally UNKNOWN and one never-visited cube. Observed:

- **One sealed full-state cube, one UNKNOWN/open cube and one genuinely unvisited cube** remained distinct after writing; two exact states were read back from the immutable complete cube.
- Source-free synthetic commitment at the farthest **odd start19** was **missed** by old fixed start2 but **recovered exactly once** when the same cached states were reduced over starts2..19. This update invoked **zero solver calls**, demonstrating actual producer/reducer decoupling and odd-word completeness.
- A changed circuit SHA moved the same cube to **unvisited** in the new namespace, not falsely sealed; a repeated write to the sealed cube and a state with the wrong P12 cube were both rejected.
- Every synthetic ledger attempt file had **0600** permissions. No source/original bytes, HMAC target, K04 route, key or PDF were loaded.

Execution printed only:
`synthetic_only=True, sealed_cubes=1, open_unknown=1, never_visited=1, cached_models=2, 18_word_start_replay=True, reducer_updated_without_SMT=True, source_circuit_mismatch_rejected=True, private_file_mode_0600=True, original_component_recovered=False`.

The original-source wrapper is authored and committed **but has not yet been used to persist actual historical state**. Healthy pre-existing little/AB scans were *not* interrupted to retrofit caching. Their terminal aggregate statuses can be reported with the correct caveat but exact SAT state caches do not exist retroactively; when one pre-existing firstpacket model was found in a 100-cube interval, that exact interval had to be rerun for 18-window K04 acceptance. This is precisely the wasted solve the new ledger prevents **for future new runs**.

## Complementary later-first producer direction (same persistent contract)

After Agent1's [source-free backward whole-coupon construction](h17-k04-xoropp-laterfirst-backwards-coupon-recovery-20261128.md) showed that REQUESTED3 could share a generator with the missing ACK2 even if REQUESTED1 did not, the cached wrapper gained `--fit-attempt 3`. It fits **only REQUESTED3** in the expensive 4096-bucket firstpacket inversion, stores those states in a *distinct* SHA namespace keyed by that packet and the exact backward reducer version, then uses **Agent1's independently tested exact inverse transition** to project 18 complete coupons at preceding output-word distances and apply the original K04 commitment **without conditioning on REQUESTED1 replay**. The earlier REQUESTED1 is a separate whole-packet diagnostic.

For a private local execution this uses the same two-phase commands with `--fit-attempt 3` added to **both** steps; a different source packet results in a separate immutable state cache. No new original-source backward scan was launched by Agent37; the inverse transition and all 72 backward coupon controls are explicitly credited to Agent1. The contribution here is reusable expensive-state persistence and cheap target-reducer replay for **either** producer direction, without duplicate SMT on future projection changes.

## Important boundary

A sealed cube means the exact firstpacket model enumeration terminated UNSAT **after model-blocking** in that run; it does **not** prove the original printer used the conjectured PRNG. An UNKNOWN cube can contain unenumerated accepted states and remains open even if all cached states fail all currently declared coupon windows. Fresh source or circuit revisions invalidate the cache; changes to *only* the cheap coupon window never should. The ledger cannot create missing source evidence, recover the original physical coupon or K08 wording by itself.

No historical K04/K08 recovery. Six/8 original slots accepted, combined INCOMPLETE.
