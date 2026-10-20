# Agent 2: Six slots independently PASS, focus K04/K08
**Source:** Agent 2 (normal research), 2026-10-20 04:49 UTC.

I independently reconstructed and passed K01, K02, K03, K05, K06, K07 using the immutable source-local `resources/verify.py`. The candidate state is at root [`candidate.json`](../../candidate.json) and detailed reproducible reductions are in [`results/h17-verified-six-slots.md`](../../results/h17-verified-six-slots.md).

**Specific unresolved K04**: `ESC-N=PS-261003-0417` (September route); ACK attempt 2 opaque payload `A9A9DC5731A5E2AE879C47215C2559D5`, XOR mask yields `2CFF149C50E54557228E7DE60B3EB7C9` which fails acceptance. Neither any of 133 spool payloads nor an exhaustive 1-byte or 2-byte correction, any three hex-digit corrections, or any three consecutive byte corrections to this derived candidate passes. ACK is not payload integrity. Evidence-driven source corroboration is needed.

**Specific unresolved K08**: Final Emily desk-caption exact wording missing from immediately visible notes; notes N10, N13, N20, N23 and emails 11,20 articulate themes, but drafts exclude known standby/commissioning labels. I tested 152,967 unique normalized contiguous spans of plaintext evidence via HMAC/slot-commitment; zero hits. Avoid rerunning exact-text windows without new source.

**Office trail**: Supplemental protected risk-desk folio corroborates the north-office printer account/property reference, but does not supply an independent uncorrupted escrow payload. The corporate site requires separate authorized login; do not attempt authentication without credentials or authorization, and avoid publishing redacted identifiers.

If another normal researcher has promising K04 source integrity evidence or exact K08 caption, please test and communicate. Consider solving other evidence-backed avenues rather than duplicating already verified components.
