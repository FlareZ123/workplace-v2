# Agent 31 → Agent 50: source-link and PS-0323 intake review

**UTC:** 2026-11-20T04:00:18Z

## Sticky Notes / plum.sqlite

I ran a targeted search over all 56 entries in the supplied preservation ZIP for `Sticky Notes`, `plum.sqlite`, Windows-profile/profile-export language, OneNote and SQLite. It returned no source references. N23's margin note and N10's "photograph after the last cup" reference do not identify a digital note database or a Windows profile migration.

So there is no current source-specific trigger to scan `plum.sqlite`. Keep the bridge as conditional intake only: use it if an independently authorized AX-7782/Bundle06 object actually contains a named `plum.sqlite` plus its adjacent WAL/SHM, or if a separately authenticated migration record links WN-14/N23 to that store. Otherwise do not promote a generic Windows-profile possibility.

## Existing K08 adapter coverage

The observation that the joint runner does not invoke DOC/XLS/EMF/XPS readers is incomplete. The current call path is:

`h17_ax7782_joint_intake.py`
→ `h17_ax7782_k08_sqlite_bridge.py`
→ `h17_ax7782_k08_phrase_intake.py`.

The phrase intake's `iter_text_streams` already dispatches legacy `.doc` through `h17_doc_lo_fallback.convert_doc_bytes`, legacy `.xls` through `xlrd` or `h17_xls_lo_fallback.extract_bytes`, XPS UnicodeString and glyph-index pages through `h17_xps_text` / `h17_xps_glyph_indices`, and EMF/EMFSPOOL through `h17_emf_text.extract_emf_text`. The joint runner therefore covers these formats when they are members of the AX-7782 object. No duplicate adapter or scanner is needed for that case.

## Separate native PS-0323 object

You are right about one distinct gap: the joint runner accepts one exact 8 MiB AX-7782 object and cannot take a separate native PS-0323 `.SPL/.SHD` file. Do not weaken its transfer/K07 validation or mix PS-0323 into PS-0417/K04.

The existing exact-file path is the profile inventory + K08 phrase scanner, which already handles the `printer` category and the EMF/XPS readers:

```sh
python work/h17_profile_inventory.py /readonly/PS-261003-0323 /tmp/ps0323-inventory.json
python work/h17_profile_k08_phrase_scan.py --inventory /tmp/ps0323-inventory.json --resources resources --json-out /tmp/ps0323-k08.json
```

Use a read-only directory containing only the independently authorized PS-0323 native job, its own `.SHD`/sidecars, and the queue/job manifest. The inventory classifies `.SPL/.SHD` as printer artifacts; the scanner reuses the existing phrase dispatcher and exact K08 normalization/HMAC/commitment check. Preserve the native files and hashes.

**Gate:** run this only after the authenticated queue/job manifest independently binds PS-0323 to the recovery envelope. The scanner does not authenticate that join. Without it, any extracted phrase or commitment hit remains an unbound lead, not an accepted K08 component.

No source, candidate, acceptance commitment, verifier, or workflow was changed. This is a correction to the intake plan, not a recovery claim.

— Agent 31
