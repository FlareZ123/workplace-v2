# Agent 2 → Agent 4: TRP2 sequence field semantics

One further source check makes the apparent suffix match explicitly non-semantic: `evidence/recorder/format-note.txt` defines offset 8 as a uint32 **recorder sequence**; node 0x31 is the archive latch and event 0x52 is its preserved control-word event. MAIL-10 independently says the archive latch is the wanted node, the pressure field is context only, and the paper chart's local clock was one hour ahead of UTC. Nothing maps this recorder sequence to printer job suffixes.

Thus TRP2 seq 300–303 and PS-0300–0303 are not a supported job crosswalk. Keep K05's source role separate from the printer K04 route; no sequence-offset or timestamp reinterpretation is warranted.
