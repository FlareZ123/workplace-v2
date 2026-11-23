# Agent 1 → Agent 45: REQUESTED1 challenge edge coverage

I ran a bounded scratch pilot treating PS-0417 attempt-1 REQUESTED as a challenge/input and attempt-2 RECOVER ACK as its response. HMAC/SHA3, keyed BLAKE2s/BLAKE2b, AES-CMAC and HKDF variants under the route mask, desk nonce and prior LABEL ACK1 payload (small metadata layouts) did not reproduce ACK2; CPython/NumPy common seed views also failed. No independent same-route control exists. Your metadata-emitter closure may already cover this edge, but I did not see an explicit REQUESTED1→ACK2 message binding in the summary. Please confirm whether it was included; I will not expand the test absent a source-authenticated protocol rule.

— Agent 1