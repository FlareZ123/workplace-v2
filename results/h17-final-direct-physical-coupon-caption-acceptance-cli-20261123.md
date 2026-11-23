# H-17 direct final-record recovery: commitment-gated physical coupon + author caption intake

**Agent31 | 23 November 2026 | synthetic complete-key PASS; original six PASS, K04/K08 missing**

## Deliverable

The existing bulk native-source recovery in work/h17_complete_native_recovery.py scans new binary/multimedia sources. A custodian who recovers the **exact 16-byte original ESC-N coupon** and **complete author-final envelope caption** also needs a direct, deterministic and safe entry point. A portable standard-library CLI was created:

- Source: [agents/agent31/h17_verified_manual_intake.py](../agents/agent31/h17_verified_manual_intake.py)
- Positive/negative original-source tests: [agents/agent31/test_h17_verified_manual_intake.py](../agents/agent31/test_h17_verified_manual_intake.py)

Example (the coupon zeros and phrase here are placeholders, not real recovered data):

    python agents/agent31/h17_verified_manual_intake.py \
      --coupon-hex 00000000000000000000000000000000 \
      --caption 'Exact handwritten physical-envelope caption' \
      --output work/h17-final-verified.json

Use --root /path/to/export for the supplied original ZIP extraction. The CLI reads the canonical candidate and original untouched acceptance.json/recovery-routing.json, dynamically imports the exact original verify.py, and uses the original K04 physical-coupon XOR mask and K08 normalized HMAC-SHA256 first16 rule. **No final candidate is written unless all eight individual slots and the full original combined commitment PASS.** Writing uses exclusive creation, so it cannot overwrite an existing key. It rejects malformed coupon hex, empty captions, missing original controls, and nonmatching original commitments.

## Executed source checks and planted positive

The local original archive's six baseline components pass. Using the original disputed selected copied 18:02 ACK2 16 bytes (A9A9DC5731A5E2AE879C47215C2559D5) and N01 photograph caption (the sea looks different when you have finally finished your tea), the original verifier reports **K04 NO_MATCH, K08 NO_MATCH, six PASS, original combined NO_MATCH**, and the CLI declines to write. The copied buffer is not authenticated as a true physical coupon, and the N01 caption is not the final envelope inscription.

For an actual full positive-path test, one fixed synthetic 16-byte coupon (7B68DAAA4C2AE2D6A2C042B921315267) and source-styled synthetic caption were chosen. Only the temporary fixture's K04/K08 and combined commitments were changed to match them; the original six accepted key bytes, routing and verifier code were retained. The test reports 8/8 synthetic PASS, synthetic combined PASS, and writes the expected complete file. A repeated attempt to overwrite it fails; a wrong coupon in the same temporary fixture emits no accepted file. Invalid hex and blank captions fail. The original acceptance files were never modified.

## Required original input

An authorized copy of either the selected ESC-N physical print coupon (exact 16 bytes) or an original native print render that authentically yields those 16 bytes, AND the final author-inscribed recovery envelope phrase or traceable final notebook revision. Both are absent from the supplied 46-member preservation export. When they become available, the CLI immediately checks the complete recovery using original immutable commitments; it cannot mathematically infer the missing text or opaque coupon from old draft/copy fields. This is a **last-mile recovery capability, not a seventh authenticated recovered component**. Existing native acquisition parsers remain available for fresh spool/media rather than requiring this manual path.

No original evidence, route, acceptance, verifier, canonical candidate or facility system was altered.
