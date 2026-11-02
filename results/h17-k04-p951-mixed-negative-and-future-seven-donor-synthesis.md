# K04 p951: complete mixed past/future native donor coupon reconstruction

**Agent39, 2 November 2026 ~22:20 UTC. New conditional seven-native-output configuration.** Reproducible [source-specific 224→128-bit affine coupon synthesizer](../agents/agent39/k04_p951_mixed_negative_future_coupon_sft.py). Selected original printer row129 is withheld before extraction; original acceptance is not consulted for this source-only target-reachability calculation.

The preceding [global future-output survey](h17-k04-p951-global-future-native-donor-pair-families.md) finds 46 seven-native-word portfolios composed entirely of future outputs. A distinct mixed-time construction lets one source-present **negative MT position** substitute for a future output:

```text
Original p951 MT native donor indices:
  future: 1178, 1179, 1180, 1181, 1347, 1574
  past:   -237

Original missing p951 MT native selected indices:
  951, 952, 953, 954
```

Treat the register at conceptual position -1100 as a free 624×32-bit native MT state, propagate forward under exact MT19937 recurrence and condition only on the 132 intact original printer packets. Source equations have rank **15,365**. The first three future donors 1179,1180,1181 determine **95/128** selected bits; adding 1347 and1574 determines **126/128**; adding native -237 increases to **127/128**; the sixth future donor1178 increases to **128/128**, yielding a complete reconstructed selected value if all seven independently indexed native donor contents become available.

There are **eight alternative positions** for the final future word, each reaching128 given the same other six donors: `1178, 1405, 1632, 2086, 2540, 3448, 3671, 4356`. Each substitution provides another complete seven-output mixed portfolio. These are mathematical placement alternatives, **not actual recorded output values**. This mixed model uses a legitimate unconstrained early MT origin for symbolic representation and explicitly does **not** conflate it with the CPython seeded initial register, avoiding the prior invalid-backward-prehistory trap.

Original printer-only source constrains `native X[-237]` at just **two bits** (bit0=1, bit31=0), leaving 30 bits absent, so the mixed configuration does **not** supply an original K04 bit. Even though this negative source position is temporally earlier than the missing print packet, the archived records do not independently authenticate any complete native MT word at -237. Neither the historical common producer nor the future donor schedules are established.

The SFT constructs an exact affine expression for all 128 selected native bits over the seven named 32-bit donor inputs, with an independently seeded arbitrary native-MT-state positive-control set of seven complete withheld selected-spool reconstructions. It pins the original spool SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. **No original physical coupon recovered; no authentic K04 byte and no K08 final author-word authenticated.** Official six PASS, combined INCOMPLETE.
