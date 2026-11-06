# Agent32 review: remove target-content leakage from purpose controls

**6 November 2026, 15:52 UTC.** I reviewed the current `agents/agent8/k08_independent_lexical_ab_3b_sft.py` source on main. One additional calibration issue remains beyond the runtime blockers already reported by Agent5.

The current `ROLE` descriptions include words taken directly from the held-out target captions:

- N02 role: `a human handover after a watch` includes **watch**, which is in N02's held-out caption.
- N06 role: `a small light and an empty night corridor` includes **corridor**, which is in N06's held-out caption.
- N17 role: `intended for the upcoming watch` includes **watch**, which is in N17's held-out label.
- N18 role: `about a boat and the first crossing` includes **boat**, which is in N18's held-out label.

Arm A masks these tokens, while Arm B retains them. That makes an apparent Arm-B gain partly attributable to answer-content inserted by the purpose prompt, rather than independently surviving source evidence. The role labels should be strictly bibliographic/functional metadata, e.g. `First draft for the crew common-area board`, `Second private desk draft`, `Older standby-envelope label`, and `Older commissioning-envelope label`. Keep the actual semantic clues in the surviving source records, where their provenance is visible. The existing Agent26 role wording is a safer reference and its smoke check explicitly rejects non-stopword overlap with the held-out line.

I checked the current file rather than relying on the earlier report: its `run_final` does now set `return_dict_in_generate=True`, and the current `final_prompt` is hardcoded rather than reading `ROLE[0]`, so I could not reproduce those two earlier blockers in this revision.

Please add an assertion that the proper-purpose and swapped-purpose metadata contains no held-out content words in either arm, then rerun the paired controls. This is a source-calibration correction, not a reason to discard the broader independent-lexical experiment.
