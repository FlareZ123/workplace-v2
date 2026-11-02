# K04: eight-distinct-recorder-donor MT reconstruction, exhaustive negative

**Agent 9 | 2 November 2026 | K04 unresolved.** The source-pinned reconstructed printer coupon from ESC-N job PS-261003-0417, RECOVER ACK2 at 18:02, has no independent integrity certificate. This experiment constructs full replacement coupons from independent original recorder source fields, and uses only the unchanged K04 slot SHA-256 commitment at the final stage. The disputed selected printer payload and all original accepted keys are withheld from candidate construction.

## Source model

Previous v1 source analysis found exact MT19937 recurrence matches between independent original TRP2 recorder four-byte controls and surviving printer output words, including the ordered recorder quartet 28,17,72,45. Under a speculative shared-source-state model, a candidate untempered output word equals M XOR MT_twist(hi, successor_low31). Each candidate word therefore needs a full 32-bit middle-state word, a 31-bit successor-state word and one unknown predecessor high bit. The final printed 32-bit word is tempered, written little-endian and XORed with its original K04 route-mask word.

This scan chooses four distinct middle and four distinct successor source records, eight distinct control records total, from the original TRP2 archive-latch cohort (node49/event82), preserving each original four-byte control. All sixteen predecessor-highbit patterns are checked. This tests a complete 16-byte source construction that is different from v1's 88,804 naturally ordered four-word source windows and its 43,680 direct four-control copy permutations. Actual event-stage source-index provenance is missing, so the donor assignment is only a hypothesis.

The original TRP2 SHA256 is 5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba. The K04 original XOR mask is 8556C8CB6140A7F9A5123AC7571BEE1C, original acceptance digest 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0. Sixteen labelled original four-byte recorder controls exist in the chosen cohort; twelve have valid CRC32, and original rows 14, 41, 72, 77 have invalid CRC32. The damaged controls are permitted **only as raw source bytes** for the second exploratory search; their bad-CRC records are still excluded from the official K05 reduction.

## Exhaustive completion

| Donor cohort | Permutations of eight distinct sources | Highbit patterns | Full source-derived K04 SHA256 tests | Original matches |
|---|---:|---:|---:|---:|
| 12 CRC-valid original controls | 19,958,400 | 16 | **319,334,400** | **0** |
| All 16 original raw controls | 518,918,400 | 16 | **8,302,694,400** | **0** |

The all-16 set contains the valid-only set. Both individual executions processed their exact expected factorial count. Synthetic OpenSSL SHA256 (high-level full message) versus SHA256_Transform (one-block compression) full-256bit control passed. Actual full 16-record run completed in 126.30 seconds using five C/OpenMP workers. The CRC-valid run completed in 4.86 seconds. Original progress output ended with:

    synthetic_SHA256_Transform=PASS
    mode=valid donor_count=12 checked=319334400 expected=319334400 matches=0 elapsed_sec=4.86
    mode=all donor_count=16 checked=8302694400 expected=8302694400 matches=0 elapsed_sec=126.30

**Reproducer:** [original-source-labelled, self-checking C/OpenSSL scanner](../agents/agent9/k04_eight_recorder_mt_sft.c) embeds exactly the sixteen recorded controls, their CRC qualifiers, original mask and SHA256 target, with both exhaustive modes. It does not write evidence, commitments or recovered candidates. Independent original-source checkout can regenerate the controls from evidence/recorder/trip-recorder.raw, schema offset12 four-byte raw control and CRC32 over the first20 bytes of each 24byte record.

## Scope

This excludes **only** the defined eight-distinct raw TRP2 archive-latch donor / standard MT19937 full-word recurrence / original mask interpretation. It does not exclude unobserved donor words, different physical/copy provenance, a different generator or different source placement. Broad free assignment grants no independent historical ranking of the candidates. No actual selected K04 bits or K08 author-final words were recovered. Canonical K01/K02/K03/K05/K06/K07 remain individually PASS, K04/K08 remain MISSING, combined REC8 INCOMPLETE and accepted=false.

Companion new source-only experiment: [K02 telemetry halfwords against printer MT three-word ancestors](h17-k04-k02-freeze-mt-three-word-bridge.md), also zero links under its specified model.
