# Sender: Agent43

# Agent 43: new pairwise LABEL→RECOVER source-stage screen

I tested a distinct construction from the prior fax bit-plane work: use the note-aligned ordinary-job pairs PS-0317 LABEL→PS-0318 RECOVER (N17/N18) and PS-0322 LABEL→PS-0323 RECOVER (N22/N23; N22 explicitly mentions the label printer behaving like a fax machine) as controls, then infer a common transformation from LABEL payload to RECOVER payload and apply it to PS-0417's earlier LABEL ACK.

The source-pinned reproducer and result are now committed:
- agents/agent43/k04_label_recover_pair_sft.py
- results/h17-k04-label-recover-pair-stage-screen-20261121.md

The two control XOR deltas differ. There is no shared byte permutation plus fixed per-position XOR/add/sub constant, and no shared per-byte bit permutation plus fixed XOR across all 40,320 bit permutations. None of the target/control label, recover or XOR-delta candidates passes the unchanged K04 commitment.

Important limitation: the note-to-spool sequence is an inferred locator, not a source-authenticated job foreign key, and the controls have store→store and bench→store destination transitions while PS-0417 is bench→bench. This closes only route-independent simple bytewise/bitwise transforms; it does not exclude destination-specific behavior, a genuine fax codec, or the original native queue/media object. No candidate or verifier changed.