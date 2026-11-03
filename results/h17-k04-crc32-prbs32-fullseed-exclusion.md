# K04: Exhaustive 32-bit CRC-32 additive serial scrambler exclusion

**Agent 2 | 3 November 2026, 11:23 UTC. Original K04 commitment: NO_MATCH.** Six original REC8/1 components PASS; K04 and K08 remain unresolved.

## Novel target-reaching copy-channel hypothesis

MAIL-16 warns that the reconstructed ESC-N ACK does not prove physical coupon integrity. N22 describes the label printer behaving "like a fax machine"; this is a speculative clue for a serial-channel corruption model, not evidence of actual CRC32-based firmware.

Select the original 3 October 18:02 UTC job PS-261003-0417, RECOVER attempt2 ACK. Its untrusted retained copy is A9A9DC5731A5E2AE879C47215C2559D5. Keep the original route mask 8556C8CB6140A7F9A5123AC7571BEE1C and original slot SHA256 target 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

For all unsigned 32-bit initial register states, emit 128 serial bits of reflected CRC-32/ISO-HDLC-style PRBS under feedback polynomial 0xEDB88320. At each step emit the old state's low bit, then update register = (register >> 1) XOR (0xEDB88320 if old low bit is 1 else 0). Pack the 128-bit stream into 16 bytes using MSB-first or LSB-first bit order within every byte. Form each complete candidate as copied_ACK XOR original_mask XOR emitted_pad, and check its *full unchanged original K04 SHA256 commitment*.

There are 2^32 possible states per bit packing, so exactly **8,589,934,592 complete candidates** are evaluated. This family changes potentially every byte, unlike previous local byte-edit and four-byte repairs. Unlike Agent18's 16-bit LFSR test, this is a full 32-bit state space. Agent8's repeated XOR periods 1..24 do not cover this 32-step CRC-feedback law.

## Original-source pin, positive, exhaustive run

Portable C++17/OpenSSL source-pinned [single-file reproducer](../agents/agent2/k04_crc32_prbs_complete_sft.cpp), commit ad62c49b, checks the original spool SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083 and exact selected ACK source record before searching.

For efficiency the program precomputes each of the 32 basis-bit streams, enumerates seeds by Gray-code index, and updates only one 128-bit basis contribution between adjacent seeds. It still checks the complete SHA256 digest of every 16-byte candidate individually. Each packing is split into 16 disjoint shards of 268,435,456 states.

A planted independent complete 16-byte coupon derived by the serial emitter with seed A5301F69 is checked against its own SHA256 in the identical search. Exactly one planted seed occurs per packing, in shard 12; the corresponding job must find it. All other jobs require zero planted hits. **Any original K04 commitment hit or missing planted positive makes the job fail.**

[Manual-only GitHub Actions run 41626633574](https://github.com/FlareZ123/workplace-v2/actions/runs/41626633574), committed workflow .github/workflows/agent2-k04-prbs32.yml at 45200428, completed with **32 of 32 successful jobs**. The two shard-12 logs explicitly read:

- MSB-first: PLANTED_MATCH seed=a5301f69; DONE assignments=268435456 original_hits=0 planted_hits=1
- LSB-first: PLANTED_MATCH seed=a5301f69; DONE assignments=268435456 original_hits=0 planted_hits=1

The other 30 jobs each completed the same assignments and required zero planted hits. The C++ kernel separately passed a one-million-state local pilot and planted-positive shard control.

**Result: 8,589,934,592 original full SHA256 checks, zero original matches, two planted-positive hits.**

## Scope

This excludes *only* the exact reflected CRC32 feedback law, emitted-low-bit stage, both within-byte bit orders, and all 32-bit initial states acting on the retained copied ACK with the original mask unchanged. It does not exclude other 32-bit feedback polynomials, nonlinear line coding, per-lane restarts, independent raw-media originals, different producer logic, or a different selected physical coupon. No historical source asserts this specific printer scrambler; the model was exploratory. Original evidence, K04 mask, nonce, commitments, verifier and candidate remain unchanged.

Original K04 authenticated bits: **0/128**. Original K08 exact final words: **0**. Six other slots remain PASS and combined REC8 remains INCOMPLETE.
