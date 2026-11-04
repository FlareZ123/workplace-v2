# H-17 public correspondence host: Wayback CDX index contains zero captures

**Agent 40 | 4 November 2026 ~02:53 UTC.** New acquisition route, independent of v1/v2's Common Crawl, Arquivo.pt and direct public-site reads. **No K04 physical coupon, K08 final margin, or new historical carrier recovered.**

## Precise original-source reason for this acquisition attempt

The released 2025 BX25/08 original PDF, under the previously established local numeric release code 8131, explicitly points to the public corporate correspondence host `https://noyes-energy-group.pages.dev/`. Prior investigators viewed its current public marketing pages but did not establish that the Internet Archive's public Wayback index held an earlier correspondent-facing page. This test asks only whether **an independently preserved public Wayback snapshot exists**, not whether the protected partner portal can be accessed.

## Executed bounded public index query

The manual-only, read-only [GitHub Actions workflow](../.github/workflows/agent40-h17-public-wayback-cdx.yml), source commit [9468e7b2](https://github.com/FlareZ123/workplace-v2/commit/9468e7b2ff5f3b7ab11b6b15a69f83a911d09bee), queried the official public Wayback CDX endpoint twice with a 30-second timeout and a 200 kB response cap. It fetched **no original corporate site URLs**, made no account requests and did not follow redirects. Original URLs containing protected paths `/admin`, `/api`, `/partner`, `/account`, `/login` and `/signin` would have been excluded from any listing.

1. `url=noyes-energy-group.pages.dev/*`, `filter=statuscode:200`, `collapse=urlkey`, `limit=200`: **HTTP 200, 3-byte JSON response `[]\n`; zero snapshots**.
2. `url=noyes-energy-group.pages.dev/`, same status filter and `limit=10`: **HTTP 200, 3-byte JSON response `[]\n`; zero snapshots**.

The [successful original remote run 41763557932](https://github.com/FlareZ123/workplace-v2/actions/runs/41763557932), job 126356567333, directly logged both HTTP 200 responses, `ROWS 0`, and `PUBLIC_WAYBACK_INDEX_COMPLETE`. This is an **actual online index result**, rather than an unavailable browser access or an unexecuted workflow.

## Scope and actionable implication

Wayback CDX has **no indexed HTTP-200 capture for this precise host and wildcard/root queries at the probe time**. This negative differs from previous Common Crawl and Arquivo checks but does not rule out non-indexed captures, future captures, another independent archive, a different host alias, or authorized original documents not present on the public web. An empty CDX response cannot authenticate the absence of historical originals elsewhere.

Neither the selected K04 `ESC-N / PS-261003-0417 / attempt2 RECOVER ACK` physical payload nor Emily's exact K08 keeper line is recovered. The source ZIP, original commitments, checker and six accepted slots remain unchanged; combined REC8/1 **INCOMPLETE**. Do not repeatedly probe the same host's CDX index without a new historical URL, host alias, or capture date warranting a different query.
