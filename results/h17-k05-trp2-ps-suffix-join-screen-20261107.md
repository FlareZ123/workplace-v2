# TRP2 seq300–303 / PS0300–0303 suffix-join screen

**Date:** 7 November 2026  
**Owner:** Agent14  
**Status:** bounded negative; numeric join remains unauthenticated

## Question

The official K05 selector yields four CRC-valid archive-latch control words with TRP2 sequence numbers 300–303. The spool reconstruction also contains jobs PS-261003-0300 through PS-261003-0303. Does this exact suffix overlap establish a producer or selector relationship between the K05 control block and those four 16-byte spool payloads?

## Source facts

- The official `resources/work/recover_six.py` selects K05 from CRC-valid TRP2 records with node 49, event 82, timestamps in [2026-10-03 21:14:00, 21:14:08) UTC, choosing the greatest sequence per latch and concatenating latches 0–3.
- That selector produces seq300, 301, 302, 303, all at 21:14:02 UTC with AUX=4318. The official script does not define a join to printer job IDs.
- The spool reconstruction contains PS-261003-0300 through PS-261003-0303. Their logged job times are 07:00, 07:05, 07:10, and 07:15 UTC, approximately fourteen hours before the TRP2 latch event. The suffix overlap is therefore not a temporal join.
- HST4 PV seq100–103 also align arithmetically with these four spool suffixes under the proposed +200 offset. The HST4 export documentation does not define that offset as a per-record foreign key; it says `revision` is scoped to `(tag, field, seq)`, does not define `seq` as a global job identifier, and describes PV values/units as historian context rather than raw diagnostic words. The official six-component reproducer uses HST4 DIAG_WORD rows for K02, not PV rows for a printer selector.

## Method

The SFT pins `trip-recorder.raw` SHA-256 `5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba` and `spool-reconstruction.log` SHA-256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. It reselects the four K05 words from the raw TRP2 file using the official time/node/event/CRC/latch rule, then loads the four same-suffix spool payloads. It checks:

1. direct occurrence of any K05 CONTROL word, in either byte order, in any of the four spool payloads;
2. per-record CRC32, Adler32, MD5, SHA-1/256, BLAKE2s, and HMAC-SHA256 constructions over CONTROL, sequence, and AUX in bounded field orders;
3. CPython `random.Random` per-record seed forms derived from CONTROL, sequence, and AUX;
4. xorshift128 and xoshiro128** streams initialized directly from the 128-bit K05 block;
5. PCG32 direct state/increment and canonical initstate/initseq interpretations of the 128-bit K05 block.

The tested output alignments include both word byte orders and forward/reverse stream order where applicable.

## Result

All tested families produced zero exact matches. The four same-suffix payloads contain no direct occurrence of any selected CONTROL word. The SFT passed in GitHub Actions run [42396388676](https://github.com/FlareZ123/workplace-v2/actions/runs/42396388676).

## Interpretation and limits

The equality of TRP2 sequence numbers and spool suffixes is a real numeric overlap. It is **not an authenticated source relationship**. The official K05 selector is defined by recorder time, node, event, CRC validity, and greatest sequence per latch; it does not name a print job. The approximately fourteen-hour timestamp separation further rules out treating the four rows as contemporaneous events.

This screen excludes only the finite mappings listed above. It does not prove that no relationship exists, and it does not recover or select K04. Do not use seq300–303 as printer job identifiers, K04 donor state, or a K04 selector without an original queue/job manifest or commissioning record that explicitly defines the join.

## Reproduction

- Script: [`agents/agent14/k05_trp2_ps_suffix_sft.py`](../agents/agent14/k05_trp2_ps_suffix_sft.py)
- Official K05 source selector: [`resources/work/recover_six.py`](../resources/work/recover_six.py)
- TRP2 format: [`resources/evidence/recorder/format-note.txt`](../resources/evidence/recorder/format-note.txt)
- Printer evidence: [`resources/evidence/print/spool-reconstruction.log`](../resources/evidence/print/spool-reconstruction.log)
