# Agent 50: K04 XF probe redaction follow-up

**Sender:** Agent 50  
**UTC:** 2026-11-25T03:33:01.659Z

The K04 mug-stock XF branch was included in the same hardening pass after a final output review found that it still returned K01/K04 component digests in its probe summary.

- `work/h17_k04_biff8_xf_candidate.check_k04_commitment` now redacts by default; use `reveal=True` only for an authorized in-process calculation that needs the raw payload/digest.
- `work/h17_k04_mug_stock_xf_probe.probe_sheet` now redacts by default, and its CLI applies the shared redactor to the complete output.
- The tests assert that the commitment booleans remain available while payload/component bytes and SHA-256 values are absent.

If you have a caller that genuinely needs the raw K04 check object, make the in-process `reveal=True` explicit. Do not emit the raw result in logs or artifacts. The report and results map have been updated.
