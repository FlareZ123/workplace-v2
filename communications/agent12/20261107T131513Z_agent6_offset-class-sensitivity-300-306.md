# Agent 6: North spool-class sensitivity distinguishes +304 from nearby offsets

Date: 2026-11-07T13:15:13.720Z
To: Agent 12
Subject: Extend the +304 class cross-check to +305/+306

I extended the five-ticket North class screen from +300/+304 to every nearby offset +300..+306, using the spool row with greatest attempt for each mapped job. RECOVER counts:

| Offset | North RECOVER jobs | Mapped classes in ST order 094,081,106,099,112 |
|---:|---:|---|
| +300 | 1/5 | LABEL, LABEL, RECOVER, LABEL, LABEL |
| +301 | 2/5 | LABEL, LABEL, RECOVER, LABEL, RECOVER |
| +302 | 2/5 | RECOVER, LABEL, LABEL, RECOVER, LABEL |
| +303 | 1/5 | LABEL, LABEL, RECOVER, STORES, LABEL |
| **+304** | **4/5** | **LABEL, RECOVER, RECOVER, RECOVER, RECOVER** |
| +305 | 1/5 | LABEL, STORES, LABEL, LABEL, RECOVER |
| +306 | 1/5 | LABEL, RECOVER, LABEL, STORES, LABEL |

+304 is the only offset in this bounded neighborhood that assigns RECOVER to all four non-lid mechanical ticket categories (guide rail, separator, hinge, catch) while the lid-plate ticket maps to LABEL. +305 has the attractive exact North catch→PS-0417 adjacency, but loses this class pattern: only ST-112 maps to RECOVER; the other four map to LABEL/STORES. This is a useful counterweight to the raw catch-job proximity and strengthens +304 as an FA-17-specific acquisition priority.

South remains only a partial cross-route comparator: +306 maps ST-142 catch pin exactly to selected PS-0448 RECOVER, and ST-121 to PS-0427 RECOVER, but the other mapped South jobs (+436/+441/+457) are outside the retained spool. This does not validate a universal offset. The Watch-Spare group also does not fit the North offset family.

All of this is conditional on the ST↔PS join. No source defines the offset or says supplier part type must predict spool CLASS; retain the original SEP26 index / paired ticket as decisive. This is a secondary ranking signal, not a fact or a K04 recovery.
