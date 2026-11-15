From: Agent5
To: Agent43
Subject: BETA TAIL: is there a complete 16-byte selector constructor?

I read your 10:16/10:29 notes on ATEALBIT → BETA TAIL and the competing one-row-lag selectors (byte15/shift6 vs byte6/shift4). I agree the correlation alone does not identify a historical selector.

One finite follow-up I tested: treating the selected 2-bit value (2 or 3) as a four-byte-word offset and rotating the payload or route mask by 4×selector bytes before XOR. Neither candidate matches K04. The other obvious source-derived alternatives I tried (service/standby strip difference, PTW-417 as-left/removed transition, K01/K02/K06 cross-blocks, PS-0417 vs WATCH-SPARE and same-job LABEL/RECOVER differences) also miss.

Do you see a distinct, complete 16-byte constructor that the BETA TAIL / two-bit field actually specifies (e.g. a lane selection or copy-stage mapping), or are the two predictors strictly post-hoc correlations with no defined output mapping? I am not asking for another predictor sweep; a concrete mapping is the only useful next step.
