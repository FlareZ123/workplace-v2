# K04 same-job XOR-delta state test (12 Nov 2026)

## Question and hypothesis

Could the three `RECOVER` payloads for `PS-261003-0417` be per-attempt XOR deltas to one mutable spool buffer, rather than independent full payloads? If so, the cumulative state at the last acknowledged attempt might differ from the recorded ACK payload. This is an exploratory event-sourcing hypothesis; no supplied source says the `PAYLOAD` field is delta-coded.

## Frozen source inputs

- `evidence/print/spool-reconstruction.log` SHA-256: `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`
- `evidence/recovery-routing.json` SHA-256: `f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5`
- `acceptance.json` SHA-256: `681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f`
- K04 mask: `8556C8CB6140A7F9A5123AC7571BEE1C`
- K04 component commitment: `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`

The three same-job `RECOVER` records are:

| Attempt | State | Payload |
|---:|---|---|
| 1 | REQUESTED | `CD3E4F216ADB2FB180DA2AA90B33F7A4` |
| 2 | ACK | `A9A9DC5731A5E2AE879C47215C2559D5` |
| 3 | REQUESTED | `44D53DFC29D7943A95D89371DA58EC64` |

## Complete candidate test

Constructed six 16-byte candidate states: each of (p_1,p_2,p_3,p_1\oplus p_2,p_2\oplus p_3,p_1\oplus p_2\oplus p_3). For every state, tested both the raw block and block XOR the source mask. Each candidate was checked by SHA-256 against the unchanged K04 slot commitment.

| Candidate | SHA-256 after XOR with mask |
|---|---|
| (p_1) | `b138a3b90d9cfab0f4994e3a38b354bf205265e2bafa2e29b01444b5dfae14ca` |
| (p_2) (route-selected ACK) | `11a7f6064781a6ac7678dc6dd24759af95981c8a927f8da4436515354d34549b` |
| (p_3) | `02402fd772d7c1dd9c62c90f66cc9b1ace9c593d6cbfa58fee96619fc5abeeaf` |
| (p_1\oplus p_2) | `49c75c8e9532d725d2cd8e6c04d768b3ff37ee5c89ff8db3225b8e68261583ad` |
| (p_2\oplus p_3) | `bcf5f48032eb05a72a67526c5d9b9e48b41fadeb772bf7c58302aa59b4c9cc56` |
| (p_1\oplus p_2\oplus p_3) | `f3532b1fd38612964527aae284b145a11f1e6cd2e9bd9ad5bcca518d43f251a0` |

None equals the K04 commitment. The six raw-block hashes also fail.

## Conclusion and scope

The simple same-job XOR-delta / cumulative-buffer hypothesis is rejected for these three recorded payloads. This does not establish that the export is integrity-checked, nor does it recover the physical coupon. The route-selected ACK2 block remains the only source-selected payload, but its masked candidate does not pass. Do not promote attempt1, attempt3, or cumulative XORs as K04. Further progress still requires an independently indexed copy-stage record or integrity-checked source object; do not expand this into a permutation or arbitrary delta sweep.

