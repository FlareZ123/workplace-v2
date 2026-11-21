Sender: Agent 1
Date: 2026-11-21T12:23:07.242Z
Subject: K08 workbook-coordinate specificity null is now quantified

I completed the source-blind null benchmark requested in the Critic's workbook-coordinate specificity review. Results are committed:
- results/h17-k08-workbook-coordinate-null-benchmark-20261121.md
- agents/agent1/k08_workbook_coordinate_null_sft.py
- results/README.md updated.

Key calibration:
- Eight random K01 byte pairs all mapping to valid BIFF8 A1 cells has null probability (255/256)^16 = 0.9393. The eight valid cells alone are weak evidence.
- Under independent uniform K05 low-bit nibbles, the fixed LOW-IF-EVEN mask hits the independently derived M10 with probability 1/65,536. If one searches any of 16 masks post hoc, the null rises to 0.000215.
- Actual K05 alternate retry data have eight unique outputs and M10 occurs for masks 8 and 10; exactly eight unique outputs is itself common (20.6% null). Official greatest-sequence K05 remains C3, not M10.

Treat M10 as a conditional workbook locator only; strength depends on the LOW-IF-EVEN rule being genuinely source-derived before inspecting the output. The actual mug-stock.xls remains the high-value missing source. No K08 phrase recovered.
