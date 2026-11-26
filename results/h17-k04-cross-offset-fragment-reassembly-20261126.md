# K04: bounded cross-offset PS-0417 fragment reassembly

**Agent 6 | 26 November 2026 | Exploratory result: no K04 commitment hit.**

## Question

The earlier same-job byte-mosaic search selected donors at identical byte offsets and explicitly left cross-offset reassembly open. This experiment tested whether a 16-byte coupon payload could instead be assembled by concatenating two, three, or four contiguous fragments drawn from the four retained PS-0417 payload rows, with arbitrary source offsets and segment lengths.

The four retained rows are the earlier LABEL/ACK row, RECOVER attempt 1 REQUESTED, RECOVER attempt 2 ACK, and RECOVER attempt 3 REQUESTED. All four are queue entries for PS-0417 at DEST=bench. MAIL-14 identifies the LABEL row as a dispatch sticker, not a coupon/control-group row; it was included only as a possible stale-buffer donor. Any hypothetical construction requiring it would remain conditional absent a source link.

## Fixed candidate family

For each fragment count \(n\in\{2,3,4\}\):

- Choose positive fragment lengths \(l_1,\ldots,l_n\) summing to 16.
- For each output fragment, choose any of the four source rows and any contiguous start offset from 0 through \(16-l_i\).
- Concatenate the selected fragments in output order. Source rows may be reused.
- XOR the resulting 16-byte payload with the unchanged K04 route mask and compare the complete SHA-256 digest with the original K04 commitment.

This tests contiguous cross-offset fragments in raw byte order. It does not reverse bytes, permute bytes within a fragment, or use sources outside the four PS-0417 rows.

## Results

| Fragments | Candidate constructions | Synthetic control hits | Original K04 commitment hits |
|---:|---:|---:|---:|
| 2 | 14,960 | 1 (unique) | 0 |
| 3 | 9,162,048 | 1 (unique) | 0 |
| 4 | 3,008,881,408 | 1 (unique across all shards) | 0 |
| **Total** | **3,018,058,416** | **all controls passed** | **0** |

The four-fragment search used four disjoint composition-index shards. Their completed candidate counts were 752,733,184; 753,323,520; 752,867,840; and 749,956,864, summing exactly to 3,008,881,408. Each shard matched its independently computed expected count. The SHA-256 single-block transform was checked against the high-level OpenSSL SHA256 API. The 4-byte-window mosaic (52 windows, \(52^4=7,311,616\) constructions) is a subset of the completed four-fragment domain.

The small two-/three-fragment search and the four-fragment C++ search each included planted positive controls. The original candidate bytes, mask, and any candidate component were not printed or committed.

## Interpretation

This closes only the specified two-, three-, and four-fragment contiguous reassembly families from the four retained PS-0417 rows under the currently transcribed mask. The three-RECOVER-row subdomain is included. No candidate was recovered, and the selected ACK2 payload remains unauthenticated; this result does not establish the historical coupon bytes.

It does not test five or more fragments, arbitrary noncontiguous byte selection, other source objects, an incorrect route mask, or a different printer producer/copy stage. It does not change K04, K08, or REC8/1 acceptance. Do not repeat this exact contiguous-fragment family; a subsequent attack should change the producer/source relation rather than increase fragment count without a new mechanism.

## Reproduction

From the repository root, run the two-/three-fragment control and target screen:

```sh
python agents/agent6/k04_ps0417_cross_offset_fragment_sft.py --small-only
```

Compile the four-fragment search once, then run all four disjoint shards:

```sh
g++ -O3 -march=native -fopenmp agents/agent6/k04_ps0417_cross_offset_fragment_sft.cpp -lcrypto -o /tmp/h17-k04-fragments
for s in 0 1 2 3; do
  python agents/agent6/k04_ps0417_cross_offset_fragment_sft.py --shard "$s" --shards 4 --threads 4 --exe /tmp/h17-k04-fragments
done
```

The Python wrapper extracts the four rows and fixed acceptance inputs from `resources/`, writes them only to a temporary file, and deletes that file on exit. The C++ program reports counts and hit totals only; it does not print source or candidate bytes. This is a local exploratory computation, not a public-CI job.
