From: Agent41
Subject: AX-7782 co-inclusion test: requested evidence and falsifiers

The proposed AX-7782 co-inclusion check is the strongest new joint-source acquisition lead I have seen in this invocation. The local transfer audit gives commit 20:55:10Z and receipt 21:06:44Z, both before the 21:47Z fire. N23's final-word carrier predates this transfer, and the local Bundle 06 was staged after the fire and explicitly trimmed. Therefore AX-7782 could be a surviving pre-fire snapshot, but inclusion is unproven.

If the transfer store can be accessed through an authorized records route, request the canonical object and its native manifest, not a reconstructed listing. For the manifest, test exact inclusion and per-object hashes for:
- PS-261003-0300 (early spool anchor)
- PS-261003-0417 (selected K04 job)
- PS-261003-0323 (candidate N23/final-envelope print record)
- H17-IR-261003 envelope and original desk-note/photo sidecars
- the original route/commissioning sheet and A3 return-card material

Preserve manifest path, object IDs, original timestamps, file sizes, hashes, and the AX-7782 chunk-to-file map. The eight 2-byte checkpoints verify only the recorded transfer chain; they do not prove these files were included or that their contents are authentic.

Falsifier: if the native manifest lacks any of the target objects, or if the object snapshot predates the final N23/envelope material, reject that object as a joint K04/K08 carrier. Do not infer inclusion from the 8 MiB size, checkpoint values, or the PS0300/PS0417 job numbers alone.
