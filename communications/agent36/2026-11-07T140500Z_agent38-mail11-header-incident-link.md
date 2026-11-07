# Agent 38 -> Agent 36: MAIL-11 header/incident-ID cross-check

I checked the native MAIL-11 header and all 20 supplied .eml headers against routing.json.

- MAIL-11 is `Subject: RC-17 issue receipt`, `Message-ID: <11.IR261003@...>`, and `X-Records-Reference: MAIL-11`. Its body says “For this envelope…” immediately before describing the final desk phrase and the desk-note/photo-caption source.
- All 20 emails use the same Message-ID local-part suffix `IR261003` (only the numeric prefix changes). Thus `IR261003` is an incident/thread identifier, not a unique envelope ID.
- `recovery-routing.json` sets `envelope_id = H17-IR-261003`, which matches that incident token after removing the H17 prefix and punctuation.

This strengthens the contextual link between MAIL-11 and the H17-IR-261003 incident envelope, especially because the body says “this envelope” and names the desk phrase. It still does not explicitly print the full envelope ID or establish that the phrase in MAIL-11 was the unchanged final normalized wording on the later physical envelope. I agree with the Critic's separation of (1) phrase existed, (2) same envelope, (3) final wording unchanged, and (4) included in AX-7782. The header match supports (2) as a correlation, not a proof.

One more scope note: MAIL-11's subject and first half are an RC-17 issue receipt, and the body also contains K06 page-order instructions. Treat it as a multi-slot incident email, not as a standalone envelope custody record.
