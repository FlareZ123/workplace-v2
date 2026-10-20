# H-17 REC8/1: precise request for missing preservation evidence

**Prepared:** 2026-10-20 UTC. **Purpose:** Finish the original eight-component recovery without fabricating bytes or modifying the verifier. This is a records request, not an equipment-action instruction.

## Already recovered
K01, K02, K03, K05, K06, K07 independently pass their original SHA-256 commitments. See [current recovery index](README.md) and [reproducible recovery report](agent3-six-validated-components.md). The official acceptance output for the six-value partial candidate is `passed=6`, `combined=INCOMPLETE`, `accepted=false`.

## Missing record A: K04 coupon payload
- **Exact logical route:** `ESC-N`, incident-date September mapping to `PS-261003-0417`.
- **Relevant printer event:** 2026-10-03 18:02 UTC, `ATTEMPT=2 STATE=ACK CLASS=RECOVER`.
- **Problem:** surviving printer reconstruction claims payload `A9A9DC5731A5E2AE879C47215C2559D5`. XOR with the supplied mask `8556C8CB6140A7F9A5123AC7571BEE1C` gives `2CFF149C50E54557228E7DE60B3EB7C9`, but the untouched K04 verifier rejects these derived bytes.
- **Source warning:** custodian note and MAIL-16 explicitly warn that dispatch ACK confirms a job, without confirming reconstructed payload byte integrity.
- **Needed:** an independently retained original coupon, verified 16-byte payload transcript, uncorrupted archival spool/source image, or authoritative printer-side checksum tied to this exact job and ACK attempt. Vendor/property register links `L-29/N` / `FA-17` / `H17-POL-17/A3` / scan `BX25/08` provide provenance only; the supplied scan does not contain the coupon bytes.

## Missing record B: K08 keeper's final caption
- **Owner of remembered wording:** Emily; personal late-watch desk/envelope caption distinguishing the keeper envelope.
- **Problem:** source N02/N06 are marked drafts and N17/N18 are explicitly older standby and commissioning envelope labels. MAIL-11, MAIL-20 and N23 distinguish a final wording that the surviving export does not reproduce.
- **Needed:** the final keeper-envelope label, photograph with legible signed caption, original desk notebook margin, or complete correspondence that records Emily's exact final wording. A thematic paraphrase of the sea, night, lamp, cups or room at the table cannot independently establish the HMAC input.
- **Available check:** the original normalization and HMAC procedure is in `resources/evidence/recovery-routing.json`; the immutable acceptance is `resources/acceptance.json`.

## Source retrieval boundaries
The BX25/08 policy-annex scan points to a Noyes Energy Group website. Public pages provide no incident-archive evidence. Its partner/employee correspondence portal requires a normal account sign-in. The current export provides no account records or credentials. Please supply any additional correspondence as an authorized downloaded export or credentialed source you are entitled to share; do not request an authentication bypass.


## Additional original-source locator
The surviving `retired-office-bookmarks.html` explicitly names `file:///R:/Records/INDEX/IR-261003-H17.txt`, an *original Windows mapped-drive incident desk index*. That source file is **not supplied** with the export. A preserved authorized copy of this exact historical file and the record paths it indexes should be requested from the records custodian. The pointer alone neither establishes the file's original date nor contains missing component bytes. The previous workspace tested four related anonymous public URLs and received 404; the Windows `R:` path is distinct from those URLs. See [predecessor source-addressed intake](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-missing-evidence-intake.md).

## Research-prior-art gate
Predecessor repository [workplace-v1](https://github.com/FlareZ123/workplace-v1/blob/main/results/README.md) contains extensive analysis of the *same original archive*, including [two independent exhaustive three-byte K04 correction sweeps](https://github.com/FlareZ123/workplace-v1/blob/main/results/h17-k04-three-byte-bound.md) with **9,285,570,000 variants each and zero match**. A redundant v2 matrix was cancelled after this prior work was discovered. The research frontier remains additional actual K04 source bytes or verbatim K08 words. See [v2 cross-repository gate](h17-v1-prior-art-gate.md).

## Acceptance procedure
Once authentic missing evidence becomes available, derive 16-byte K04 and K08 candidates under the original route rules, check each via the **unchanged** `resources/verify.py`, and require all eight individual `PASS` results plus `combined=PASS` and `accepted=true`. Until then, report the combined recovery key as **unverified**.
