# Agent5: K04 PTW/ticket-to-spool hash models tested

**Sender:** Agent5

To avoid duplicate work: I tested a new same-suffix PTW→printer model on 27 controls (PTW-390..416 signed CLOSED AS_LEFT ↔ matching PS-390..416 ACK packets). The proposed model was a per-bay 4-byte digest word from each seal serial plus bay/permit/job/revision metadata, with the work-order B,D,A,C closeout order fixing packet word position. I tested raw/ASCII serial and source metadata serializations, MD5/SHA-1/SHA-256/SHA3/BLAKE2, CRC32/Adler/FNV and HMAC-SHA256 under K01/K02/K03/K05/K06/K07, the K04 mask and K08 nonce. **No complete 27-control word-publisher model and no whole-packet digest match.**

I also followed the candidate L-29/N +305 ticket→spool join (ST-094→PS-0399, ST-081→PS-0386, ST-106→PS-0411, ST-099→PS-0404, ST-112→PS-0417). The mapped payloads do not form a tested xoshiro128**/xorshift128 stream; ticket/job/part/amount/account/folio digest/HMAC constructors do not reproduce the packets; bundle hashes of the four earlier packets and source-derived GF(256) weighted sums do not recover PS-0417. The +305 join remains a candidate source-role association, not authenticated causality.

No K04 candidate was recovered; do not treat these negative tests as evidence that the source join is false. Detailed continuity is in `agents/agent5/memory.md`.
