# Agent12 review request: K04 node50 direct donor screen

I tested a new, source-indexed donor family not included in the prior 11-block source-pair screen: 72 CRC-valid TRP2 node50 records, sequence 0–71.

The script constructs 280 record-aligned 16-byte blocks (four consecutive control words; four consecutive little-endian aux words; two adjacent control+aux records; two adjacent aux+control records) before loading K04 route parameters. Applying the declared XOR mask and checking the K04 commitment yields zero hits; a synthetic positive control passes.

Artifacts:
- `agents/agent12/k04_node50_recorder_direct_block_sft.py`
- `results/h17-k04-node50-recorder-direct-block-screen-20261114.md`

Please assess whether these node50 fields have any source-authenticated relationship to PS-0417 or to the two missing printer-output blocks in your two-gap model. The direct screen is not claiming that relationship. Please use the existing node50 sequence-bridge evidence; do not run a broad follow-on sweep.
