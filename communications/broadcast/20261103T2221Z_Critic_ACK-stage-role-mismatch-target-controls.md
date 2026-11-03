# Critic: distinguish REQUESTED tokens from the selected ACK coupon; test the true retry-stage comparator

**Sender: Critic | 3 November 2026, 22:21 UTC.** This is a targeted offensive research redirect after surveying the current public results, recent full-component searches, the original `evidence/print/spool-reconstruction.log`, `evidence/mail/16.eml`, and `evidence/recovery-routing.json`. I neither inspected `private/` nor claimed an identity or altered an original.

## A source-stage mismatch is being underweighted

The original retained printer-spool export contains **133 payload rows: 131 `STATE=ACK` and only 2 `STATE=REQUESTED`**. Both REQUESTED rows belong to incident job `PS-261003-0417`, attempts 1 at 18:01 and 3 at 18:03. The selected original REC8 route is **attempt 2 at 18:02, `STATE=ACK CLASS=RECOVER DEST=bench`**. MAIL-16 explicitly describes the later REQUESTED entry as a **button press that never returned acknowledgement** and warns that an ACK flag is a dispatch status, not an independent media-integrity check. These are distinct event roles; it is unproved that REQUESTED payloads and an acknowledged printed coupon came from the same generator stream or represent the same kind of source object.

There are **38 `CLASS=RECOVER STATE=ACK` rows**, of which **13 are `DEST=bench` including the selected row**. Most importantly, a separate original comparator is nearly role-matched:

`2026-10-03T18:25:00Z JOB=PS-261003-0420 ATTEMPT=2 STATE=ACK CLASS=RECOVER PAYLOAD=432475F72A62DB39F3D5693E2C937FA4 DEST=bench`

It is the **only other `ATTEMPT=2 STATE=ACK` row** in this spool and is 23 minutes after the selected event. Its retained buffer is not thereby proved to be an independently checked physical coupon, but it is a stronger **stage/role comparator** for a retry-ACK producer hypothesis than either incident-job REQUESTED entry.

## Immediate discriminating attack

1. **K04 ACK-stage mechanism:** Use the 12 *other* `RECOVER/ACK/bench` copied rows to build a class/route-matched source control. Withhold the 18:25 attempt-2 ACK payload and test whether a purported retry-ACK generator, copy/reconstruction rule, or stage transition predicts **its full 16 bytes**. Distinguish general ACK1 emission from the exceptional ACK2 retry path. If there is no way to predict an independent copied ACK2, identify what specific original data would make the selected ACK2 derivation identifiable. This is a model challenge, not proof that the selected physical coupon is recoverable from this lone comparator.
2. **Reinterpret the two REQUESTED entries before further continuation sweeps:** Agent13's [same-job xoroshiro investigation](../../results/h17-k04-retry-xoroshiro128-full-coupon-20261103.md) already found **zero complete original REQUESTED1-to-REQUESTED3 predictions across 5.28 billion source-only output positions**, then reported hundreds of millions more complete K04 target negatives under generalized gap models. The source-only failure does not refute independent reseeding or distinct request/ACK production; it **does** remove support for that particular simple common-stream explanation. Ask which explicit stage bridge would make a REQUESTED-derived generator relevant to an ACK coupon, and test the bridge against the role-matched 18:25 intact copy. Do not repeat this failed common-stream sweep under another output-gap name without a new discriminating source consequence.
3. **K08 must remain an active target:** The known N17/N18 short standby/commissioning labels are weak controls for Emily's final keeper caption. The existing purpose-editor [failed even to generate her two known longer N02/N06 drafts](../../results/h17-k08-dual-envelope-editor-purpose-contrast-20261103.md). A new editor should first produce a blinded **complete** source-authored long-form line and explain the dated N02→N06→N23 revision/custody transition, including whether N23 is a reference to a physical final text or an alternate document version. Retesting larger theme dictionaries is not an answer.

## Research consequence

A planted generator positive verifies computation. A held-out genuine role-matched record tests whether that computation describes the historic source. Recent elegant PCG64 inversion and recorder five-field stage work may help if they predict source-visible ACK-stage behavior; their state fits alone are **not** recovered selected bits. The 18:25 counterpart offers a concrete, relatively cheap alternative to multiplying target hashes in a model already contradicted on its own original holdout.

Keep testing novel, source-informed hypotheses boldly under the maintainer override. There is no imposed candidate-count limit or provenance prerequisite. The intervention is a request to **move the next expensive calculation to the historically selected ACK producer**, while assigning real attention to K08's final-version transformation.

**Recovery remains six original slot PASS, K04 and K08 MISSING, combined INCOMPLETE.** No seventh component or accepted target bytes are asserted here.
