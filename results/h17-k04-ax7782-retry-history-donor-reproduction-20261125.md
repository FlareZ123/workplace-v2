# K04 AX-7782 retry-history donor reproduction

Reproduced from the committed source-pinned script in GitHub Actions. The script itself asserts the candidate-set cardinalities and zero original-slot hits.

~~~json
{
  "AX7782_attempt_rows": 16,
  "AX_only_candidate_presentations": 512,
  "AX_only_distinct_components": 484,
  "AX_word_views": 32,
  "cross_source_candidate_presentations": 40960,
  "cross_source_distinct_components": 38720,
  "historical_AX_printer_producer_link_authenticated": false,
  "nonoverlapping_source_blocks": [
    "K02raw",
    "K05raw",
    "K06raw",
    "PTW417",
    "WN14"
  ],
  "original_K04_commitment_matches": 0,
  "selected_ACK2_payload_decoded": false,
  "seven_seeded_full_stream_controls": "7/7 PASS",
  "total_candidate_presentations": 41472,
  "total_distinct_components": 39204
}
~~~

This is an aggregate-only result: no candidate bytes, raw payloads, checkpoint values, route masks or component digests are included.
