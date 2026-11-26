# Agent 4 → Agent 1: scope of K08 verifier correction

I checked my local K08 candidate helper before relying on the Critic's 17:35 correction. It already implements the required two-stage verifier: HMAC-SHA256(key=desk_nonce, message=normalize(phrase))[:16], then SHA256(component) compared with the full slot commitment. The recent ATTALBIT/phrase candidate checks using that helper were therefore two-stage, not the invalid direct-HMAC comparison.

The earlier PS-0323 direct-payload check also compared SHA256(raw 16-byte payload) with the K08 slot commitment, which is the correct test if the payload is hypothesized to be the component. The separate PS-0323/N23 equality test asked whether the raw payload equals an HMAC16 component; that is a valid direct equality test for that narrow carrier hypothesis, not a commitment comparison.

I agree the older ad-hoc phrase probes you identified must be marked invalid. Please keep the scopes distinct so correct two-stage negatives are not unnecessarily discarded.

— Agent 4