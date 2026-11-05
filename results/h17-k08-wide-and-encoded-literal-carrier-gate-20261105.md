# H-17 K08: original-source wide and encoded literal carrier gate

**Agent 8 | 5 November 2026.** A directly target-reaching, **source-carrier** search across ten intact textual encodings of a final keeper inscription. **No encoded final text was recovered**, and no original K08 component passes. This deliberately avoids enlarging free-form natural-language caption grammars.

## New observation channel

The original local export contains 42 evidence files. Prior K08 carrier analyses tested raw ASCII strings, one-byte XOR/ROT13 masks, source-derived pads and repeating-key transforms. Here the distinct hypothesis is that an exact author-final caption was exported intact through **a conventional text encoding**, and so was not visible in ordinary source-literal scans. The source never says such a transport happened; this is a bounded plausible representation screen for historical office documents.

The original crew-note SHA256 is `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`. All 42 original evidence files were read directly from the supplied ZIP extraction; no original was rewritten. The K08 route's genuine binary desk nonce is `5F933DA6A1BD03C32DA5CBC25344F497`; original slot SHA256 target is `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

Every candidate text is normalized with the original ASCII rule, HMAC-SHA256 keyed by the true nonce, first 16 MAC bytes retained, then SHA256 of the retained 16 bytes is compared against the untouched original slot commitment.

## Two independent literal transport screens

**Wide-character original bytes:** Examine every byte offset in every evidence file for contiguous UTF-16 LE, UTF-16 BE, UTF-32 LE or UTF-32 BE source runs representing at least 16 printable ASCII characters (including permitted line whitespace). Decode and check every contiguous normalized two-through-32-word span, deduplicating within each file.

```text
SOURCE_FILES 42 ORIGINAL_WIDE_RUNS 0 COMPLETE_CANDIDATES 0
ORIGINAL_K08_MATCHES 0 SYNTHETIC_POSITIVES 4
```

**Encoded text payloads:** Independently examine original byte streams for complete 16-character-or-longer printable ASCII runs in six conventional encodings: contiguous hex, Base64, Unicode `\\uXXXX` escapes, percent/URL escaping, HTML numeric or named entities, and MIME quoted-printable including soft line wrapping. Enforce recognizable format features, such as multiple escaped bytes for escaped formats, then decode and apply the same complete K08 acceptance to all contiguous two-through-32-word spans.

```text
ORIGINAL_FILES 42 PRINTABLE_DECODED_RUNS 0 COMPLETE_PHRASE_CHECKS 0
ORIGINAL_K08_MATCHES 0 SYNTHETIC_CONTROLS 6
```

An original source text under the precise **ten tested format grammars** would be found if it survived intact as a full length-16+ printable run and matched the chosen syntactic extraction. Neither test found an authentic qualifying run, so neither can supply a final-caption candidate from the surviving export.

## Full positive controls and reproducer

For all four wide formats and all six encoded formats, a **separately planted full 69–76-character caption** encoded in the given format was detected, extracted and matched against a separately constructed synthetic K08 HMAC16/slot SHA256. Each SFT also verifies the original N02 known draft HMAC prehash `BF889359B0303F2B2B2FD96AE841210B` using the actual nonce, and authenticates the original crew-note SHA pin.

- [Four-codec wide literal SFT](../agents/agent8/k08_wide_character_literal_sft.py), standard Python only.
- [Six-codec encoded literal SFT](../agents/agent8/k08_encoded_literal_transport_sft.py), standard Python only.

Both were executed against the local original 42-file evidence tree. File paths are arguments, defaulting to `resources/evidence/`. There is no original-target tuning or phrase guessing.

## Scope and decision

This is a **positive-capability, negative-source** test. It excludes intact simple wide text and a finite list of unencrypted/ordinary escaped representations within the original local evidence files. It says nothing about encrypted, compressed, fragmented, custom-encoded, shorter-than-16-character, external or destroyed author-final inscriptions, including the physically worded final envelope. It does not recover any K08 word or reveal a human-authenticated source of the final selection.

A new K08 study should focus on **the author-final physical or contemporaneous custody witness**, and any new transport hypothesis should first identify why that encoding or source location is expected. Known N17/N18 labels and N02/N06 drafts are not the terminal keeper inscription.

Original REC8 state remains **K01/K02/K03/K05/K06/K07 PASS, K04/K08 MISSING, combined INCOMPLETE**. The original ZIP, route, acceptance and verifier remain unchanged.
