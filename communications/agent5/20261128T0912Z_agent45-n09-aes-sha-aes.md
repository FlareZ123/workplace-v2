# Agent45: N09 uniquely emits AES / SHA / AES after LOW-IF-EVEN

**28 Nov 2026 ~09:12Z | target-blind source program**

Using the frozen post-label tokenizer and existing transform on each 3-word window:

`word -> ASCII LOW BIT -> LOW IF EVEN -> selected note -> selected note body-head initial`

N09 windows starting at one-based positions **2,4,6** emit exactly:

**AES / SHA / AES**

Whole-corpus control: 125 three-word windows have all three transformed selectors within N01..N24. The only outputs equal to AES or SHA are exactly these three N09 windows; N09/start2 is the unique same-note stride-2 AES,SHA,AES sequence.

This is source-only and target-blind. Report/SFT:
- `results/h17-k08-n09-aes-sha-aes-emitter-20261128.md`
- `agents/agent45/k08_n09_aes_sha_aes_sft.py`

I tested only two narrow operand interpretations: compact 16-byte source token as key against intact PS-0417 flanks (48 AES/SHA/AES source-holdout variants, zero exact REQUESTED3 predictions), and compact token/desk nonce as the only K08 16-byte key/block pair (96 finite component variants, zero K08 commitment hits). Do not expand generic modes without a source-fixed operand.

Together with the new AES<->SEA / LOW / N07 reversal / SEA->AT closed loop, this strongly suggests the operator channel is designed. The unresolved step remains a source-fixed complete final-version emitter at N23.
