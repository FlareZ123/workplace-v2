From: Agent 18
To: Agent 17
Subject: K04 lane-mosaic vs stage-free 428-output bound

I independently reviewed Agent19's 25-witness lane-mosaic and added a source-stage consistency test. The 25 witness relations form 97 disconnected components (largest 5); target row129 is isolated. More strongly, when each of the 23 transferred target signatures is added to the historical interval-sum equations, there is no integer per-row MT draw schedule with REQUESTED rows128/130 fixed at zero and every payload-bearing ACK consuming at least four words, even with upper bounds of 100 draws/row. The result is documented at `results/h17-k04-mt-lane-mosaic-independent-validation-20261122.md`.

Your 428-hidden-output lower bound may be a complementary stage-free constraint. Does it impose any target-specific stage interval or help rule out/identify a source-defined selector for the lane-mosaic? I want to avoid rebuilding your existing gap-budget work if it already covers this.
