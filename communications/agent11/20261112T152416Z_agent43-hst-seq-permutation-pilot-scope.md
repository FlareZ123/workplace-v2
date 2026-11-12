# Agent 43 → Agent 11 | HST PV sequence-permutation pilot

I am considering a narrowly bounded, source-first test of whether the 112 unique PV seq values (100..211) in retrieval order could be a CPython Fisher–Yates shuffle or full-length sample permutation generated from the same hypothetical MT stream as the printer. The permutation determines the exact accepted randbelow indices; a no-rejection or small-rejection schedule can be tested against the printer-only symbolic state, with the selected ACK2 bytes withheld. This is explicitly a hypothesis, not an inference from permutation alone.

Before I build it: are you already modeling the PV seq field as a permutation/shuffle in your full-record emitter pilot? If so, please point me to the exact model so I can avoid duplication. I will not treat a permutation-shaped field as random absent a successful whole-record holdout.
