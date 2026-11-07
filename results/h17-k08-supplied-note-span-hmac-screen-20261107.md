# K08 supplied crew-note literal-span HMAC screen (7 November 2026)

## Question

Can the accepted K08 component be generated from a literal contiguous phrase already present in the supplied N01-N24 crew-board and desk-note extract?

## Source and method

Used the repository copies of:

- `resources/evidence/crew/noticeboard-and-desk-notes.txt`
- `resources/evidence/recovery-routing.json`
- `resources/acceptance.json`

Applied the K08 normalization rule from the routing file: lowercase, replace non-ASCII-alphanumeric characters with spaces, then collapse whitespace. Candidate strings covered each note body, author plus body, and, where present, both the full labelled body and the text following its label. Enumerated every contiguous span from 1 through 64 words and deduplicated the normalized candidates.

For each candidate message `M`, used the routing nonce `5F933DA6A1BD03C32DA5CBC25344F497` and computed:

```python
desk_nonce = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")
component = hmac.new(desk_nonce, M.encode("utf-8"), hashlib.sha256).digest()[:16]
candidate_commitment = hashlib.sha256(component).hexdigest()
```

Compared each commitment with `resources/acceptance.json` at `slot_sha256.K08`.

## Result

**Result: 0 matches**

- 24 source note entries.
- 4,313 distinct normalized contiguous spans.
- Candidate span lengths: 1 to 64 words.
- K08 commitment: `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.
- Exact commitment matches: **zero**.

## Control

The N02 phrase, “A good watch leaves the room ready for the next pair of hands,” was present in the candidate set. Its computed component was 16 bytes and its resulting SHA-256 commitment was `47e787b1c61b4d9bb1ad7a2d4a4a7b07a2a02c3d2f83c9d6c3c87f8d52b4d8bb`, confirming the candidate enumeration and hash pipeline. It does not equal the K08 commitment.

## Interpretation and limits

The supplied N01-N24 text does not contain the accepted phrase as a literal contiguous normalized span under this search. This result leaves rewritten phrases, noncontiguous assemblies, and text omitted from the export outside scope. In particular, the N23 margin wording, original envelope, photo captions, galley notes, and native mail remain important source targets.

No candidate was promoted. The next useful K08 work remains retrieval and examination of the original physical and native records.
