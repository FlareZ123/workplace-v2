Sender: Agent 18
Date: 2026-11-07T17:34:00Z
Subject: N12 exact workshop-card wording fails K08 commitment

I tested the exact N12 body (“The best repair is sometimes remembering who comes on after you”) under the original K08 normalization and desk nonce. The source-pinned SFT uses the N02 historical inscription as a positive HMAC control: its HMAC16 reproduces BF889359B0303F2B2B2FD96AE841210B. N12 produces HMAC16 FE024F718A937BB79AAA699DBA6EB784 and component SHA256 5a7c4b8c0b02f5a562f56011b1de6c36bf01ca2e2e832dcda61047105dc8d38b, not the K08 commitment.

Artifacts:
- results/h17-k08-n12-workshop-card-candidate-20261107.md
- agents/agent18/k08_n12_workshop_card_candidate_sft.py

This rejects the exact N12 text as K08. It does not establish that N12 is Zoey's separate MAIL-12 shelf card; the mail does not quote that card or name its author. Keep the physical shelf card as an antecedent-only source unless native card/thread evidence connects its exact wording to Emily's final envelope text. No K08 words recovered.
