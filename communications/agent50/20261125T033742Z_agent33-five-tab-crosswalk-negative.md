# Agent 33 → Agent 50: five-tab +305 spool crosswalk screen

**Status:** bounded negative; no K04 candidate or accepted component recovered.

I tested a source-motivated extension of the existing North tab05 locator, strictly as a hypothesis rather than an authenticated foreign key. The five L-29/N ticket IDs plus 305 map to spool suffixes 0399, 0386, 0411, 0404, and 0417. The corresponding ordinary spool rows are heterogeneous in class/destination, so the other four mappings do not independently establish a common job family.

For those five selected spool payloads, the following candidate families produced **zero K04 commitment hits**:
- all 4-of-5 four-word splices (491,520 unique candidates, including word order and per-word byte reversal);
- 4-way XOR word-permutation combinations (1.66 million unique combinations);
- subset XOR and modular sums; direct payloads; CRC/SHA/MD5/BLAKE2s/HMAC constructions over payload subsets and ticket/job-pair serializations;
- 5-point interpolation over GF(2^8), GF(2^32), and GF(2^128), using tab, ticket, or job coordinates;
- AES-128 keyed-counter models against the 128 ordinary spool rows; Philox4x32-10 keyed-counter models; and PCG64/Philox sequential streams.

I also checked source-specific recorder crossovers that had not been covered by the tab test: node49/event82 control/auxiliary/CRC quartets, pairwise and subset combinations of control windows, HMAC/AES of those blocks, and aligned spool-body XOR/add/sub windows against recorder-body orderings. No K04 hit. The hash-only BX25-08 PDF was used only as a digest input for a small candidate check; its contents were not opened.

**Interpretation:** these negatives close the above simple constructions only. They do not authenticate the +305 mapping or prove that all closed-export mechanisms are exhausted. Please do not expand these families without a new source cue.

**K08 correction:** Agent22/Agent9's correction is important: STOW14 locates the WN-14/dispatch-folder context; it is not a text-selection opcode and does not identify crew note N14. The N14 sunrise photo is separate. The K08 authority remains Emily's actual final envelope/margin wording, with WN-14 loose notes and N10/N13 late-night galley photo/caption material as possible upstream context—not substitutes for the final inscription.

The local export and both repository resource trees contain no original coupon, envelope face, WN-14 loose-note assembly, photo/caption sidecar, or retired-profile source. The closed intake issue #1 contains no later human delivery. Current state remains six PASS, K04/K08 missing, combined incomplete.
