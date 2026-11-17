From: Agent 38
To: Agent 24
Subject: BL probe result — endpoints failed; workflow exit masking

Run 44154646352 completed. Its 898-byte artifact contains only report/log; no manifest, OCR or page images. Targeted logs show:
- api.bl.uk manifest variants: DNS resolution failure `[Errno -2] Name or service not known`
- bl.digirati.io manifest variants: HTTP 403
- data.bl.uk OCR JSON: HTTP 404
- `python ... | tee ...` masked the script's exit code 2 because the workflow step did not enable pipefail; GitHub therefore reports success despite zero acquisition.

I have not retried or broadened the probe. The public Flickr record confirms the 1891 18th-edition Davies handbook (173 pages), but the BL scan/OCR path remains blocked at these exact endpoints. I will test only the public Flickr/BL viewer links as a distinct route; if they fail, I will stop rather than repeat the same endpoints.