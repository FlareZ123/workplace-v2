# K04 same-job cross-class source-fusion falsifier

**Agent 24 | 7 November 2026 | 21,935,032 complete original commitment checks; zero matches.**

## Question

Can the missing K04 coupon be reconstructed from retained fragments across all four records carrying job ID `PS-261003-0417`, including the earlier LABEL acknowledgement and the three later RECOVER attempts? This is a narrow extension of the existing three-RECOVER retry tests. It specifically tests whether the same-job LABEL record contributes fragments to a cross-class copy/reassembly error.

## Source facts

The source-pinned spool log contains four records for this job, in chronological order:

| Record index (zero-based) | Time (UTC) | Attempt | State | Class |
|---:|---|---:|---|---|
| 117 | 16:45 | 1 | ACK | LABEL |
| 128 | 18:01 | 1 | REQUESTED | RECOVER |
| 129 | 18:02 | 2 | ACK | RECOVER |
| 130 | 18:03 | 3 | REQUESTED | RECOVER |

The official K04 route selects the 18:02 RECOVER ACK2 payload and reduces a candidate coupon with the unchanged 16-byte route mask before checking the unchanged full SHA256 commitment. The log warns that it is a retained-fragment reconstruction and that payload integrity is unverified. The earlier LABEL record is not the official selected payload; it is included here only as a possible fragment donor.

## Method

The portable C++ SFT at [`agents/agent24/k04_samejob_crossclass_source_fusion_sft.cpp`](../agents/agent24/k04_samejob_crossclass_source_fusion_sft.cpp) pins the original spool, route, and acceptance file hashes before parsing.

It exhaustively checks two source-fusion families. In each, every one of the four same-job payloads contributes one contiguous four-byte fragment, with all 13 possible offsets and both byte directions per source, and all 24 source orderings:

1. **Concatenated fragments:** four selected fragments are appended in source-order permutation.
2. **Round-robin interleave:** the four selected fragments are interleaved one byte at a time.

Each family contains (24 \times 26^4 = 10,967,424) complete 16-byte coupon assignments.

A further boundary test checks 184 complete 16-byte candidates: raw chronological payload-stream windows and hex-nibble-stream windows that cross the selected ACK2 record boundary, each also checked in reversed byte order. The selected 16-byte ACK2 field itself is excluded from this boundary set.

Both fragment families and the raw-boundary search include planted complete-coupon positive controls. The unchanged original K04 commitment is used for every candidate.

## Results

| Family | Complete candidates | Original K04 hits | Planted control |
|---|---:|---:|---|
| Four-source concatenated 4-byte fragments | 10,967,424 | **0** | PASS |
| Four-source round-robin 4-byte fragments | 10,967,424 | **0** | PASS |
| Target-including raw/hex boundary windows | 184 | **0** | PASS (raw boundary) |
| **Total** | **21,935,032** | **0** | **PASS** |

Source pins passed:

- spool SHA256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- route SHA256: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- acceptance SHA256: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

Reproduce from the repository root:

```sh
g++ -O3 -march=native -std=c++17 agents/agent24/k04_samejob_crossclass_source_fusion_sft.cpp -lcrypto -o /tmp/k04_samejob_crossclass_source_fusion_sft
/tmp/k04_samejob_crossclass_source_fusion_sft resources/evidence/print/spool-reconstruction.log resources/evidence/recovery-routing.json resources/acceptance.json
```

## Interpretation and limits

This rejects the specified four-source contiguous-fragment concatenation, round-robin interleave, and target-boundary window constructions. It does **not** authenticate any K04 bit. It does not test arbitrary nonlinear transformations, different fragment lengths, missing raw printer `.SPL/.SHD` files, or the physical coupon itself. The ACK remains evidence of dispatch, not proof of media integrity.

No original resource, route, acceptance commitment, candidate, or verifier was modified. The six previously accepted components remain accepted; K04 and K08 remain unresolved, and the combined recovery key remains incomplete.
