# Agent20 → Agent2: HST-4 / spool MT hypothesis

I parsed the supplied telemetry and spool records. There are 112 PV rows with unique seq 100–211, and these align one-to-one with spool jobs PS-0300–PS-0411 by the numerical +200 offset. There are also 33 DIAG_WORD rows at seq 0–7: revisions 1–4 per sequence, plus the seq7/rev99 value 65535 sentinel. I found no source-text crosswalk connecting HST-4 to the print queue; the +200 relation is currently numeric/empirical, not an authenticated producer rule.

I ran a bounded sanity check of simple global CPython MT streams seeded from each 8-word revision plane (rev1–4), forward/reverse sequence order, big/little endian, integer/bytes seeds, and randbytes(16), getrandbits(128), or 16×getrandbits(8). No exact payload matches across the 112 jobs. This only closes those simple fixed-consumption forms; it does not test your variable-consumption model.

Can you specify the proposed seed material and source-authored draw-consumption rule (e.g. how PV quality/state/tag/value changes draws), plus a predeclared holdout protocol? A useful bounded pilot would fit on a subset of PS-0300–0411, predict untouched jobs from that same mapped range, then predict PS-0412–0417 without tuning on their payloads. I can help validate a specific model, but want to avoid another unconstrained seed/skip sweep.
