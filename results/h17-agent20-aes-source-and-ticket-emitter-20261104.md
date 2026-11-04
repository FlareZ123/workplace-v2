# K04: source-selected and paired-ticket AES generation pilot

**Agent 20, 4 November 2026. Original REC8 recovery remains six PASS and K04/K08 MISSING.**

## Proposed mechanism

The retained 18:02 ESC-N RECOVER ACK2 spool payload is an unauthenticated copied coupon. A new hypothetical route is to derive a full coupon from known source identifiers and archival keys, rather than alter bytes of the disputed copy. Two source-constrained AES-128 mechanisms were tested using original archived source fields, without fitting to the K04 commitment. No original document attests that the 2026 printer used AES.

## Experiment A: common source-selected AES label emitter

The five selected independent prehash or raw blocks were held out as original source-object targets:

| Original selected source | Exact 16-byte block |
|---|---|
| K01 WN-14 signed ink | 049AAB2E1CDE7A82CD7C60234303C91A |
| K02 LT-204 selected telemetry prehash | E1A5E474BAD7E853A2E8C71D3317D507 |
| K05 TRP2 selected latch quartet | FF8B78200A56E8586DCDA00EF01E4572 |
| K06 RC-17 authorized C strips | 5DBF40EE52FAAED9A536D3326CF0D95A |
| K07 AX-7782 selected checkpoint prehash | 8947CEDCB9CC73BAB7E87BE63302C5C9 |

Ten original 16-byte key inputs: six individually accepted REC8 components, K02 and K07 source/prehash blocks, K04 route mask and K08 desk nonce. For each of six source roles including K04, form record-identity labels from its three visible aliases plus fixed archival prefixes, suffixes and separators. Candidate 16-byte producers: AES-128 CMAC of label, or AES-ECB applied to MD5(label), either half of SHA256(label), or a zero-padded ASCII label when short enough.

The source-pinned executed test made **132,800 complete 16-byte predictions**, split K01 22,520 / K02 21,970 / K05 22,170 / K06 22,440 / K07 22,040 / K04 21,660. **Zero** selected other-family 16-byte source blocks reproduced; **zero** K04 complete-component commitment hits after applying the original XOR mask. One planted full synthetic CMAC result was recovered. This excludes the exact label families and key/mode combinations, rather than proving absence of a historical keyed emitter.

Reproducer: [selected AES source-label SFT](../agents/agent20/k04_aes_selected_label_sft.py).

## Experiment B: cassette-ticket-derived AES, with a real sibling heldout

The original print-fleet retirement register maps north ESC-N / selected job PS-261003-0417 to five L-29/N service tickets **094, 081, 106, 099, 112**. South ESC-S / job PS-261003-0448 has independent L-29/S tickets **130, 151, 121, 135, 142**. The source-visible south RECOVER ACK1 packet is **234BE186E97EE05830909790E336109E** at 18:24 UTC. It is withheld as a complete original 16-byte sibling control. No original selected north copied payload is used to fit.

Seven encodings of the entire five-ticket set, three MD5/SHA256-half AES-128 key derivations, nine documented per-route message fields, seven message layouts, and four AES CMAC/ECB modes define **5,292 paired north/south formulas**. The original south 16-byte source yielded **zero exact predictions**; the masked north predictions yielded **zero full K04 commitment matches**. A planted entire south target appeared twice, reflecting duplicate formula outputs. Native NIST AES-ECB and RFC4493 CMAC known-answer controls passed.

Reproducer: [ticket AES holdout SFT](../agents/agent20/k04_ticket_aes_sft.py).

## Source pins, control boundaries and next value

Original source SHA256:
- Print spool: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
- Return register: 10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac059cd045e3cbf
- Recovery routing: f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5
- Acceptance commitments: 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f

Original K04 mask 8556C8CB6140A7F9A5123AC7571BEE1C and K04 SHA256 commitment 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0 remained immutable. Both scripts accept H17_RESOURCE_ROOT for source location, require Python cryptography, and read original evidence without writing it.

The independent south source control rejects this ticket-seeded AES family before target attribution. The five selected original source controls reject this global archive-label AES family. Neither test authenticates an original K04 bit, nor supplies the K08 final text. Do not expand the same uncued cryptographic parameter grid without a new, discriminating original source relation.

Closest prior work: [Agent10 non-AES ticket generator](h17-k04-paired-cassette-ticket-producer-holdout-20261104.md), [Agent46 Murmur3 selected source-label generator](h17-crossarchive-selected-source-label-emitter-20261104.md), [Agent18 selected-role transformation tests](h17-agent18-source-generating-frontier-20261104.md).