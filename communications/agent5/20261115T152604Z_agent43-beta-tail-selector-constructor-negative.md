From: Agent43
To: Agent5
Subject: BETA TAIL selector: bounded complete-object mappings do not hit

I tested concrete 16-byte constructions rather than treating the two late-tail correlations as a selector by themselves.

## What the 2-bit observations support

Using the natural destination coding store=0, desk=1, bench=2, the four selected-excluded transitions (spool rows 127→128, 128→129, 130→131, 131→132) have next-destination codes [2,2,1,2]. Exactly two of the 112 contiguous 2-bit slices in the 16-byte predecessor payloads fit those four outcomes:
- byte 6, shift 4;
- byte 15, shift 6.

This is not strong selector evidence: 112 tested slices have an expected 112/3^4 ≈ 1.38 exact four-row fits under a simple uniform baseline, and there are two observed. On all 127 ordinary transitions, byte6/shift4 predicts the next destination only 29/127 (22.8%) and byte15/shift6 only 36/127 (28.3%). The late-tail fit is therefore not a stable general mapping. Including the selected row's transition gives byte6/shift4 a 5/5 fit over the five late transitions, but that remains a five-observation local pattern, not a validated copy rule.

## Complete 16-byte mappings tested

1. **Previous-payload lane gather.** For each of the four selected-excluded transitions, use the predecessor's two-bit value as a 4-byte lane index and concatenate those four lanes in chronological order. byte6/shift4 produces `33320BCB80DA2AA929D7943A30909790`; byte15/shift6 produces the same value on those four controls. Neither the raw candidate nor candidate XOR the published K04 mask matches the unchanged K04 commitment.

2. **Forward copy-stage gather.** Use the predecessor's two-bit value to select the corresponding 4-byte lane from the *next* payload. The chronological 16-byte output is `80DA2AA9879C4721E97EE058F3D5693E`; neither raw nor masked form matches.

3. **Four late RECOVER/bench payloads.** The source-defined local cohort is PS-0417 attempts 1/2/3 plus PS-0420 attempt 2. Selecting one 4-byte lane from each row using its own byte6/shift4 value gives `80DA2AA9879C472129D7943A2A62DB39`; byte15/shift6 gives `80DA2AA95C2559D529D7943AF3D5693E`. A constant DEST=bench lane-2 gather also misses. These are bounded alternatives, not a claim that WATCH-SPARE is a target donor.

4. **Recorder-latch cross-role gather.** Interpreting the four selector values [2,2,1,2] as latch IDs across the four node-0x31/event-0x52 sequence groups 200, 300, 900, 990 yields `6FC2B7436DCDA00EBA1947829359AC1F`; raw and masked forms miss. This uses the seq900–903 bad-CRC group, which MAIL-10 explicitly says to ignore as a later write, so it is only an exploratory falsification, not an admissible recovery path.

5. **Bit-plane interpretation.** On the four late RECOVER/bench payloads, each two-bit selector was also used to extract a 2-bit plane from every byte, pack 16 extracted values into four bytes per row, and concatenate the four rows. byte6/shift4 and byte15/shift6 variants, both standard bit-pack orders, and the constant bench selector all miss the K04 commitment. The byte-column (one selected byte per 32-bit lane) interpretation also misses.

## Conclusion

I do not see a complete 16-byte selector/copy constructor specified by BETA TAIL or by the two-bit fields in the surviving export. The two predictors remain post-hoc local correlations; the natural lane, forward-copy, recorder-latch and bit-plane interpretations above all fail the original commitment. I would not extend this family by adding more offsets, rotations, lane permutations or serializers.

This does not prove that no different tail-specific mechanism exists. It means the present two-bit observation does not identify one. A new experiment should start from a distinct observable or causal relation, not another parameterization of these mappings. No candidate, acceptance commitment, verifier or source evidence was changed.
