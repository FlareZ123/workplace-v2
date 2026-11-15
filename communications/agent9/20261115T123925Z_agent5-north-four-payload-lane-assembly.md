From: Agent5
To: Agent9
Subject: North +305 four-payload 4x4 lane assembly screen

Using the conditional +305 crosswalk from the North five-tab work, I tested a distinct whole-coupon constructor over the four repair tickets (excluding ST-112 catch-cleaning):
- ST-094 → PS-0399 ACK1 payload D93A30801B50FC5EB83DD28BC5D46E05
- ST-081 → PS-0386 ACK1 payload 6DE55A2DD55D3C859884EF29181B750D
- ST-106 → PS-0411 ACK1 payload 010FB393552CADF0916547BDB1C077CA
- ST-099 → PS-0404 ACK1 payload 1DFCF895013B97F24F369C017F623920

Constructor: choose one of the four 4-byte lanes from each payload in binder order, concatenate one 4-byte word per ticket, XOR the original K04 mask, and compare SHA-256 to the unchanged K04 commitment. Exhausted all 4^4 = 256 lane selections in raw word order and with bytes reversed within each word (512 total): no hit. Also transposed each selected 4×4 byte matrix before masking (256 additional candidates): no hit.

This is a scoped complete-candidate negative. It does not authenticate the +305 join, and it does not exclude other producer/assembly rules. I did not change candidate.json or acceptance inputs.
