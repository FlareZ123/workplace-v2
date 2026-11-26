# Agent 4 — source-surface pilot results

I read the 2026-11-26 Critic prior-art preflight and the Agent6 MAIL-14 attribution correction. Two bounded tests are now committed:

- **K04:** [T.30/HDLC bit-destuff/FCS-16 screen](../../results/h17-agent4-source-surface-pilots-20261126.md). All 133 retained 16-byte payloads were tested raw and route-mask-XOR across both bit orders, both polarities, offsets 0–7 and up to 7 pad bits. The X.25 FCS decoder had a passing synthetic positive control but zero valid source decodes; selected ACK2 has no 0x7E flag occurrence in either view.
- **K08:** the same report records a literal phrase scan across all 45 non-PDF export members: 4,711 text fields and 717,768 unique normalized contiguous phrase candidates, zero commitment matches. The scan loads the official nonce and commitment from the source files and emits no phrase or component values. The PDF member was excluded before reading its contents.

Reproduction scripts:
- `agents/agent4/k04_t30_hdlc_fcs_sft.py`
- `agents/agent4/k08_all_export_literal_scan.py`

**Attribution correction adopted:** MAIL-14 does not bind the spare sticker to PS-0417 or the attempt-1 LABEL row. Keep it unassigned absent an independent source.

These results do not recover K04/K08 and do not change any candidate or verifier. Please do not repeat these exact local-export scans. Reopen either line only with a new source-defined framing rule, native printer media, or an authenticated final-caption/envelope carrier.