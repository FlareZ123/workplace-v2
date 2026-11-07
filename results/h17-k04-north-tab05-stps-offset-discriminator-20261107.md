# North tab-05 ST-to-PS offset discriminator

**Question.** Can the final L-29/N binder tab distinguish the competing ST-to-PS offsets (+300 and +304)?

## Source-derived inputs

- `print-fleet-retirement-note.txt` gives the L-29/N binder order. Tab 05 is `ST-112`, “catch clean.”
- `archive-labels.ini` resolves logical route ESC-N to `PS-261003-0417`.
- `spool-reconstruction.log` records the last ACK for each candidate job, including class.
- `recovery-routing.json` supplies the K04 XOR mask; `acceptance.json` supplies the K04 commitment.

## Result

| Candidate offset | ST-112 maps to | Gap before selected PS-0417 | Candidate job's last ACK class |
|---|---:|---:|---|
| +300 | PS-0412 | 5 | LABEL |
| +304 | PS-0416 | 1 | RECOVER |

The selected PS-0417 job's last ACK is also `RECOVER`. Thus +304 gives both a much tighter adjacency and a same-class predecessor. +300 gives a LABEL-class job five positions earlier. This is an additional discriminator for +304 beyond the previously reported PTW receipt and L-28 holdout comparisons.

## Important limitation

This does **not** authenticate the ST-to-PS arithmetic. No explicit mapping record in the supplied export says that an ST ticket maps to a PS job by adding 304. It is a source-consistent correlation and should raise confidence in +304, not be promoted to proof.

It does **not** recover K04. The PS-0416 last-ACK payload XOR the published K04 mask does not match the K04 commitment, so PS-0416 must not be substituted for the selected PS-0417 payload.

The equivalent South-route check is unavailable in this export: the candidate PS-0442 and PS-0446 rows are absent from the supplied spool reconstruction. Do not sort South tickets by numeric suffix to invent a binder order; the retirement note's tab order is the source order, and ST-151 is tab 02 / guide-shim credit, not the final tab.

## Reproduction

Run from repository root:

```powershell
python agents/agent38/st_ps_offset_discriminator_sft.py
```

The script reads only the five cited source files and prints both offset mappings, selected ACK classes, adjacency, and the K04 commitment check. It uses Python standard-library modules only.
