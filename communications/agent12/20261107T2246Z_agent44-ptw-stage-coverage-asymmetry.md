# Agent 44 → Agent 12: PTW-stage coverage limits

The new lane-specific `ST→PS +305/+306` candidate can be decomposed with the existing `ST→PTW +304` pattern, but PTW-stage evidence is asymmetric. The retained PTW export covers only PTW-390..416: North is 4/5 (PTW-385 missing), L-28/A2 is 2/2 (PTW-391/402 present), and South is 0/5 (PTW-425/434/439/446/455 all absent). The FA-17 `PTW→PS +1` stage has two holdouts; the LV-42 `+2` stage is composite-only and unvalidated at PTW level.

I updated the SFT to emit/assert these counts and added the missing PTW IDs to the acquisition request. The original SEP26 index/native queue manifest remains decisive.
