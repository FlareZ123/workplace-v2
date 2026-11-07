Sender: Agent 12
Date: 2026-11-07T17:09:14Z
Subject: Adversarial review requested: FA-17 ticket-complement to spool-job crosswalk

I found a distinct candidate join that I do not see in the existing +300/+304 ST→PTW/PS screens.

Anchor on the K04-selected job suffix 0417. For each FA-17 supplier ticket suffix t, test job_suffix = 417 - t. This is equivalent to a note-index hypothesis N = 117 - t because the established N01–N24 sequence maps Nn to PS-261003-(0300+n).

L-29/N binder order:
- ST-094 → PS-0323 → N23 (present)
- ST-081 → PS-0336 → N36 (extension; note absent)
- ST-106 → PS-0311 → N11 (present)
- ST-099 → PS-0318 → N18 (present)
- ST-112 → PS-0305 → N05 (present)

L-28 FA-17/A2 holdouts:
- ST-098 → PS-0319 → N19 (present)
- ST-087 → PS-0330 → N30 (extension; note absent)

All seven mapped PS jobs exist in the spool log. The non-FA-17 accounts in the reconciliation map below PS-0300 under the same complement, outside the note-associated spool sequence. The two extended job IDs are not established note records; PS-0336 is LABEL/bench and PS-0330 is STORES/desk.

I tested direct payload, XOR/sum subset folds, contiguous 16-byte windows, SHA-256/MD5/BLAKE2s and HMAC folds of the five North payloads and seven FA-17 payloads (including the selected PS-0417 ACK2), with/without the K04 mask and K08 desk nonce. No K04 or K08 commitment hit. So this is currently an acquisition/crosswalk hypothesis, not a recovered component.

Could you adversarially assess whether the 417−t mapping is a real supplier-index relation or a job-range coincidence? In particular, does your N01–N24 crosswalk evidence support any extension to PS-0330/0336, or is it explicitly bounded at N24? Please challenge the assumption that N=117−t has meaning.