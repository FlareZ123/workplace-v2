# K08 P212 locator: committed-attempt conflict

**Agent:** 9  
**Date:** 19 November 2026  
**Status:** source audit; P212 remains conditional and is not authenticated

## Question

Does the mixed-attempt AX-7782 construction used to derive P212 follow the source-defined committed transfer chain?

## Primary-source rules

Three surviving records answer this directly:

1. `resources/evidence/mail/13.eml` identifies AX-7782 as the final custodian handoff and says: “The second attempt has the checkpoint used in the committed chain.”
2. `resources/recovery-routing.json`, K07, requires the checkpoint for each sequence 0..7 from the selected transfer's CHUNK records, taking the **greatest attempt per seq**.
3. `resources/evidence/transfers/transfer-audit.jsonl` contains attempts 1 and 2 for each of the eight AX-7782 chunks, with a non-dry-run COMMIT for eight chunks.

These rules select attempt 2 for every sequence. They do not select attempt 1 on even sequences.

## Reproduction

The source-defined vector is:

```text
8947 CEDC B9CC 73BA B7E8 7BE6 3302 C5C9
```

Concatenating those eight checkpoints as bytes and applying SHA-256, retaining the first 16 bytes, yields:

```text
93495F5E425AB8E592123DABAEB68545
```

This exactly equals the accepted K07 value in the unchanged canonical `candidate.json`. The same bytes, passed through the existing byte-LSB / first-bit-as-LSB packing convention, yield:

```text
53 D5
```

The P212 locator instead selects attempt 1 for even chunk numbers and attempt 2 for odd chunk numbers. Its vector is:

```text
6224 CEDC F3B8 73BA 1888 7BE6 3DB0 C5C9
```

That vector's first 16 SHA-256 bytes are:

```text
03EEC83CE17C337C2A6E141312C62181
```

and its byte-LSB pack is `50 D4` (ASCII `P`, unsigned 212).

Thus the P212 result depends on four **non-committed** attempt-1 checkpoints (sequences 0, 2, 4 and 6). It is not the committed K07 checkpoint chain. This distinction rules out describing the mixed vector as K07; it does not, by itself, rule out a separate K08 side-channel that intentionally uses alternate retry records.

## Interpretation

The source-derived phrase **LOW IF EVEN** can motivate a separate exploratory interpretation of retry metadata. However, the specific mapping “lower attempt on even chunks, higher attempt on odd chunks” is not stated in MAIL-13 or the K07 routing rule and conflicts with the explicit committed-chain selection.

The later P212 -> MAIL-04 -> PTW-417 -> N10 loop and the TWRAP subject-initial checksum are downstream of that same mixed-attempt P212 and the same LOW BIT packing convention. They show internal consistency conditional on the mixed selector; they do not independently validate it or override the committed-attempt rule. The interpretation of P as “page” (or as an Excel cell column) is also not quoted by the source.

Accordingly:
- retain P212 as a **conditional, unverified K08 side-channel locator hypothesis** based on non-committed retry checkpoints;
- do not call it the committed transfer chain or an authenticated page/book locator;
- do not use the MAIL-04/TWRAP closure as independent validation of the mixed selector;
- do not generate keeper phrases from this locator;
- K08 remains unrecovered because no exact final Emily caption is supplied or derived.


## Subsequent cross-carrier calibration (19 November)

Agent35 applied the same LOW-IF-EVEN selection operator to K05's separate valid retry stratum: two valid TRP2 records per latch, selecting the lower sequence for even latches and the higher for odd latches. The resulting low-bit pack is `0A4D` = **M10**, matching the independently derived note/seal route to MAIL-10. The official K05 component still yields `0343` = **C3**. This is cross-carrier support for the low/even/high/odd selector as an exploratory routing operation; it does not make the AX-7782 mixed vector the committed K07 chain, and it does not prove a workbook carrier or recover K08 wording. See [the K05 retry calibration](h17-k08-k05-low-if-even-0a4d-20261119.md).

Agent13's [low-bit/wrap fixed-point network](h17-k08-lowbit-wrap-fixedpoint-20261119.md) adds these conditional identities: P212 low bits give rotation distance 4; rotating ATEALBIT by four gives LBITATEA, whose low-bit pack returns 212; ATEA and AX-7782 both map to 13/MAIL-13; TWRAP maps to 10/N10. This is a coherent locator/checksum network, but cyclic rotation as the operation and P212 as a page/cell address remain inferred rather than explicit source rules. The network is not an independent validation of the AX mixed selector and does not contain the final caption.

The correct scope is therefore: **not K07 committed chain; potentially meaningful separate K08 side-channel; locator only, no phrase recovered.**

## Reproducible local calculation

The core check is:

```python
import hashlib

committed = bytes.fromhex(
    "8947CEDCB9CC73BAB7E87BE63302C5C9"
)
mixed = bytes.fromhex(
    "6224CEDCF3B873BA18887BE63DB0C5C9"
)

def lowbit_pack(raw):
    bits = [byte & 1 for byte in raw]
    return bytes(
        sum(bits[i + j] << j for j in range(8))
        for i in (0, 8)
    )

assert hashlib.sha256(committed).digest()[:16].hex().upper() == (
    "93495F5E425AB8E592123DABAEB68545"
)
assert hashlib.sha256(mixed).digest()[:16].hex().upper() == (
    "03EEC83CE17C337C2A6E141312C62181"
)
assert lowbit_pack(committed).hex().upper() == "53D5"
assert lowbit_pack(mixed).hex().upper() == "50D4"
```

No acceptance commitment, verifier, source record or canonical candidate was modified. No K08 HMAC candidate was tested.
