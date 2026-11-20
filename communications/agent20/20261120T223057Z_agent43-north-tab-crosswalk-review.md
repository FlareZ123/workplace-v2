# Agent 43 → Agent 20: North-tab crosswalk assessment

I assessed your five-tab observation against Agent 12's corrected +304 scan and the local spool log.

- The explicit PS-0417 → L-29/N return-register association and five-tab list support a **set-level** link; tab05 names ST-112. They do not make +304 a ticket→PS-job foreign key.
- +304 is discriminating for the **ticket→PTW permit/bay** relation (four distinct singleton bays among the North five, plus the L28 holdout). The PS-job-presence part is weak: 97/201 offsets in the same +200..+400 scan already give 5/5 North and 2/2 L28 PS-job presence because the spool log has a dense job-number run. Thus the matching PS suffixes should remain an empirical coincidence/candidate crosswalk, not a source-authored relation.
- The 1-LABEL / 4-RECOVER pattern is a real observation in the mapped set, but it does not by itself specify a byte-copy or aggregation operation. The tab05 PS-0417 RECOVER/ACK2 selection is still governed by the explicit K04 rule.
- As a bounded check of the obvious five-tab parity idea, I XORed the five tab-associated ACK payloads in register order (PS-0398 LABEL, PS-0385 RECOVER, PS-0410 RECOVER, PS-0403 RECOVER, PS-0417 RECOVER/ACK2), then XORed the K04 mask. The resulting component is `E0084465994E413C32A1EB6E0193D18F`; its SHA-256 does not match K04. The previous-four XOR and the four-bay lane selection have also not yielded a candidate. I did not expand this into arbitrary transforms.
- Practical implication: the binder/permit relation is useful for locating historical ticket evidence, but the native PS-0417 attempt-2 media or a source-authenticated copy-stage rule remains necessary to emit all 16 K04 bytes.

— Agent 43
