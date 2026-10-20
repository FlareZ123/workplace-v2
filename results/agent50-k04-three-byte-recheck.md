# Independent exhaustive K04 three-byte recheck

Agent 50 (normal research), 2026-10-20. The unmodified H17 source still contains **no accepted K04 coupon**.

* Candidate from last ACK RECOVER attempt 2 after documented XOR: `2CFF149C50E54557228E7DE60B3EB7C9`.
* Original immutable K04 SHA-256 target: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.
* Compiler: GCC with OpenSSL `SHA256`. Same method as `results/tools/k04_three_byte.c`; a local copy and all logs are preserved in the user handoff ZIP.
* Five independently executed shards, assigned by `triple_idx % 5`, each returned `EXHAUSTED ... triples=112`. There are `C(16,3)=560` position sets. Each enumerates all `256^3` byte values, for **9,395,240,960 hashed assignments**. Positions outside each triple stay equal to the original ACK-derived candidate. Every candidate changing at most three byte positions appears among these tested assignments.
* Positive control: replacing bytes 0..2 with `00 00 00` yields candidate `0000009C50E54557228E7DE60B3EB7C9` and SHA-256 `1847c4eda40e82cff046fe5f33352921947e8233995f96c768efe76d2ff53960`. The same executable with that test target returned `FOUND positions=0,1,2 candidate=0000009C50E54557228E7DE60B3EB7C9` before the first inner-loop increment. Positive control PASS.

**Outcome:** no K04 original commitment match under the exhaustive up-to-three-byte repair class. The checked class makes no claim about four or more corrupt bytes, a different authentic print payload, an independent source, or provenance. This is corroboration of substantially earlier identical bounds in [workplace-v1](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-three-byte-bound.md), discovered after the local test started. Future agents should reuse both results and avoid another run.

K04 and K08 remain MISSING; six other components PASS; combined acceptance INCOMPLETE.
