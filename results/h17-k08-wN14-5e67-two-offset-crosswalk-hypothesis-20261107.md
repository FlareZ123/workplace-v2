> **SUPERSEDED / RETIRED (2026-11-07 16:06 UTC):** The two-offset interpretation below is a false lead and must not be used for recovery or acquisition prioritization. MAIL-03 supplies signed WN-14 groups A=`049AAB2E` and C=`CD7C6023` from the ordinary duty sheet. MAIL-06 supplies the remaining signed groups B=`1CDE7A82` and D=`4303C91A`; it explicitly says the old standby transcription's group-D suffix `5E67` is **not** the value on the signed sheet and that the duty register is authoritative. The signed A/B/C/D join is `049AAB2E1CDE7A82CD7C60234303C91A`; its SHA256 is `346d1643b6aaca7d0507e664b091a4c83575f6d67128ac17e583408ac07c3f0d`, exactly the K01 acceptance digest. Therefore `5E67` is neither a signed group value nor a source-defined offset. The +94/+103 arithmetic is an incidental alignment produced by using a stale, explicitly rejected standby value. Do not request PS-0426 or HST seq226 on the strength of this hypothesis. The independent HST seq+200 and N23→PS-0323 associations retain their own caveats; this correction does not validate or invalidate them.

# H-17 WN-14 5E67: two-offset crosswalk hypothesis

**Date:** 2026-11-07  
**Author:** Agent 11  
**Status:** RETIRED false lead; superseded by the signed-register evidence above.

## Question

Could the unsigned WN-14 standby suffix `5E67` identify two missing HST-4 records through the newly identified N23-to-spool and HST-to-spool index alignments?

## Source facts

1. MAIL-06 records a standby WN-14 transcription whose group-D suffix ends `5E67`. The same message distinguishes that standby transcription from the signed duty register. The signed register and the provenance of the standby transcription are absent from the local export. The suffix is not an accepted WN-14 component.
2. The 24-note crosswalk in `results/h17-k08-note-spool-sequence-crosswalk-20261107.md` maps N01–N24 to PS-261003-0301–0324 at exact five-minute intervals. This is a strong structural association, but no source field explicitly states Nxx→PS-(0300+N). N23 therefore has a candidate job locator PS-261003-0323.
3. The HST-4 crosswalk in `results/h17-hst4-pv-spool-job-crosswalk-20261107.md` maps all 112 PV sequence values 100–211 arithmetically to spool suffixes 0300–0411 using `job suffix = seq + 200`. This alignment is exact in the surviving export, while its source meaning remains unproven.
4. Combining those two candidate joins places N23/PS-0323 at HST PV seq 123.

## New arithmetic alignment

Interpret the two hex bytes of `5E67` as decimal offsets:

- `0x5E = 94`
- `0x67 = 103`

Applied to the N23 anchor HST seq 123:

| Candidate offset | HST seq | Implied spool job | Significance |
|---:|---:|---:|---|
| +94 | **217** | **PS-0417** | Selected K04 job identity |
| +103 | **226** | **PS-0426** | Missing job/HST row; route unknown |

The first offset lands exactly on HST seq 217, which the existing HST/spool crosswalk associates with the selected K04 job PS-0417. The second lands on seq 226 / PS-0426.

There is a broader range alignment. Applying +103 to the note anchors N09–N24 (HST seq 109–124) yields HST seq **212–227**, exactly the 16-record tail absent from the HST-4 PV export. Applying +94 to N18–N24 yields seq **212–218**, the first seven rows of that missing interval. N23 specifically maps to seq 217 and 226.

This is a surprising cross-source alignment and gives a concrete reason to prioritize seq 217 and 226 when the original HST export is recovered.

## Bounded falsification and limitations

- The two offsets do **not** describe a same-note reprint stream in the surviving spool metadata. Across the available offset-94 and offset-103 job ranges, later jobs do not preserve the original note job's CLASS or DEST, and their 16-byte payloads are all different. This weakens a literal “same note reprinted at +94/+103” interpretation.
- The `5E67` suffix is from an unsigned standby transcription. No source defines its bytes as sequence offsets, job offsets, page/word coordinates, or any other index.
- The N23→PS-0323 association is inferred from exact numbering and five-minute timing. The HST seq+200 mapping is an exact arithmetic relation in the surviving rows, but its operational meaning is unproven. The combined mapping therefore remains inferential.
- PS-0323 has no source-preserved queue/host/device assignment. MAIL-16 says ESC-S is not an input to K08 and WATCH-SPARE is unrelated; do not infer that PS-0323 belongs to ESC-N or that its paper was collected.
- The PS-0323 16-byte payload is not itself the K08 component: SHA256(`1E51EFD2E5CA8F4E1FC8B49297B3D74F`) is `6edf08df2bdea3571b88886e7322234c97b4595f95b53db25bbf19c6dd92e95e`, which differs from the K08 acceptance commitment.
- This interpretation does not supersede the low-confidence page-94/word-103 hypothesis or prove it. It is an alternative use of the same unsigned suffix.

## Highest-value discriminating evidence

1. Original HST-4 seq 212–227, with all fields and raw representations. Prioritize seq **217** and **226**, while preserving the full interval to test continuity.
2. Original signed WN-14 duty register and the source/provenance of the standby group-D transcription ending 5E67.
3. Original PS-0323, PS-0417, and PS-0426 job objects and route/queue/host manifests. Keep the note, HST, and print joins separate until a native identifier or manifest ties them together.
4. If PS-0426 is linked to ST-121 or an L-29/S return, obtain the original ticket/index rather than relying on an arithmetic ST/PS offset.

## Conclusion

The `5E67 → (+94,+103)` interpretation is a useful **locator hypothesis**, because its offsets land on two records inside the missing HST tail and the +94 target is the selected K04 job. The same evidence does not establish that the suffix was intended as offsets. Preserve the hypothesis for targeted acquisition; do not use it to populate candidate.json or assert either missing component.
