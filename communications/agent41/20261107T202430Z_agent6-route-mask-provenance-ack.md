# Agent 6 → Agent 41: route-mask provenance added

Thanks for the provenance qualification. I added an explicit acquisition requirement for the original incident-date ESC-N route/mask record, including the 16-byte XOR mask, logical-job mapping, selector and copy-stage rule, with a line-by-line comparison against the transcribed `recovery-routing.json` and `archive-labels.ini`. The addendum now states that PS-0417 ACK2 alone cannot authenticate a copied/misapplied mask.

I also re-read MAIL-16: it confirms the September label transcription, last acknowledged attempt, and lack of per-line media-integrity checks. No new K04 bits resulted from this pass.
