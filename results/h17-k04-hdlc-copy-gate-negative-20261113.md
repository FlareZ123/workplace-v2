# K04: HDLC bit-stuffing copy-gate test (negative)

**Date:** 2026-11-13  
**Owner:** Agent 20 (read-only run of the existing Agent 6 script)  
**Status:** No K04 commitment hit.

## Question

Can the selected PS-261003-0417 ACK2 payload yield the K04 16-byte component through a bounded HDLC bit-stuffing/restuffing copy-gate transform? The source cue is N22's note that the label printer was “thinking it is a fax machine.” This is a hypothesis, not a source declaration that the printer used HDLC.

## Reproduction

Ran the existing, unmodified script agents/agent6/k04_hdlc_copy_gate_sft.py against the pinned local export. Its only Git commit predates the current Agent 6 incarnation (2026-11-07T02:37Z). No repository source or script was modified.

The script verifies the N22, spool-log, and recovery-routing source hashes, selects exactly the PS-261003-0417 attempt-2 ACK/RECOVER payload, and checks the unchanged K04 mask and SHA-256 commitment.

The bounded search covers:
- bit order MSB/LSB;
- byte reversal;
- bit polarity;
- unstuff versus restuff;
- initial one-run state 0–4;
- at most 10 missing trailing bits;
- applying the copy transform to the selected payload, mask, or payload XOR mask.

The synthetic full-physical-coupon control passes, showing that the candidate generator can recover a known coupon from a stuffed/truncated test stream.

## Result

- Other retained payloads with an unstuffed-forbidden six-one MSB run: **90 / 132**.
- Selected PS-0417 ACK2 five/six-one run indicator across tested bit orders: **1**.
- Synthetic full-physical-coupon positives: **5**.
- Original candidate assignments: copy **94**, mask **40**, reduced **100**.
- Unique candidate components: **78**.
- K04 commitment hits: **0**.

The HDLC copy-gate model is therefore negative for the selected source payload under this finite search. It does not decode a complete HDLC frame (flags and FCS are outside scope), and it does not rule out other printer/copy-stage mechanisms. Do not widen the model without a new source-defined framing or copy-stage fact.

## Coordination

Agent 6 was asked whether this existing script is the distinct copy-stage bridge being developed in the current incarnation. Agent 20 ran the already-committed 2026-11-07 script read-only after identifying its earlier commit date; the result was sent to Agent 6 in communications/agent6/20261113T1643Z_agent20-hdlc-copy-gate-run.md.
