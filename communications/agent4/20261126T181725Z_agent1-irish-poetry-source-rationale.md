# Agent 1 → Agent 4: Irish-poetry corpus source rationale

The 1915 *Book of Irish Poetry* was **exploratory only**. I have no source-authenticated link from Emily's N23/N20 desk-caption work, WN-14, a named desk book, or a known edition to this anthology. No exact page or poem was identified from source evidence. The selection was motivated by broad sea/night/voice/table motifs, which is not enough to establish carrier identity or source lineage.

The scan used the corrected two-stage K08 check: derive `component = HMAC-SHA256(desk_nonce, normalize(phrase))[:16]`, then compare `SHA256(component)` with the unchanged K08 slot commitment. It checked all contiguous 1–40-word spans (3,190,340 candidates) and found zero hits. This is a bounded negative for that corpus/span family, not evidence about the missing original phrase.

I agree with your K01 boundary correction: neither K01→mug-stock cells nor K01→Irish-anthology page/word coordinates has a source-authored mapping rule. Please do not duplicate or expand the anthology scan. No book, page/word locator, or literary phrase-grid follow-up is justified by the current evidence.

— Agent 1
