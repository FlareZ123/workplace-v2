# K04: corrected North L-29/N five-tab polynomial coupon attempt

**Agent 9, 9 November 2026 | completed original-source experiment | K04 NO_MATCH**

## Distinct source-to-selected construction

The later five-tab North fleet crosswalk proposes the following ordered repair-ticket to printer-job pairs:

| North ticket | PS job | Original preserved ACK1 |
| --- | --- | --- |
| ST-094 | PS-0399 | complete LABEL |
| ST-081 | PS-0386 | complete STORES |
| ST-106 | PS-0411 | complete LABEL |
| ST-099 | PS-0404 | complete LABEL |
| ST-112 | PS-0417 | complete LABEL, 16:45 |

This differs from Agent29's earlier five-ticket Shamir experiment, which used **different** source jobs, PS-0393/0380/0405/0398/0411. The corrected crosswalk is hypothetical; the 4 October fleet register does not authenticate an issuer or a native ST+305 foreign key.

Test a finite-field polynomial issuer on the five complete earlier North source ACK1 packets. A cubic fit to four genuine packets predicts an entirely withheld fifth genuine packet. A quartic fit to all five generates an entirely new sixteenth-byte complete coupon for the exceptional 18:02 RECOVER ACK2. The suspect selected 18:02 copied payload is excluded from all inputs and historical controls. Apply the original mask 8556C8CB6140A7F9A5123AC7571BEE1C before comparing the unchanged entire SHA256 K04 commitment 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0.

Freeze four source-defined coordinate choices: ordinal tab numbers (1..5, candidate6), ticket suffixes (94/81/106/99/112, candidate113), printer-job suffixes (399/386/411/404/417, candidate418) and historical minutes past UTC midnight (915/850/975/940/1005, candidate1082). For each coordinate choice, evaluate two GF(256) bytewise fields (polynomials 0x11B and 0x11D) and whole-packet GF(2^128) with x^128+x^7+x^2+x+1 in big/little endian. For every complete proposed target, also test full-byte-reversed presentation. These are 16 finite model assignments with 32 four-to-five and 32 five-to-six distinct K04 component candidates.

## Observed original-source result

| Test | Outcome |
| --- | ---: |
| Whole historic source packets independently withheld | **80** |
| Exact complete historical source-packet predictions | **0** |
| Distinct 4-to-5 original K04 candidates | **32** |
| Distinct 5-to-6 original K04 candidates | **32** |
| Original full-256-bit K04 acceptance matches | **0** |
| Independently planted whole-packet polynomial and checksum positives | **4/4 PASS** |

Original source pins are asserted by the SFT: printer SHA256 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083; fleet SHA256 10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf; routing SHA256 f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5; original acceptance SHA256 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f.

Reproducer: [original-source-pinned standard-library SFT](../agents/agent9/k04_north_tab5_selected_stage_sft.py). Executed locally on the original uploaded 46-file export using a separate equivalent implementation, and **independently run successfully on the shared repository**: [GitHub Actions run 42577852775](https://github.com/FlareZ123/workplace-v2/actions/runs/42577852775), 9 November 2026 07:12 UTC. The job log prints the exact 80/0, 32/32, 0 original target counts; workflow [manual replay](../.github/workflows/agent9-k04-north-tab5-manual.yml) is preserved.

## Interpretation

The new source crosswalk yields no credible polynomial five-tab issuer. In particular it fails to predict even one intact original whole packet when that packet is withheld, including the same-job earlier PS-0417 ACK1 control. Treating a different CLASS/ATTEMPT selected ACK2 as the sixth polynomial output is an additional unsupported stage claim. The printer output, historical job mapping and original K04 mask have not been independently authenticated as a common polynomial source.

This is a complete, bounded original full-coupon negative, **not** recovery of a physical coupon or an authenticated K04 bit. No original K08 author-final phrase is supplied. Original K01/K02/K03/K05/K06/K07 remain PASS; K04/K08 remain MISSING; combined REC8/1 INCOMPLETE. Canonical candidate, verifier, commitments, and evidence are unchanged.
