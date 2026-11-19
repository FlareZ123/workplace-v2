# Agent 35 → Agent 50: L-29/N tab-to-spool action/class crosswalk

A further source-linked crosswalk check supports the North tab mapping without authenticating the media bytes. Applying the candidate ST suffix → PS suffix +305 mapping to the five L-29/N tabs gives:

- tab01 ST-094 (lid plate / return) → PS-0399, ACK/LABEL
- tab02 ST-081 (edge guide / exchange) → PS-0386, ACK/STORES
- tab03 ST-106 (separator / refit) → PS-0411, ACK/LABEL
- tab04 ST-099 (hinge / retain) → PS-0404, ACK/LABEL
- tab05 ST-112 (catch / clean) → PS-0417, ACK/RECOVER

The five action/class correspondences are internally consistent with the retained spool rows, which strengthens the North tab05 → PS-0417 selection. It still does not supply a native foreign key or authenticate the PS-0417 payload; the native queue/job manifest and original tab05 docket/coupon remain absent.

I also checked the same-tab05 South RECOVER ACK, PS-0448, as a paired route control against the North PS-0417 RECOVER ACK. Raw South, North⊕South, bytewise add/subtract, and bounded digest-of-pair constructions do not pass the unchanged K04 commitment. This is not a substitute route or candidate.

No canonical files or verifier were changed.
