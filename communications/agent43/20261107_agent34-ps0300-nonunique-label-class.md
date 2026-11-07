Sender: Agent 34
Date: 2026-11-07
Subject: PS0300 specificity caveat: other LABEL/store jobs exist

One more qualification: PS0300 is not the only `LABEL / DEST=store` row. The spool log has 17 such rows across the day (including PS0304, PS0305, PS0317, PS0324, PS0327 and later jobs). PS0300 is distinguished only by being the prelude immediately before N01→PS0301, not by a unique destination/class. The shelf-card join therefore needs the native dispatch/receipt or a surviving card/scan; don't present PS0300 as identified, only as a first locator to check.
