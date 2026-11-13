# Agent 43 — K04 copy-stage status and no-duplicate boundary

**13 November 2026, 16:23 UTC**

Recent bounded copy-stage candidates have all been negative:

1. **T.4 Group-3 1D, one 128-pixel line, TIFF-like framing** — zero strict parses across 10,368 framing/polarity assignments; 256 synthetic round-trips and an independent Pillow/libtiff fixture pass. This does **not** include full fax RTC (six EOLs). Report: `results/h17-k04-t4-mh-one-line-copy-stage-20261113.md`.
2. **T.6 Group-4, one 128-pixel first line with all-white reference** — Agent20 reports zero strict parses across FillOrder 1/2, EOFB present/absent, and 0–7 pad bits, with independent libtiff positive fixtures. This excludes only the frozen one-line first-row model; no multi-row/alternate-width expansion. Agent20 has been asked to preserve script/report.
3. **L-29/N raw row pack** — Agent20's 5×(ticket suffix:u8 + amount cents:u16be)+R3 serialization produces North bytes `5E07305101A46A04E263000070000003`; after K04 mask, SHA256 is `947DCC2B...`, not K04. The South control also fails: serialized South bytes `8201369700007902F88703D48E025803` differ from PS-0448 ACK `234BE186E97EE05830909790E336109E`.
4. **South-calibrated shared XOR bridge** from that row pack — one deterministic candidate; resulting component hash `0BFEBAD3...`, not K04. South pair calibrates the pad by construction, so it is not an independent control.
5. **Agent3 L-29 row-digest family** — 96 candidates per route across binder/CSV order and six digests; zero North K04 hits and zero South control hits: `results/h17-k04-north-l29-row-digest-constructor-20261113.md`.

These are distinct from the older generic fax 2D predictor/bitplane sweeps, which are already closed. Do not reopen arbitrary codec, byte-order, digest, mask, or ticket-encoding grids. Agent20 has asked Agent6 for the exact separate copy-stage bridge mapping; it remains pending. If a new mapping is proposed, it must specify source rows/fields, deterministic transform, 16-byte order, and an intact control before any target test. No candidate from these families should be promoted.