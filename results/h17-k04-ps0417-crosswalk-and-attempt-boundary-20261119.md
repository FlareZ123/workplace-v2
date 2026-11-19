# K04 PS-0417 crosswalk and attempt-chain boundary

**Status:** no new 16-byte K04 candidate. This note consolidates source-linked checks and corrects several easy-to-overstate joins so the next researcher does not repeat them.

## 1. Route and ticket identity

The official route transcription maps ESC-N to PS-261003-0417, ESC-S to PS-261003-0448, and WATCH-SPARE to PS-261003-0420 (resources/evidence/archive-labels.ini). The print-fleet note associates those jobs with L-29/N + FA-17 + H17-POL-17/A3, L-29/S + LV-42 + CS-18/5, and L-29/W + ST-09 + STORES/FLT respectively (resources/evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt).

The supplier reconciliation has ST-112 R3/POSTED at FA-17 / H17-POL-17/A3; the North binder list places ST-112 at tab05. It also has ST-142 R3/POSTED and ST-151 R3/POSTED at LV-42 / CS-18/5; the South binder list places ST-142 at tab05 and ST-151 at tab02 (resources/evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv and print-fleet-retirement-note.txt).

**Incident-date route caveat:** REC8/1 requires resolving ESC-N at the incident date (2026-10-03). The local archive-labels.ini is undated, and the print-fleet return register is a reconciliation dated 2026-10-04. The custodian note says the native Stores return index is not in this export. Thus PS-0417 is the best local ESC-N candidate, but the incident-date route resolution itself still needs the native index/queue manifest.

**Important join limit:** there is no explicit ST-112→PS-0417 foreign-key field in the local export. The association is inferred through route, binder, account, and folio context. The candidate North suffix offset +305 gives five action/class correspondences in the retained spool:
- ST-094 lid plate / return → PS-0399 ACK/LABEL
- ST-081 edge guide / exchange → PS-0386 ACK/STORES
- ST-106 separator / refit → PS-0411 ACK/LABEL
- ST-099 hinge / retain → PS-0404 ACK/LABEL
- ST-112 catch / clean → PS-0417 ACK/RECOVER

This is corroborative, not independently discriminating: a bounded offset sweep from 0 through 500 also found five class matches at +228 and +264. The +305 mapping remains a candidate cross-record join supported by the route/folio anchors, not an authenticated ticket/job key. The native Stores return index and queue/job manifest are absent.

The South +306 mapping is only partially represented: ST-121→PS-0427 (tab03) and ST-142→PS-0448 (tab05) are present; South tab02 ST-151 would predict PS-0457, which is absent from the retained spool. The tested PS-0417 versus PS-0448 comparison is a same-tab05 cross-route catch-family comparison (North catch cleaning versus South catch retain), not an identical action or byte source. Raw, XOR, bytewise add/subtract, and bounded digest-of-pair constructions did not pass the K04 commitment.

## 2. Attempt-chain stage constraint

Using only the 132 intact spool packets and excluding selected row129, recurrence discovery reproduces 25 fullword and 17 firstword relations. Adding the source-motivated exact four-word-per-attempt constraints for the consecutive PS-0417 RECOVER attempts at rows128/129/130,

`S129 = S128 + 4` and `S130 = S129 + 4`,

leaves the current chronology bounds unchanged:
- row128: [913, 967]
- row129: [917, 971]
- row130: [921, 975]

The p951 witness already assigns starts 947/951/955, so the attempt-chain condition adds no discriminator. The 42-relation graph does not directly constrain row129. However, zero witness participation is not unique to row129; many intact RECOVER ACK rows also have no fullword/firstword witness. Do not infer a special producer from row129's isolation alone.

Destination is not a sufficient discriminator either: PS-0417 and PS-0420 are both DEST=bench; PS-0448 is DEST=desk. PS-0420 row132 has one fullword plus one firstword witness, while selected row129 has none, but this is only a control observation.

Underlying stage-fit and symbolic-basis references: results/h17-k04-historical-witness-stage-fit-20261119.md, results/h17-k04-inlier-decoy-oracle-wholepacket-20261118.md, agents/agent43/k04_historical_witness_stage_fit_sft.py, and agents/agent49/k04_p951_symbolic_basis.py.

## 3. Payload integrity and remaining source

MAIL-16 states that the ACK field came from the dispatch log and must not be read as a media-integrity flag; it also says the retained-fragment export has no independent payload checksum for every line (resources/evidence/mail/16.eml). The custodian note independently says this is a working preservation export, not the full incident record; raw spool payloads are not all independently validated; ACK proves receipt, not correctness; and absence of a gap marker is not a completeness certificate (resources/evidence/records-custodian.txt). Therefore the selected PS-0417 attempt-2 RECOVER payload in spool-reconstruction.log is not independently authenticated. Applying the documented K04 mask to that local payload does not pass the unchanged K04 acceptance commitment.

Additional bounded checks in this invocation did not produce a K04 hit: the signed PTW-417 revision-4 CLOSED REMOVED serial quartet; the four prior North-tab spool payloads as XOR/hash/window/CRC/seed-sequence inputs; and the North/South catch-family pair. These are scoped negatives, not reasons to broaden into generic seed, PRNG, or arbitrary payload algebra.

**Actionable missing evidence:** an independently authorized native PS-261003-0417 attempt-2 queue/dispatch/job object, its rendered/media output, or the original ESC-N physical coupon; plus the native Stores return index if the ticket/job join must be authenticated. Existing read-only intake tools are work/h17_missing_source_intake.py and work/h17_k04_binary_window_intake.py. No canonical candidate, acceptance file, or verifier was changed.
