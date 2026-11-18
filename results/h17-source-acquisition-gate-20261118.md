# H-17 optional source-acquisition lane: exact missing historical originals

**Agent 45 — 2026-11-18**

**Critic clarification (18 November):** This report describes a high-value **authorized original-source acquisition lane**, not a necessary precondition for solving the REC8/1 commitments. The maintainer explicitly confirms solvability and permits genuine closed-export reconstruction under uncertainty. No original coupon or final caption is present in the working export as currently characterized, but that source gap does not prove that no source-dependent transformation, selection relation, or alternative interpretation can construct an accepted K04/K08 candidate. Agents should pursue materially different complete-object mechanisms concurrently with any lawful source intake. Historical authenticity remains a separate question from a commitment PASS.

## Current state

Six of eight components are authenticated by the unchanged acceptance commitments. K04 and K08 remain the only missing components; REC8/1 cannot complete until both are supplied.

The supplied export is intentionally trimmed. The current repository-wide source-boundary checks agree that no authenticated K04 coupon bytes or Emily's final keeper wording exist in the supplied ZIP, current repository tree, private/ tree, Git history, or sampled workflow artifacts.

## K04 — high-value independent original sources

Highest-value historical records:

1. Native print-host material for PS-261003-0417: .SPL, .SHD, EMF/PRN, or equivalent rendered output/media.
2. The native queue journal/export for PS-261003-0417, including mode, purpose, and dry_run.
3. FA-17 / H17-POL-17/A3 asset card and September 2026 equipment-count/commissioning material.
4. The physical escrow coupon or an independently authenticated copy.
5. R:/Stores/returns/SEP26/index.htm and R:/IT/desktop-move-2026.html/profile-migration package are useful source-side joins.

The retained text spool identifies the correct dispatch selector as the last ACK for exact job PS-261003-0417, attempt 2, CLASS=RECOVER, payload A9A9DC5731A5E2AE879C47215C2559D5. Applying the published mask yields 2CFF149C50E54557228E7DE60B3EB7C9, whose SHA-256 does not equal the K04 commitment. Therefore the retained ACK is a selector, not an authenticated coupon byte source.

## K08 — high-value independent original sources

Highest-value historical records:

1. Emily's original WN-14 final envelope/margin or desk-note stack containing the final caption.
2. The separate photo/galley-caption carrier referenced by the preserved correspondence.
3. The referenced mug-stock workbook and any preserved thumbnail/cache copy.
4. Native PS-0323 rendered/print output, if it exists.
5. R:/Records/INDEX/IR-261003-H17.txt and the related profile migration package.

The unchanged K08 rule is authoritative: normalize the recovered phrase, HMAC-SHA256 it with desk nonce 5F933DA6A1BD03C32DA5CBC25344F497, retain the first 16 bytes, then SHA-256 that 16-byte value against the acceptance commitment.

## Ready-to-run intake

`work/h17_missing_source_intake.py` is now committed as a read-only intake/commitment harness. Point it at an authorized recovered SharePoint/R-drive tree. It will select the last ACK for PS-261003-0417 and check the K04 commitment, and scan named WN-14/desk/caption/galley/crew text carriers for contiguous K08 commitment hits. Existing native XPS/EMF/profile scanners in `work/` should be used for binary/native carriers before feeding their extracted text or bytes into the acceptance verifier.

The SharePoint connector is the currently identified authorized retrieval route, but it is not connected in this invocation; connection requires explicit user action.

## Do not do

- Do not alter acceptance commitments or verifier logic.
- Do not treat the rejected ACK payload, PS-0323 text payload, public-book scans, or generic PRNG/hash fits as recovered components.
- Do not probe protected intranet/admin/custodian systems.
- Do not widen already-closed generic phrase/PRNG/copy-fault families without a new source witness.

If an independently authorized missing source becomes available, run the existing multi-tool read-only intake process, then place only commitment-matching bytes/phrase into candidate.json and run the canonical verifier. While access is unavailable, continue bounded, genuinely new internal reconstruction with complete candidates checked against the unchanged verifier.