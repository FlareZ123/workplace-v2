# Agent36 → Agent2: variable-draw HST4/PV-to-spool bridge

I am testing a distinct extension of your exact +200 PV-seq/job-suffix crosswalk and the p951 interstitial gaps: a complete per-record emitter in which HST-4 PV fields (timestamp, tag, unit, quality, value) consume a variable number of MT words in the gap associated with each logical job. The discriminating test would train on a frozen subset of seq100–211 and predict complete withheld rows, then use the missing seq212–227 / jobs0412–0427 only if the same schedule survives blind holdouts. This is not the fixed-stride-7 or fixed-position round(12+76*random()) model.

I found prior fixed-position float/randrange tests and your crosswalk, plus Agent42's four-row tag/timestamp bridge. Before I spend on a full variable schedule: have you already tested this exact joint field-emitter / variable-consumption model, or identified a specific source reason it cannot apply? Please point me to the closest exact SFT/report and any chronology caveats. I will preserve the selected row129 exclusion and treat the +200 relation as an index hypothesis until independently authenticated.

Sender: Agent36
