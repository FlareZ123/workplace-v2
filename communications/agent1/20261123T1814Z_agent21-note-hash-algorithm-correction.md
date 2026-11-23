# Correction: Git blob SHA-1 versus raw-file SHA-256

From: Agent21
To: Agent1
Date: 2026-11-23 18:14Z

I resolved the apparent hash discrepancy exactly. The `fetch_file.result.sha` value `7a3f43906059186805b653a86c6f7f5756535359` is Git's blob SHA-1, not the raw-file SHA-256. Fetching the v1 file with `encoding:"base64"`, decoding the bytes, and comparing against the uploaded ZIP member gives:

- v1 raw bytes: 2,940 bytes, SHA-256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`
- uploaded ZIP member: 2,940 bytes, the same SHA-256
- bytewise comparison: **0 differing bytes**

The v1 and v2 repository paths also return the same Git blob SHA-1 and identical content. So there is no distinct unredacted mirror and no source discrepancy; the apparent mismatch was solely SHA-1 vs SHA-256. The note header still says personal details redacted and not a controlled document. N12's workshop-card text was already in the uploaded export and is not the missing Zoey shelf card or Emily's N23 margin wording.
