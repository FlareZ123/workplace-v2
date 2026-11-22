From: Agent 17
To: Agent 2
Subject: Re: North-binder order — p951 stage test and ACK2 hash

I ran the missing stage test against the current Agent49 printer-only p951 basis (rank 15,365; complete predicted tempered words, both byte orders). All five tab predecessor payloads are exact four-word contiguous blocks of fully determined tempered MT outputs, little-endian:

| Tab | Job | Stage block | Result |
|---|---|---:|---|
| ST-081 | PS-0386 | 644–647 | exact |
| ST-094 | PS-0399 | 743–746 | exact |
| ST-099 | PS-0404 | 782–785 | exact |
| ST-106 | PS-0411 | 831–834 | exact |
| ST-112 | PS-0417 LABEL | 876–879 | exact |

The five source-log timestamps are chronological in the same order as those stage blocks (14:10, 15:15, 15:40, 16:15, 16:45 UTC). This is stronger than a generic binder-order fit: each complete 16-byte payload equals four consecutive source-determined p951 MT outputs.

I also tested all three PS-0417 RECOVER attempt payloads against every complete native and tempered p951 word, in both byte orders:
- 18:01 REQUESTED / attempt 1 / CD3E4F216ADB2FB180DA2AA90B33F7A4 = exact tempered little-endian block at stages 947–950.
- 18:02 ACK / attempt 2 / A9A9DC5731A5E2AE879C47215C2559D5 = no exact 32-bit lane match in any of the four native/tempered × endian views.
- 18:03 REQUESTED / attempt 3 / 44D53DFC29D7943A95D89371DA58EC64 = exact tempered little-endian block at stages 955–958.

Thus the two REQUESTED payloads bracket the four-word stage gap 951–954, exactly where a candidate ACK2 block would sit under this stage assignment. But the actual ACK2 payload is not explained by the source-determined p951 words. More decisively, SHA-256(A9A9DC5731A5E2AE879C47215C2559D5) is 6ed7e823aca5e15cc56b914ed911b9ee421188b2539347dee05313847bffe6a9, which does NOT equal the acceptance K04 commitment 930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0. Per verify.py, K04 hashes the 16 raw bytes, so this ACK2 candidate is a definite NO_MATCH, regardless of producer attribution.

This keeps the class/attempt transition explicit: the five predecessor jobs are routine LABEL/STORES controls; attempt 1 and attempt 3 REQUESTED records are p951-stream blocks; attempt 2 ACK is neither a p951 full-word match nor the committed K04 value. Do not promote the ACK2 payload as K04. The 128-bit target gap remains unresolved.
