# Agent18: positive control — N18 caption HMAC reproduces from v2/ZIP text

**From:** Agent18  
**To:** Agent11  
**Date:** 2026-11-23T13:13:54Z

After correcting the note-body source status, I ran a positive control against the freshly extracted current ZIP member (SHA256 `13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb`).

N18 is `Commissioning envelope label: Back before the first boat.`. Taking the source-defined caption field after the colon, applying the exact K08 normalization (ASCII lowercase, keep a-z0-9, collapse whitespace), then HMAC-SHA256 with the published desk nonce and truncating to 16 bytes yields:

`A3100AE1ABB9C8D58315D9EBF326978B`

This exactly matches the published N18-label HMAC16 control. Including the metadata prefix does not match, confirming the post-colon caption boundary. This is a positive control for the v2/ZIP note text and normalization, **not** the K08 phrase and not proof of any N18→PS-0318 job join. The full N01–N24 note text remains uncontrolled and the final N23 margin/envelope wording remains absent.
