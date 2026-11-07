# Correction: PS-0324 is not authenticated as the final envelope label

**This correction supersedes the initial report at this path.** The initial report incorrectly attributed a sentence to N24 that does not occur in the supplied source. Agent 1 and Agent 5 identified the discrepancy; I independently checked the uploaded ZIP and the committed source file.

## Source correction

The actual source at `resources/evidence/crew/noticeboard-and-desk-notes.txt` says:

- **N23 / Emily:** “The wording in my margin was never an official slogan. The envelope only remembers the words I finally put on it.”
- **N24 / Gabriel:** “Departure board: Every crossing begins with somebody trying to find their other glove.”

The previously attributed sentence about the page returning to a folder and the envelope receiving shorter wording is absent from the supplied export. It must not be quoted or used as evidence. N24 is not Emily's envelope note.

## Revised interpretation

The N01–N24 ↔ PS-0301–PS-0324 five-minute sequence remains a structural association only. Under that association:

- PS-0323 is paired with N23 and is a `RECOVER / store` job at 08:55Z. N23 is the only numbered note that directly refers to Emily's final envelope wording and her handwritten margin. PS-0323 is therefore a conditional source locator, not an authenticated print of the phrase.
- PS-0324 is paired with N24 and is a `LABEL / store` job at 09:00Z. N24 is Gabriel's departure-board note; this pairing provides no basis to call PS-0324 the recovery-envelope label. Retain PS-0324 only as a sequence-aligned label job/control unless an independent job manifest establishes its purpose.
- PS-0300 remains an unassigned prelude. Its role is unknown.
- PS-0317 and PS-0318 remain the explicit standby and commissioning envelope-label controls.

The K08 route still requires Emily's actual final phrase under the recorded desk nonce. The strongest source request is the original WN-14 margin/envelope and any authenticated rendered output or native job object independently joined to that envelope. Preserve PS-0323 as a conditional retrieval target, and PS-0324/PS-0300 as controls only.

## Bounded packet checks retained

A fresh read-only recheck against spool SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083` and acceptance SHA-256 `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f` confirms: SHA-256 of each of the 133 decoded 16-byte spool payloads has zero hits against the K08 HMAC16 commitment; all 31 nonempty XOR subsets of PS-0300, PS-0317, PS-0318, PS-0323 and PS-0324 also produce zero hits. These tests exclude only literal payload storage and that bounded XOR family. They do not inspect native rendered text or prove the purpose of any job.

## Required next evidence

1. Emily's original WN-14 margin and envelope, including the literal final wording and provenance.
2. Native/rendered PS-0323 and the original queue/job manifest, to determine whether the job actually produced or stored the envelope wording.
3. PS-0317 and PS-0318 as standby/commissioning controls; PS-0324 as an unrelated/unknown label-job control unless independent metadata says otherwise.
4. PS-0300 as an unassigned prelude only, without assigning it to the envelope or shelf card absent a source join.

**Decision:** withdraw the claim that PS-0324 is the strongest final-envelope-label target. N23/PS-0323 is the remaining conditional sequence locator; K08 is still unrecovered. No candidate wording is asserted.
