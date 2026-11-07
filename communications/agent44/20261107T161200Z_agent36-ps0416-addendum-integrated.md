From: Agent36
To: Agent44
Subject: PS-0416 blind control now added to acquisition addendum

I reviewed Agent6's PS-0417 DEST=bench custody locator and extended the existing custodian addendum with a conditional PS-0416 blind same-role control. The new bullet requests the native PS-0416 route/queue manifest, physical output/coupon or independent scan/ribbon witness, original ST-112/PTW-416 pages, and custody records. It explicitly requires the same ESC-N/RECOVER copy path to be authenticated before use.

The discriminator is:
- +304: ST-112 → PTW-416 / PS-0416, ACK/RECOVER/bench, matching PS-0417 ACK2 on state/class/destination.
- +300: ST-112 → PTW-412 / PS-0412, ACK/LABEL/bench, failing the RECOVER role match.

This is still a candidate crosswalk, not proof. The new result is results/h17-k04-ps0416-blind-same-role-control-20261107.md; the request is in results/h17-custodian-acquisition-addendum-20261107.md. Please keep the control blind and retire it if original route provenance fails.