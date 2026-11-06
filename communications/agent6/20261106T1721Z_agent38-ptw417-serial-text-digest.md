# Agent 38: PTW-417 serial-text digest follow-on

I tested a distinct PTW-417 label-text hypothesis following the existing raw serial and record-ID work: because the work order and print-fleet return register tie PTW-417 seal-rack labels to selected ESC-N job PS-261003-0417, the K04 physical coupon might be a standard 16-byte digest of the four selected signed as-left serials serialized as label text.

The source-pinned SFT `agents/agent38/k04_ptw417_serial_label_digest_sft.py` (commit `8b3312529069ea6bce8689324cd808ff619ef42e`) covers all 24 serial orders, six separators, optional SG- prefix, case, four explicit PTW/job identifiers as prefix/suffix and 12 standard digest reductions. It produced 48,384 unique 16-byte candidates from 55,296 assignments. Both original K04 interpretations (coupon XOR mask, or direct component) had zero hits, with one independently planted positive each. Canonical K03 source reconstruction and commitment check passed. Source pins and remote Git blob IDs match the attached ZIP copies.

This closes only this serial-label digest family. No K04 bytes are authenticated and no historical hash operation is claimed.