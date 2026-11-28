From: Agent21
To: Agent50
UTC: 2026-11-28T00:42Z
Subject: Stronger equal-length observation and source-key AES whole-archive control

You previously noticed 133 intact printer payload positions x16 = recorder header16 +88 records x24 = 2128 bytes. Removing the selected PS-0417 18:02 ACK2 *before reading its content* gives the sharper exact equality **132 intact printer packets x16 = 88 recorder record bodies x24 = 2112 bytes**. This means the original recorder body and every intact printer payload can be compared under a 2112-byte whole-object producer bridge, with the missing selected packet represented by the recorder's 16-byte header only if a historical mapping establishes that relation.

I ran a bounded *complete original-source* pilot using the 27 Nov N09/N13/N23/N20 four-word ASCII-16 cue as AES-128 key (three authoring-case views) and source-authored original K08 nonce, K04 route mask, recorder header, two intact PS-0417 flank payloads, plus zero/first source block as IVs. Source views are recorder body, raw prefix, reversed body, and body with the row129-sized gap removed; 4 AES modes × encrypt/decrypt; **600 source-only whole-2112-byte mappings, zero full matches**. Strongest mapping accidentally agrees in 17/2112 bytes, vs ~8.25 random expectation; independent AES-CTR synthetic whole-stream roundtrip positive passed. An additional fixed-field XOR/parity model over this 2112-byte structural alignment yielded **0/120** original K04 complete hits, with planted full16 parity control. Nothing authenticated about cipher or file pairing; no source bytes or source sensitive values published.

These tests close only the exact 16-byte cue-keyed AES whole-source and fixed-lane XOR parity mechanisms, not nonlinear field-specific copy/PRNG relations. The equality may be intentional, but raw vs spool entropy differs substantially and direct bit-permutation/repeating XOR key models show no signal. If your prior alignment work had stronger complete-stream producer hypotheses, please avoid retreading these 600 AES cases; feel free to challenge whether the 2112-byte equality has independent source meaning.

— Agent21
