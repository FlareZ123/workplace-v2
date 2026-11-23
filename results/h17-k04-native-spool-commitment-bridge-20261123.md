# K04 native spool commitment-first recovery bridge (2026-11-23)

## Purpose and current decision

The supplied H-17 export contains a reconstructed printer text log but no authenticated original Windows `.SPL/.SHD` objects. The existing intake pairer and exact K04 commitment scanner have been composed into one native-source recovery path. The initial version screened **only** SPL/SHD pairs whose shadow contained the literal application identifier `PS-261003-0417`. Agent43's 23 November review identified a concrete false-negative: Windows spooler job IDs need not equal the application's PS label, and retained binary SHD metadata need not contain that text.

**Current implementation now scans every eligible native SPL for a complete K04 commitment hit, regardless of SHD availability and application-label text.** This is a source-independent selection repair. It does not recover any historical missing K04 component from the current export.

## Method

`agents/agent25/k04_native_spool_commitment_bridge.py` composes:

1. [Native SPL/SHD pairer](../agents/agent43/h17_native_spool_pair_intake.py) for bounded, read-only native-directory and nested-container intake; metadata association is by same container, parent path and normalized filename stem.
2. [Existing K04 native/rendered-media scanner](../work/h17_k04_binary_window_intake.py) for **every** discovered SPL byte stream, scanning raw 16-byte windows and encoded 16-byte tokens, as well as source-rendered EMFSPOOL/XPS glyph text and supported raster/barcode representations. ZIP/OPC-formatted native `.SPL` files retain their SPL identity, while their rendered content is decoded for exact commitment checks. It accepts SHA256 of a direct 16-byte component or the exact original masked-payload XOR, both compared against the original full 256-bit K04 commitment.
3. *After complete component detection*, attach optional paired SHD filename/hash and an optional literal ASCII/UTF-16LE application job-ID observation. Report the event-attribution flag as **unverified** regardless of the cryptographic hit.

The output retains per-SPL and per-SHD source SHA256, container/path/stem, scan offsets, encoding, raw candidate windows and all matching complete components. It sets `recovered=true` only when exactly one distinct 16-byte component matches the original commitment across scanned source files. Multiple copies of the same cryptographic component do not create different keys. A missing or mismatched SHD string cannot veto an original cryptographic hit.

A 16-byte commitment match establishes the correct *key component*. An additional contemporaneous queue/dispatch manifest joining the native Windows spooler numeric job identity and timestamp to the logical `PS-261003-0417 / RECOVER / bench / ACK attempt 2` remains necessary to authenticate historical physical-event attribution.

## End-to-end tests

Agent25's initial synthetic paired-spool/decoy test passed with the previous scanner in [Actions run 45094353923](https://github.com/FlareZ123/workplace-v2/actions/runs/45094353923).

The amended `self_test()` exercises **three exact complete-component positive scenarios** under the unchanged cryptographic reduction:

| Synthetic original-source layout | Original K04 component | Literal PS label at matching source |
| --- | --- | --- |
| A matching SPL/SHD pair whose SHD carries PS-261003-0417 | Recovered | Yes |
| A matching SPL with binary/unlabelled SHD, alongside a wrong-payload decoy pair whose SHD *does* carry PS-261003-0417 | Recovered | No |
| A genuine SPL without a surviving SHD file | Recovered | No |
| A ZIP/OPC-formatted native `.SPL` containing a two-run rendered XPS coupon, paired with SHD | Recovered | Yes |
| A Windows filesystem spool directory holding a real `.SPL/.SHD` filename pair, where the `.SPL` is a nested ZIP/OPC XPS coupon with two printed Glyphs runs | Recovered | Yes |

The regression establishes that source selection cannot suppress a complete commitment match and that a ZIP/XPS native `.SPL` is neither discarded as a nested archive nor reduced to uninterpreted binary bytes. The XPS coupon is deliberately split over two native `Glyphs` runs, so the raw byte-window and contiguous-hex-only scanner cannot detect it. Existing EMFSPOOL, XPS and barcode decoders are reused unchanged. Initial amended self-test completed successfully on [Actions run 45129826120](https://github.com/FlareZ123/workplace-v2/actions/runs/45129826120). The original public unit test's `matching_pairs` and `candidate_offset` result keys were subsequently preserved for compatibility. The [second manual Actions run 45130094612](https://github.com/FlareZ123/workplace-v2/actions/runs/45130094612) then **passed both the amended three-case self-test and the original compatibility unit test**. The subsequent [Actions run 45131360229](https://github.com/FlareZ123/workplace-v2/actions/runs/45131360229) **passed the four-case test including native ZIP/XPS SPL and the unchanged original compatibility unit test**. An independent **Windows runner** execution [Actions run 45133633176](https://github.com/FlareZ123/workplace-v2/actions/runs/45133633176) **passed the same four-case key tests, the original bridge unit test and the native SPL/SHD pairer's own self-test**, exercising the code on the operating-system family that actually generates the source files. A subsequent **Windows runner** [Actions run 45133865219](https://github.com/FlareZ123/workplace-v2/actions/runs/45133865219) **passed five full-key positive cases**, including a physical filesystem `.SPL/.SHD` directory containing a ZIP/OPC XPS spool file, as well as both original unit-test suites.

Source/test commits:
- `a5dd961caded5b0ec8fa3bc54779965a4f963c71`: commitment-first selection;
- `d1ce458f9c51403e2cafbdf507b8f55b61283993`: three complete-component synthetic cases;
- `1964a18e8c1f28c797c4c4cbdda73119779b798d`: retain original unit-test API;
- `418bb6b7f41f1d4f697031ba6b660bc325144d8f`: manual test includes original compatibility test.
- `bccb7244b5d81c671b46b5f7590439d07b93c9b2`: preserve package-formatted SPL identity inside native archive intake;
- `2fbccde5f3475284010081fc9ff2b4c8b0c86830`: compose existing rendered-media scanner for every SPL;
- `dfa7dc57658e282db291c79cf3ef42b347a00116`: prove split XPS page-text recovery in the complete spool bridge.

## Historical source boundary

The unchanged `h17-archive-dump.zip` has no native SPL/SHD original for this route. The original copied ACK2's lack of an independent payload-integrity checksum remains. No real K04 component, original physical coupon or 8/8 REC8/1 recovery has been obtained. No source, route, acceptance, verifier or canonical candidate was modified. K08's final exact author-written phrase remains a separate missing source.

To run the already-created read-only scanner when authorized native spool files are supplied, use the repo's `agents/agent25/k04_native_spool_commitment_bridge.py` entry point with `--source` set to the preserved original spool folder or archive. Preserve its companion manifest for event attribution.

**Confidence:** High that the targeted parser selection and native rendered-coupon false-negatives are fixed for the five exact supported synthetic source structures; Linux and Windows executions passed. These controls do not prove all real printer implementations, historical source attribution, or recover a K04 component from the existing 46-file export.
