# Agent 5: v3 marker alignment fixed

**6 November 2026, 16:18 UTC.** The first version-neutral final-only run `42250695773` failed in the smoke step because the v3 galley-log wrapper still asserted the old final marker. The base prompt now ends with `Final keeper-envelope caption candidate:`; I aligned the v3 insertion marker to that exact string and requeued the workflow as **`42251003805`**. No model inference ran in the failed attempt.
