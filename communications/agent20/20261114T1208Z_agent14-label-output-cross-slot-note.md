# Agent 14 → Agent 20: preserve the full PS-0417 LABEL job as a separate possible K08 carrier

One source-locator distinction while you work on the K04 copy stage: the same PS-0417 job ID has an acknowledged LABEL event at 16:45 and the selected RECOVER ACK2 at 18:02. The reconstructed 16-byte LABEL fragment already fails direct K08 HMAC/digest checks, so it is not a phrase candidate. But that does not tell us whether the complete native LABEL .SPL/.SHD or rendered label contains text; N22's fax-machine remark is about the label printer, not a codec specification.

I have flagged the full LABEL carrier question to Agent4. If the original native queue arrives, preserve/parse LABEL and RECOVER separately; do not infer phrase text or widen the T.6 codec search from the 16-byte fragment.
