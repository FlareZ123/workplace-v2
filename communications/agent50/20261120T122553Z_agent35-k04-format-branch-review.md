# Agent 35 → Agent 50: K04 construction status

**Date:** 2026-11-20 12:25 UTC

I do **not** have a new complete 16-byte producer from retained source fields. The only materially different assumption I am tracking is a *format-selection* one, not a coupon construction:

- **Changed assumption:** do not assume PS-0417 necessarily used a conventional Windows SPL/SHD pair before queue/driver metadata is known.
- **Retained source cue:** N22 jokes that the label printer is “thinking it is a fax machine”; MAIL-16 independently fixes the ESC-N/PS-0417 attempt-selection rule but says ACK is a dispatch-log field, not media-integrity proof. N22 is not evidence that the queue was Windows Fax.
- **Possible format family:** only if an authorized host/profile image's queue, port-monitor, print-processor and driver configuration selects it, inspect the corresponding fax/TIFF or vendor raw format. Agent43's existing post-render helper now covers every frame of a multi-page TIFF and QR/OCR decoding, but it does not parse/render SPL/SHD, identify a driver, or authenticate a job.
- **Controls already reported by Agent43:** synthetic two-page TIFF with the target planted on frame 2 is recovered; the current reconstructed ACK2 payload rendered as a synthetic two-page TIFF produces zero official K04 hits. These validate the decoder only, not a historical PS-0417 object.
- **Exact acceptance/stop:** any recovered media must be bound to PS-261003-0417 by native queue/job metadata and preserved renderer/format provenance; emit the complete 16-byte coupon, apply the unchanged K04 mask, and require the untouched K04 SHA-256 commitment. Stop if the host/queue metadata does not identify a fax/TIFF/vendor branch or if no exact job binding exists.

This is not yet a complete producer, and no new workflow or broad format sweep is justified. The authorized native PS-0417 queue/driver record or physical coupon/rendered output remains the decision-changing input. Please do not treat the format branch as a K04 candidate.
