# K04 source-first SFC32 inverse: complete one-packet state recovery and original fixed-serializer falsifier

**Agent 7, 4 November 2026.** A genuinely different 128-bit printer producer was investigated, with **all possible initial states** covered by an analytic 32-bit quotient. The four earliest intact original print packets contradict both constant big-endian and constant little-endian direct SFC32 four-word emission. **No K04 target bit was recovered.** The original selected 18:02 ACK2 packet and acceptance commitment were withheld from this source-gate.

## Model and mathematical inversion

Test an SFC32 writer (small fast counting, 32-bit) that constructs a 16-byte printer packet from four *consecutive* 32-bit outputs, serializing all four words consistently big-endian or little-endian. No historical source identifies SFC32 as the real printer algorithm. Every packet may start from any 128-bit state `(a,b,c,d)`, so this test does **not** assume the same seed, fixed interpacket gaps, clock seeding or a small seed dictionary.

One step modulo `2^32` emits `t=a+b+d` and updates `a'=b XOR (b>>9)`, `b'=9c`, `c'=ROL32(c,21)+t`, `d'=d+1`. The first three observed 32-bit outputs `t0,t1,t2` determine `a0,b0,d0` *given just c0*:

```text
c1 = ROL32(c0,21) + t0
b1 = 9*c0
d0 = t2 - (b1 XOR (b1>>9)) - 9*c1 - 2
b0 = unxorshift_right9(t1 - 9*c0 - d0 - 1)
a0 = t0 - b0 - d0
t3_pred = (9*c1 XOR ((9*c1)>>9)) + 9*(ROL32(c1,21)+t1) + d0 + 3
```

Here `unxorshift_right9(x) = x XOR (x>>9) XOR (x>>18) XOR (x>>27)`. Thus enumerating all **2^32** possibilities for `c0` and checking `t3_pred == t3`, followed by full four-output replay, exhausts **every 128-bit initial state compatible with one complete packet**. This is an exact inversion, not an SMT timeout or random-seed sample.

## Original-source result

Immutable spool source SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The SFT asserts this hash, reads four consecutive original packets at 07:00, 07:05, 07:10 and 07:15 on 3 October, and enumerates both 32-bit byte orders. Count is full-state preimages of each complete observed packet:

| Original job | Big-endian preimages | Little-endian preimages |
| --- | ---: | ---: |
| PS-261003-0300 | **1** | **0** |
| PS-261003-0301 | **3** | **0** |
| PS-261003-0302 | **0** | **1** |
| PS-261003-0303 | **0** | **3** |

A constant **big-endian** serializer is impossible for original rows 0302 and 0303 even after arbitrary packet reseeding. A constant **little-endian** serializer is impossible for 0300 and 0301. A fixed-endian, four-consecutive-output SFC32 packet generator cannot explain all four intact original rows, irrespective of interpacket gaps.

An arbitrary per-record endian switch could fit the four rows individually but is not supported by the surviving print route or copy evidence; matching one standalone packet is too weak to authenticate a generator. A 50-million-forward-output source-only exploratory replay from the unique 0300 BE state produced no complete 0301 or 0302 BE packet. That replay is an additional finite diagnostic rather than a universal theorem.

## Controls, reproducer and limits

[Full single-file C/OpenMP/OpenSSL SFT](../agents/agent7/k04_sfc32_invert_sft.c) performs the 9 complete 2^32 scans (one planted synthetic packet and eight original endian views), logs each initial state, and prints all per-row counts. A planted original-like SFC32 state `DEADBEEF,3BADF00D,12345678,00001337` was recovered **exactly** and replayed, validating the derived inverse and enumeration. The local original source-pinned run completed with all counts above. This tests an unconditional direct four-word emitter only: alternate output mixing, differing byte order per packet, nonconsecutive calls within packets or corrupted copies remain possible.

**Outcome:** a new complete producer-family exclusion without consulting K04's disputed copied target or spending hashes on an already falsified model. Six other components remain PASS; K04 and K08 remain unresolved and REC8 combined acceptance is INCOMPLETE.