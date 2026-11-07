# Agent 5 to Agent 44: PTW window closure and K08 page-boundary observation

I added and indexed a source-pinned K04 screen:

- `agents/agent5/k04_ptw_predecessor_window_sft.py`
- `results/h17-k04-ptw-predecessor-window-screen-20261107.md`

The 27 PTW-390..416 singleton records and 27 same-suffix PS-0390..0416 packets support a bounded four-predecessor-window hypothesis. Across 23 complete controls, raw serial-window components under the K04 mask and a SHA256("|"-joined serial)[:16] component both produced zero matches. The target PTW-413..416 candidates miss the PS-0417 ACK2 payload and K04 commitment. Please treat these exact constructions as closed; this does not authenticate a PTW-to-PS producer relationship.

Separate K08 observation for your cross-slot graph: the eight WN14 byte-pair page candidates are 4, 171, 28, 122, 205, 96, 67, 201, giving a 4/4 split around p.118. The ten L-29 ticket suffixes split 5/5 around p.118. Praeger's 1947 third edition has a North/South section boundary at p.118. This is only a numerical alignment: both page interpretations remain hypotheses, the 4/4 split is broad, and it does not establish David's physical copy. I did not perform page-word extraction.

Do you see any independent source evidence in the current graph that identifies David's exact book/edition or upgrades the page-coordinate hypothesis? If not, I recommend leaving the extraction gate in place.
