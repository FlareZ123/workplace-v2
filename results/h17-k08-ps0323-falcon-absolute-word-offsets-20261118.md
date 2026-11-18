# K08: PS-0323 as eight Falcon absolute word offsets

**Date:** 2026-11-18  
**Identity:** Agent 3  
**Status:** Closed negative for this exact mapping

## Question

Could the 16-byte ACK payload for `PS-261003-0323` encode the eight words of K08 as eight unsigned 16-bit absolute word offsets into the 1889 *Falcon on the Baltic* transcription? This was a new construction, distinct from the existing WN-14/K01 page-word and absolute-offset tests, and from the four-word PS-0323-to-note-vocabulary selector.

The N23 → PS-0323 relationship is only a structural note/job crosswalk; it is not established as causal. The Falcon transcription is a public candidate text, not proof of David's physical copy.

## Reproducible method

- Pinned the Falcon HTML source SHA-256 to `2741b1054d1369a7dcfc51b32da1f4b4931c5ca8a10c9b200cee548db496176e`.
- Pinned the normalized 81,392-word body stream to `36997e8cf827a0c0ddade6104b8d63c5e462e69749653ce009e5e50ce4fcce66`.
- Pinned `spool-reconstruction.log` to `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`.
- Read the ACK/RECOVER packets for `PS-261003-0323` and the adjacent N20 control `PS-261003-0320` directly from the pinned spool log.
- For each packet, interpreted its bytes as eight 16-bit unsigned integers in both big- and little-endian order, with both zero-based and one-based indexing.
- Joined the eight selected normalized book words, computed `HMAC-SHA256(key=K08 desk_nonce, message=normalized phrase)[:16]`, then SHA-256 hashed that 16-byte component against the official K08 commitment.
- Positive control: the known N02 phrase reproduced its expected HMAC16 `BF889359B0303F2B2B2FD96AE841210B`.

## Result

<badge color="red">No match</badge>

All eight candidate constructions failed the official K08 slot commitment. The four PS-0323 phrases were:

| Interpretation | Candidate phrase |
|---|---|
| Big-endian, zero-based | `had fortress said channel tones came some a` |
| Big-endian, one-based | `we dismantled me the in we of into` |
| Little-endian, zero-based | `bordered navigation the utrecht silted but the boat` |
| Little-endian, one-based | `were weird up and having lodgings traversing with` |

The four PS-0320 control phrases also failed. None of the eight candidates matched the K08 commitment.

## Conclusion and boundary

There is no support for the specific construction **PS-0323 payload → eight u16 absolute word offsets → Falcon 1889 text → K08 HMAC**. Do not expand this into arbitrary byte permutations or offsets. This does not rule out other books, a page/word scheme, the actual physical copy, or a separate caption source.

## Reproduction

- Script: `agents/agent3/k08_ps0323_falcon_word_offsets.py`
- Manual workflow: `.github/workflows/agent3-k08-ps0323-falcon-word-offsets.yml`
- Run: [44262047390](https://github.com/FlareZ123/workplace-v2/actions/runs/44262047390)
- Artifact: `agent3-k08-ps0323-falcon-word-offsets` (artifact ID 14408138952)

This is a bounded negative result, not a recovery of K08.
