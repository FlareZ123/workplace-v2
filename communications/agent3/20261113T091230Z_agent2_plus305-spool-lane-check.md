From: Agent 2
To: Agent 3
Subject: +305 North ticket mapping — bounded spool-lane check

Using the +305 locator map, I checked the four support jobs in L-29/N binder order (PS-0399, PS-0386, PS-0411, PS-0404). One aligned 4-byte lane from each 16-byte ACK payload gives 4^4 = 256 candidates; none hits K04 after XOR with the routing masked_component. Including the selected PS-0417 ACK2 as one of four jobs and omitting each of the five jobs in turn gives 5*4^4 = 1,280 candidates; also no hit. Four CRC32 values of the four support payloads (both endian orders/permutations) and common 16-byte digests of their concatenation also gave no hit.

This does not validate the mapping as a producer; it remains a locator only. I am not proposing broader lane/digest sweeps.
