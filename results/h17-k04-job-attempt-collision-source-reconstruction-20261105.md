# H-17 selected K04: source-key collision and complete-coupon reconstruction

**Agent 27 | 5 November 2026.** Three mutually different, original-source-pinned complete-coupon constructions were tested using the same *real* print-spool key collision. **None reproduces the K04 acceptance commitment.** The six established components remain accepted; K04/K08 and combined REC8 are unresolved.

## Observed source-level ambiguity versus selected-record identity

The original `resources/evidence/print/spool-reconstruction.log` (SHA256 `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`) has four rows with the same logical job `PS-261003-0417`:

| Historical event UTC | ATTEMPT | CLASS | STATE | complete 16-byte copied buffer |
| --- | --- | --- | --- | --- |
| 3 October 16:45 | 1 | LABEL | ACK | `E1E60D5F6B6DD2225FA6D5A2A63AD932` |
| 3 October 18:01 | 1 | RECOVER | REQUESTED | `CD3E4F216ADB2FB180DA2AA90B33F7A4` |
| 3 October 18:02 | 2 | RECOVER | ACK | `A9A9DC5731A5E2AE879C47215C2559D5` |
| 3 October 18:03 | 3 | RECOVER | REQUESTED | `44D53DFC29D7943A95D89371DA58EC64` |

The same `(JOB,ATTEMPT)=(0417,1)` identifies two distinct source records. This is an observed risk for a *coarsely keyed source/print cache*. The selected `(0417,2)` ACK is **unique** even under that coarse key; neither the source nor the accepted route says its physical 16-byte coupon was actually overwritten by such a cache. An independent job 0420 also has two differing CLASS rows but its RECOVER ACK attempt2 is unique.

For all candidate coupon bytes `P`, the unchanged original reducer is `K04=P XOR 8556C8CB6140A7F9A5123AC7571BEE1C`; the full SHA256 digest must equal `930a52a1bab97ca2966332137c99e99298ea6182fb32ab63a3421dfb4fd8c9e0`. All tests retain the original supplied source, route sheet, acceptance and verifier unchanged.

## Three complete reconstruction mechanisms

| Source-conditioned model | Complete original SHA checks | Different complete candidate components | Genuine K04 matches | Planted complete-coupon control |
| --- | ---: | ---: | ---: | --- |
| Same-position Boolean 3-input gate on LABEL1, REQUESTED1 and copied ACK2: all 256 truth tables, 4 reversible byte/word layouts of each input/output; exclude two constant gates | **65,024** | **14,456** | **0** | PASS, four equivalent assignments |
| Wrong-cache-key AES-128 ECB encryption/decryption of one preserved 16-byte source under the other two as keys, one/two stages, both key-XOR whitening bits, independent four-way layouts | **36,864** | **32,256** | **0** | PASS, one two-stage source-key rewrap |
| Arbitrary same-position byte selection independently at each of 16 output byte positions, choosing any of **LABEL1, REQUESTED1, copied ACK2** | **43,046,721** | **43,046,721 assignments**; exact uniqueness is not claimed | **0** | PASS, one independently planted three-way selection |

Original-source output of the third source-pinned run:

```text
SOURCE_SHA_PIN_PASS collision_LABEL1_REQUESTED1_ACK2 assignments=43046721 original_hits=0 planted_hits=1 seconds=15.5764
```

Reproducers: [three-way Boolean SFT](../agents/agent27/k04_job_attempt_collision_boolean_sft.py), [wrong-key AES wrapper SFT](../agents/agent27/k04_collision_aes_rewrap_sft.py), and [43-million byte mosaic SFT](../agents/agent27/k04_collision_threeway_byte_mosaic_sft.cpp). All three test the original full 256-bit K04 commitment after applying the specified mask. The first two use Python, and the AES script needs `cryptography`; the byte-mosaic source uses C++17 and OpenSSL libcrypto.

## Relation to preceding work and decision

[Agent13's key-collision inventory](h17-agent13-zip-compression-and-spool-join-keys-20261105.md) first shows that the selected `JOB+ATTEMPT=2` itself has no duplicate. The present work answers the further question of whether **the conflicting two ATTEMPT1 records could be mixed with the retained selected copy to recover a full original coupon** under these three bounded mechanisms. It differs from [Agent7's three-RECOVER-attempt byte mosaic](h17-k04-three-retry-byte-mosaic-20261104.md), which uses REQUESTED1, ACK2, REQUESTED3, omitting the colliding historical LABEL1; and from [Agent20's ticket-derived AES generator](h17-agent20-aes-source-and-ticket-emitter-20261104.md), which does not treat the recorded class collision as a source-plaintext/key swap.

These are **conditional source-assembly negatives**. The source does not attest any shared Boolean mixer, AES wrap, or byte-level concurrent writer. The printed ACK attests receipt, while the physical coupon is still unauthenticated. No conclusion can be made about *all* cache/copy faults from this finite list; no physical K04 bit or final K08 word was recovered.

**Next discriminating evidence** would be an observed pre/post export buffer relation on an *intact* same-purpose printer transaction, or a second exact preserved 0417 ACK2 print/coupon with a trustworthy physical checksum. Absent that, another arbitrary data-mixing catalogue has little causal value. Preserve the distinction between visible source key collisions and the hidden original coupon.
