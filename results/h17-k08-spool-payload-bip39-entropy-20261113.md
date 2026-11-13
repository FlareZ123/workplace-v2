# K08 spool-payload BIP39 entropy test

**Date:** 2026-11-13  
**Agent:** 3  
**Status:** Bounded source-motivated constructor; zero K08 commitment hits.

## Hypothesis

A 16-byte retained print payload could be 128-bit BIP39 entropy for a 12-word phrase. This is a plausible but unauthenticated encoding hypothesis for the physical shelf-card / final-envelope print path. The candidate phrase is then checked using the original K08 route, rather than accepting the mnemonic on appearance.

## Method

- Pinned the official BIP39 English 2,048-word list at agents/agent3/data/bip39-english.txt.
- Converted each of the 133 retained 16-byte spool payloads directly, in logged byte order, into a standard 12-word BIP39 mnemonic.
- Normalized each phrase using the exact K08 route rule.
- Computed HMAC-SHA256 with desk_nonce as key, retained the first 16 bytes, SHA256-hashed those 16 bytes, and compared against the unchanged K08 slot commitment.
- No byte reversal, seed search, word substitution, paraphrase, or additional mnemonic generation was used.

The two source-motivated print carriers were included:
- PS-261003-0300, LABEL / store: FBBBC54356483F5864BB3F06794518A5
- PS-261003-0323, RECOVER / store: 1E51EFD2E5CA8F4E1FC8B49297B3D74F

## Result

| Measure | Result |
|---|---:|
| Retained spool payloads | 133 |
| Unique 16-byte payloads | 133 |
| BIP39-128 mnemonic candidates | 133 |
| K08 commitment hits | **0** |

The target commitment was 285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747.

Reproduction:
- Script: agents/agent3/k08_spool_payload_bip39_entropy_sft.py
- Wordlist: agents/agent3/data/bip39-english.txt
- Workflow: .github/workflows/agent3-k08-spool-payload-bip39.yml
- Successful run: 43410950241
- Machine-readable output artifact: k08-spool-payload-bip39-entropy-sft

Input SHA-256:
- Spool reconstruction: 7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083
- Routing: f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5
- Acceptance: 681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f
- BIP39 English wordlist: 2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda

## Interpretation and boundary

None of the retained 16-byte spool payloads is the K08 HMAC16 output when treated as the entropy for a standard 12-word BIP39 phrase. This closes only the direct logged-byte-order BIP39-128 construction. It does not show that the physical card or final envelope is absent, nor does it authenticate any payload as the phrase's entropy.

Do not expand this into generic wordlist phrase generation. The useful next evidence remains the literal card/margin/envelope text or an authenticated native print job/document. No acceptance, route, candidate or verifier file was changed.
