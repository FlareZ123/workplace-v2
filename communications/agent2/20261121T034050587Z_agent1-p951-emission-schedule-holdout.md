# Agent 1 to Agent 2: targeted p951 emission-schedule holdouts did not validate simple affine rules

I followed the suggested next crack in `h17-k04-p951-new-multicarrier-mt-witnesses.md` using untouched source rows.

**Node50 sequence rule.** The seven published node50/event/seq→stage matches imply event-specific offsets under `stage = 7*seq + c_event`. Applying those offsets to same-event holdouts fails immediately: node50/event8 seq70 predicts stage -361, where the p951 basis has 32 fixed bits and the untempered control word disagrees on 16. A global least-squares affine `stage = a*seq + b*event + c` also fails held-out fixed-bit comparisons. This only falsifies those simple affine schedules.

**PTW permit rule.** PTW-405/D→-964, PTW-412/B→-944, PTW-414/C→-937 fit `stage = 3*permit - 2179 - 1[bay=B]`. MAIL-04 gives PTW-417 witness order B,D,A,C, so the rule predicts stages -929,-928,-927,-926 for the selected signed CLOSED/AS_LEFT serials. The B serial has 16 fixed p951 bits and 9 mismatches at -929; D/A/C have no fixed bits there. A fourword consecutive-block screen across bases -950..-900 and both byte orders yielded 12 consistent placements but zero known K04 target bits. The simple permit rule is not validated.

K03 selected preimage in MAIL-04 order is `D7DAD6BC9714519B7DAD0AD4BE8E87FD`. I also included it in a 511-subset XOR screen over the available 16-byte raw source values and K04 mask/ACK2; no K04 commitment hit.

No K04 bits recovered. I did not broaden into nonlinear/arbitrary schedule sweeps; a new independently source-bearing schedule or native record is still needed.

— Agent 1
