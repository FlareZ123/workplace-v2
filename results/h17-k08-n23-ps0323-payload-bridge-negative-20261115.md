# K08 N23 → PS-261003-0323 payload bridge: scoped negative

**Date:** 2026-11-15  
**Identity:** Agent 5  
**Status:** no K08 commitment hit; native job/source relationship remains unverified

## Question and source relationship

N23 says the final wording was in Emily's margin and that the envelope remembers the words she finally put on it. Agent6 identified PS-261003-0323 as a possible structural locator because the note number and job suffix align; the spool row is a RECOVER/store job. This is not an authenticated join: no native queue/job manifest or collection record binds N23 to PS-0323.

The only local PS-0323 row is attempt 1, ACK, RECOVER/store, timestamp 2026-10-03T08:55:00Z, payload:

`1E51EFD2E5CA8F4E1FC8B49297B3D74F`

The K08 route requires the first 16 bytes of HMAC-SHA256 under the decoded desk nonce, over the normalized UTF-8 final phrase; the acceptance check is SHA-256 of that 16-byte component.

## Bounded tests

1. **Payload-is-component hypothesis.** If the local PS-0323 payload were the K08 component, SHA-256(payload) would equal the K08 slot commitment. It does not:
   - SHA-256(payload): `6edf08df2bdea3571b88886e7322234c97b4595f95b53db25bbf19c6dd92e95e`
   - K08 commitment: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`

2. **128-bit mnemonic hypothesis.** As a small secondary test, treated the 16-byte payload as BIP39 128-bit entropy using the repository English wordlist. The resulting phrase was `bundle month visa slide pottery poem left bird myth rural volume paddle`. Applying the exact K08 nonce/HMAC/UTF-8 route gives component `5D15029F75534D2AD13D15569FDFD5A0`; its SHA-256 is `b0087a863258fbc07d175028dcabb00cd0e046b000e31f763a3dfd80ee38593d`, not the K08 commitment. This is only a bounded encoding test, not evidence that the intended caption is a mnemonic.

Minimal reproduction for the direct test:

```python
import hashlib
payload = bytes.fromhex("1E51EFD2E5CA8F4E1FC8B49297B3D74F")
assert hashlib.sha256(payload).hexdigest() == (
    "6edf08df2bdea3571b88886e7322234c97b4595f95b53db25bbf19c6dd92e95e"
)
assert hashlib.sha256(payload).hexdigest() != (
    "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
)
```

## Evidence and limits

- `noticeboard-and-desk-notes.txt` SHA-256: `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- `spool-reconstruction.log` SHA-256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- `recovery-routing.json` SHA-256: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- `acceptance.json` SHA-256: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`

This rejects only the local payload-as-K08-component and BIP39(payload) hypotheses. It does **not** reject the possibility that the absent native PS-0323 .SPL/.SHD or rendered physical output contains the final words. It does not authenticate the N23↔0323 mapping. No K08 words or accepted component bytes were recovered; the canonical candidate was not changed.
