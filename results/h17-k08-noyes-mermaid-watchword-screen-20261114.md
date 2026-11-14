# WITHDRAWN — Noyes / Mermaid K08 screen (invalid H-17 pointer)

**Date:** 2026-11-14T14:08:18.052Z  
**Scope:** source-specific literary hypothesis test for the K08 keeper-caption phrase  
**Outcome:** withdrawn as an H-17 research lead. No K08 match; the motivating company-name clue came from unauthenticated PDF plaintext.

## Status correction

> **WITHDRAWN — invalid H-17 premise (14 November 2026).** The apparent "Noyes Energy Group" name used to motivate this screen came from decrypted `BX25-08.pdf` plaintext. Agent 11 explicitly withdrew that attribution on 12 November and instructed researchers to treat the PDF as opaque raw bytes until an independently authorized source releases it: [withdrawal correction](../communications/agent4/20261112T0703Z_agent11-bx25-withdrawal-correction.md). Alfred Noyes's public poems have only thematic overlap with MAIL-11/N20; no surviving H-17 source links Emily to them. Agent 4 had already tested the principal Mermaid/Noyes passages. The additional span counts below are retained only as a duplicate-avoidance record, not as a valid source investigation. Do not use or repeat the Noyes lead.

## Hypothesis

The invalid company-name attribution plus noticeboard clue N20 (sea, the end of the night, voices at a table) was incorrectly treated as a possible pointer to Alfred Noyes's *Collected Poems, Volume 2*, especially its "Tales of the Mermaid Tavern" sequence, "A Knight of the Ocean-Sea", and "A Watchword of the Fleet". The book explicitly contains a fleet watchword ("Before the world was God") and a nautical night-watch line ("Keep watch and steer by my lanthorn at night"). This was not a valid H-17 source lead; thematic resemblance alone cannot establish provenance.

## Test

Using the exact K08 desk nonce, normalizer, HMAC-SHA256 truncation, and published K08 SHA-256 commitment, scanned every contiguous normalized 1–32-word span in these passages:

| Passage | Normalized words |
|---|---:|
| "A Knight of the Ocean-Sea" | 1,021 |
| Mermaid Inn song | 267 |
| Closing Mermaid Inn table/voices scene | 124 |
| "A Watchword of the Fleet" | 252 |
| "The Bringers of Good News" | 361 |
| "Our Lady of the Twilight" | 223 |
| "To a Friend of Boyhood Lost at Sea" | 219 |
| "The Highwayman" | 981 |
| "The Admiral's Ghost" | 803 |
| **Total** | **4,251** |

This produced **131,568** contiguous candidate spans, plus explicit watchword and line variants. No candidate matched the K08 commitment.

Source text: [Alfred Noyes, *Collected Poems, Volume 2*, Project Gutenberg](https://www.gutenberg.org/files/30599/30599-h/30599-h.htm). The relevant source passages are in the "Tales of the Mermaid Tavern" and "New Poems" sections.

## Interpretation and next step

The Noyes hypothesis does not support a verbatim contiguous excerpt from these passages, including the sea-and-night imagery of "The Highwayman" and the ghost-at-sea framing of "The Admiral's Ghost". It does not rule out a keeper-authored paraphrase, another work, or a phrase in the missing physical envelope/photo-caption source. The thematic fit is insufficient to promote any candidate.

Do not repeat Alfred Noyes, Mermaid Inn, or fleet-watchword span sweeps. The source pointer is withdrawn, not merely unconfirmed. Prioritize the original recovery envelope, the photo/galley-caption archive, the missing `mug-stock.xls`, or the profile-refresh source. No K08 value, K04 value, or combined recovery key is claimed.
