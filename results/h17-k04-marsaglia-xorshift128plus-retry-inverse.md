# K04: invert two xorshift128+ sum outputs, predict complete retry packets

**Agent 24 | 3 November 2026 | New complete selected-coupon mechanism, original commitment NO_MATCH.** This test is an independently invented nonlinear producer-family route, distinct from prior Agent7 historical V8 **state0 upper-byte** output, Agent3/43 **xoshiro128\*\*** output and Agent24 **four-word Marsaglia xorshift128 raw-state** retry test. It uses the original 46-file ZIP, historical printer evidence only and the untouched K04 commitment. The hypothetical writer, serializer and state continuity are **unattested**.

## New inverse construction

Assume a recovered 16-byte spool packet contains **two consecutive 64-bit xorshift128+ summed outputs**, expressed in either 64-bit endian and either order of its two 8-byte words. The state is two native unsigned 64-bit words `(s0,s1)`. With all arithmetic modulo 2^64:

```
x = s0 XOR (s0 << 23)
next = x XOR s1 XOR (x >> 17) XOR (s1 >> 26)
output = s1 + next
new_state = (s1,next)
```

The two 64-bit observed output equalities yield a nonlinear 128-bit SMT bitvector system. I solved it with the **actual system libz3 C API** (`Z3_eval_smtlib2_string`), without relying on a single plausible inversion. After finding each model, block exactly its entire 128-bit initial state and solve again to UNSAT. A synthetic planted original state `123456789ABCDEF0,FEDCBA9876543210` produces output `CF8260251E21EDB3,32E811D6E07E1153`; Z3 enumerated exactly **three** complete state preimages, including the planted state, and ended UNSAT. This is a genuine inversion and exhaustion control, not a synthetic source-word equality.

## Original source and withheld tests

Read the canonical SHA-256-pinned original spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`, exclude the selected 18:02 ACK2 from all state inference. Two independent same-job two-packet sequences act as potential nonlinear generator continuations:

- **WATCH-SPARE PS-261003-0420**, 17:00 ACK1 `31C9714DD36DB2677BB9006670A9DFFD` → 18:25 ACK2 `432475F72A62DB39F3D5693E2C937FA4`.
- **ESC-N PS-261003-0417**, 18:01 REQUESTED1 `CD3E4F216ADB2FB180DA2AA90B33F7A4` → 18:03 REQUESTED3 `44D53DFC29D7943A95D89371DA58EC64`.

Four endian/reversal configurations per first packet, Z3 exhaustive preimages for each:
  
| Historical first packet | Little-normal | Little-reversed | Big-normal | Big-reversed |
| --- | ---: | ---: | ---: | ---: |
| WATCH-SPARE ACK1 | 0 states, UNSAT | 0 states, UNSAT | 0 states, UNSAT | **1 state, UNSAT after block** |
| ESC-N REQUESTED1 | 0 states, UNSAT | **2 states, UNSAT after blocks** | **1 state, UNSAT after block** | **1 state, UNSAT after block** |

Preserving observed 8-byte serializer orientation, advance each inferred state past the first two outputs and enumerate **8,192 later contiguous two-output packet windows**. None equals the paired independent preserved second packet in either job. For ESC-N's four state preimages, the 32,768 complete predicted 16-byte packets XOR original route mask `8556C8CB6140A7F9A5123AC7571BEE1C` yield **0** matches against original K04 SHA256 commitment `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. These are whole-coupon source-to-target predictions, not bit repairs of disputed ACK.

A local source-pinned, read-only Python/ctypes single-file reproducer was executed across disjoint solver cases, all output-state transitions and the complete 32,768 SHA candidates: `k04_retry_xorshift128plus_inverse_sft.py` (SHA256 `8dad20f662b35a7376c775b143e3b225428a2cb04bdfc47a1e915789b0309885`). It uses the installed system `libz3.so.4`. Preserve the exact source/serializer equations to reproduce in environments with a Z3 library.

## Scope

The tested **full64-summed-output** Marsaglia xorshift128+ packet serializer plus 8,192-window forward-state continuity does not reconstruct K04 from either intact same-job first packet and fails both second-packet holdouts. This leaves open other generators, 32-bit/truncated output serializers, unknown pauses longer than the window, multiple independently seeded retries, capture faults or non-RNG coupon production. No source identifies a true printer generator, and negative checks do not authenticate any bit of missing attempt2.

**Original acceptance unchanged:** K01,K02,K03,K05,K06,K07 PASS; K04 and K08 MISSING; combined REC8 INCOMPLETE. No original evidence, verifier, route, commitments or six-slot candidate changed.
