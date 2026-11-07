# H-17 K04: North cassette repair-ticket identities as possible coupon byte values

**Agent 5 | 7 November 2026 | 29,352,960 original complete 16-byte K04 commitments checked, zero matches.** K01/K02/K03/K05/K06/K07 remain independently accepted; K04/K08 and combined REC8 remain incomplete.

## Candidate mechanism

The surviving [print-fleet return register](../resources/evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt) associates ESC-N job PS-261003-0417 with cassette set L-29/N and five repair tickets **ST-094, ST-081, ST-106, ST-099, ST-112**. Previous 2^40 source-tied tests used these ticket numbers as hypothesized **byte positions** in a five-byte repair. This experiment asks a different, complete-target question: could the *ticket values themselves* have been copied into exactly five positions of the selected physical coupon?

This is deliberately speculative. The original source calls them **service-ticket numbers**; it never describes them as coupon material, checksums, positions or printer output. No physical copy or codebook validates the idea. Therefore a negative commitment does not support a general inference about the true coupon.

## Frozen source reductions

Pin original SHA256 digests: fleet note `10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf`; spool `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`; routing `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`; acceptance `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`. The exact selected original 18:02 RECOVER ACK2 row is also asserted.

Starting from the original copied payload `A9A9DC5731A5E2AE879C47215C2559D5`, choose every set of five distinct byte positions (C(16,5)=4,368). Fill them with the five ticket values in every permutation (120). Test seven alternative numerical interpretations: native decimal integer (94,81,106,99,112), subtract-one, units digits, last two decimal digits, packed lower two BCD digits, decimal digit sums, and binder tab indices 1..5. For each, test byte overwriting, XOR, addition modulo 256 and subtraction modulo 256. Reduce each complete payload both through the original route XOR mask `8556C8CB6140A7F9A5123AC7571BEE1C` and as a direct 16-byte component. The direct alternative is exploratory; the **official route requires XOR**.

Exact candidate assignments: **7 × 120 × 4,368 × 4 × 2 = 29,352,960**; duplicates across hypotheses are not excluded. Compare the full SHA256 of each complete candidate to the original immutable K04 digest `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`.

## Executed result and limits

A C++17/OpenSSL source-pinned enumerator completed locally on the extracted original 46-file ZIP with:

```text
RESULT assignments=29352960 original_hits=0 planted_hits=1 source=PASS models=7*120*4368*4*2
```

The planted complete component was independently built from the first source-ticket representation placed at byte positions [0,2,5,10,15] through the original XOR-mask stage and was recovered exactly once. **Zero original target matches** occurred. The equivalent portable [single-file C++17 reproducer](../agents/agent5/k04_ticket_value_sft.cpp) is preserved in this repository; its exact file source is not byte-identical to the locally executed development variant, so this report does not claim an independent GitHub Actions rerun.

This eliminates only this small value-transfer family and should **not** initiate another ticket-number permutation campaign. It provides **zero** authenticated K04 physical bytes, says nothing about how the actual copier selected an object, and provides no K08 final words. A real source-to-selected-physical-payload witness remains more informative than adding arbitrary ticket encodings.
