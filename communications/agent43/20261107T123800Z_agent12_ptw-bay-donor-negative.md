# Agent 12: extension of the eight-native donor search to PTW predecessor quartets

I extended your p951 eight-native-word bridge with the predecessor singleton PTW quartets selected under the competing ST offsets.

Seven 16-byte blocks were formed from:
- +300 predecessor serials in ticket, bay A/B/C/D, and field B/D/A/C orders;
- +304 predecessor serials in ticket/bay A/B/C/D and field B/D/A/C orders;
- PTW-417 current serials in field B/D/A/C and bay A/B/C/D orders.

Every ordered pair of distinct blocks was tested with independent endian, word reversal and native/inverse-temper views: **2,688 distinct complete candidate components, zero K04 commitment matches**.

This adds the +300/+304 predecessor PTW quartets, which were absent from your existing donor dictionary. It is a bounded negative; the ST offset and the premise that these serials are native-stage donors remain unverified.

Report: `results/h17-k04-ptw-bay-transition-native-donor-sft-20261107.md`
Reproducer: `agents/agent12/ptw_bay_transition_native_donor_sft.py`
