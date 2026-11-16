# H-17 K04: exact SFC32 same-job source inversion (16 November 2026)

**Agent 29. Outcome: no original K04 hit.** This is a complete, bounded conditional test of the native Small Fast Counting 32-bit (SFC32) generator, not a claim that the historical ESC-N printer used it. K04/K08 remain unresolved; original six slots pass; combined REC8/1 remains incomplete.

## Concrete event model

The original SHA256-pinned printer export `resources/evidence/print/spool-reconstruction.log` has hash `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. The selected job `PS-261003-0417` gives complete independent 16-byte packets at 18:01 attempt1 (`CD3E4F216ADB2FB180DA2AA90B33F7A4`) and 18:03 attempt3 (`44D53DFC29D7943A95D89371DA58EC64`). The damaged 18:02 attempt2 ACK was **withheld before inference**.

Hypothesis: one SFC32 emitter produced the same-job 16-byte packets in time order, with an arbitrary 32-bit initial counter and possibly hidden draws. This is distinct from previously tested MT, Romu, fax scrambler, and damaged-byte repair generators. Test four whole-word serializations (little/big endian, forward/reverse word order). For each 32-bit state `(a,b,c,k)`, write

```
t = a + b + k
a' = b XOR (b >> 9)
b' = 9*c
c' = ROTL32(c,21) + t
k' = k + 1
```

All arithmetic is modulo 2^32. Set `u(x)=x XOR (x>>9)` and `q0,q1,q2,q3` to the four native words of attempt1. **Exact algebraic inversion** over the sole remaining free native word `c0`:

```
b1 = 9*c0
c1 = ROTL32(c0,21) + q0
b2 = 9*c1
gb0 = u(b1) + b2 + q1 + 1 - b1 - q2
b0 = gb0 XOR (gb0>>9) XOR (gb0>>18) XOR (gb0>>27)
k0 = q1 - gb0 - b1 - 1
a0 = q0 - b0 - k0
```

Enumerate **all 2^32 possible `c0` values per serialization**, reconstruct `a0,b0,k0`, and require the generated fourth word to match `q3`. This exhausts *every* possible 128-bit initial state consistent with the first three native outputs, including **arbitrary** counter seeds (not only 1/13 or time values).

## Exhaustive source and acceptance observations

| Serializer | First-packet surviving native states | Whole 18:03 packet matches | Immediate K04 SHA256 matches |
| --- | ---: | ---: | ---: |
| little/forward | **4** | 0 | 0 |
| little/reverse | 0 | 0 | 0 |
| big/forward | 0 | 0 | 0 |
| big/reverse | 0 | 0 | 0 |

**17,179,869,184** native `c0` assignments were evaluated. Four little/forward states and their generated complete 16-byte *hypothetical* middle packets:

| `c0` | Middle packet (hex) | 18:03 full-object Hamming disagreement |
| --- | --- | ---: |
| `C50E7449` | `936E488CE7936A794F9C7C69EEBCB673` | 71 bits |
| `C523CB65` | `623E898CE0AB28781522836CEB439934` | 64 bits |
| `16147BEB` | `E31F48E31D414C43654A35C278010C89` | 66 bits |
| `E5DDC7CF` | `40C2C1275D79586904E0495156500B3B` | 54 bits |

Each complete hypothetical middle packet was XORed with the *original* K04 route mask `8556C8CB6140A7F9A5123AC7571BEE1C` and hashed against immutable target `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`: **zero** hits, even ignoring the failed 18:03 control.

**Hidden-output extension:** Advance each of those four exact initial states and test every consecutive fourword 16-byte coupon window at native word start offsets **4 through 1,048,579** (1,048,576 windows/state). **4,194,304 complete K04 SHA256 comparisons; zero original hits.** Compare each complete window with original attempt3 packet: **zero 128-bit source matches**. This is exhaustive for this defined bounded stage range, not proof about arbitrary further output gaps or per-attempt reseeding.

## Reproducibility and limits

C++17/OpenMP/OpenSSL SHA256 implementation was executed against the byte-pinned original ZIP export, never modifying evidence/verifier/acceptance/canonical candidate. Unsigned 32-bit recurrence was validated on **2,000 independent synthetic 12-output native traces**; the exact first-three-output inversion with true `c0` reconstructed all four state words and all 12 outputs. A planted `c0=1337`, arbitrary initial counter19, gave **one exact whole-object source positive** among 4,096 enumerated candidates. A separately planted 16-byte stream window at offset57 was found exactly once among 128 synthetic SHA256 comparisons. The full original scan completed, with no timed-out/unknown portion. An accompanying exact-source C++ implementation is to be kept with Agent29's working reproduction.

This rejects only this SFC32 native serialization and defined hidden-gap model. There is no evidence that ESC-N used SFC32, and no new selected coupon bits. A new producer, truly event-indexed selector, or author-final caption source must provide a different causal relationship. Do not duplicate this exact SFC32 scope.


## ACK-only source-meaning correction and independent extension (16 November, ~18:30 UTC)

The initial same-job experiment fitted 18:01 and 18:03 **REQUESTED** buffers, not independent printed ACKs. Because the source custodian explicitly distinguishes an ACK from a confirmed payload, the stronger causal alternative is a printer-emitter stream fitted only to *other intact ACK records* at the selected event boundary, while withholding the corrupted 18:02 ACK2. This is a different original observable set, not a reinterpretation of the request-buffer result.

The last regular **17:35 ACK** `PS-261003-0427` (`F0DC2DDF78FFE61C33320BCB94178480`) is the immediately preceding intact ACK in the log. The later **18:25 ACK** `PS-261003-0420` attempt2 (`432475F72A62DB39F3D5693E2C937FA4`) is a full 128-bit held-out printer-ACK control. The earlier 16:45 `PS-261003-0417` LABEL ACK has the same job ID as the 18:02 RECOVER but a different class and is not substituted for the causal last regular ACK. This test excludes all REQUESTED packets and the disputed selected ACK from producer-state reconstruction.

Run the same source-pinned exhaustive script, with its added `ack` mode:

```
g++ -O3 -std=c++17 -fopenmp agents/agent29/k04_sfc32_samejob_sft.cpp -lcrypto -o /tmp/h17sfc
OMP_NUM_THREADS=4 /tmp/h17sfc resources/evidence/print/spool-reconstruction.log 0 ack
# repeat with orientation 1, 2 and 3
```

Each of the four serializations exhausts all `2^32` possible free c0 native-state words and arbitrary initial counter (17,179,869,184 total).

| ACK-only serializer | First 17:35 ACK complete-state roots | Exact 18:25 ACK native holdouts | K04 original hits in first middle or hidden stream |
| --- | ---: | ---: | ---: |
| little/forward | 0 | 0 | 0 |
| little/reverse | 0 | 0 | 0 |
| big/forward | 0 | 0 | 0 |
| big/reverse | 1 | 0 | 0 |

The one big/reverse fully reconstructed state has `c0=424DC68C` and produces hypothetical immediate coupon `B9FCB8B7FB343B40BA5540BF5CBB445A`; its original K04 commitment fails. Search **every** next complete fourword window at native offsets 4..1,048,579: **1,048,576 additional full original K04 SHA256 comparisons, zero hits**, and **zero** full 18:25 ACK packet occurrences. The true selected 18:02 media was still not read for fitting. Synthetic 2000-state and planted whole-output-window positives still PASS under the exact same executable. Remote source blob `78de6dc7f898b180cd86f4fd4dc84b4f6c6e6a28` matches locally compiled and executed C++ code exactly.

**Combined scopes:** 34,359,738,368 first-packet state assignments and 5,242,880 complete hidden-window coupon comparisons across the two event-source interpretations, zero K04 commitment matches; the only five native initial-state roots all fail independent complete later controls. These are *conditional source-producer exclusions*, not evidence that real historical ACK buffers share any SFC32 state or that the archive has no solution by other mechanisms. K04/K08 and combined REC8/1 remain unresolved.
