# K04 job-paired native spool commitment bridge (2026-11-23)

## Purpose

The supplied export contains only a reconstructed spool text log; the original native Windows `.SPL/.SHD` objects are absent. The existing pairer and commitment-window scanner were separate tools. This bridge composes them so an authorized original spool package can be tested directly against the unchanged K04 acceptance commitment without reconstructing a PRNG stream.

## Method

`agents/agent25/k04_native_spool_commitment_bridge.py` composes:
- `agents/agent43/h17_native_spool_pair_intake.py` for bounded, read-only nested-container intake and exact SPL/SHD pairing by container, parent path and normalized filename stem;
- a literal ASCII or UTF-16LE `PS-261003-0417` hit in the paired SHD;
- `work/h17_k04_binary_window_intake.py` to scan the paired SPL's raw 16-byte windows and supported encoded 16-byte tokens against the pinned K04 SHA-256, checking both direct component bytes and the exact route-mask XOR.

The wrapper requires one unique job-ID-bearing pair and one distinct commitment-matching component. It records SPL/SHD SHA-256, source path, pair key, candidate encoding, offset and raw window. It does not extract or modify source members.

## Validation

The synthetic control plants `payload = component XOR mask` at offset 6 in a synthetic `0417.SPL`, places the exact job ID in its paired `0417.SHD`, and adds a same-stem decoy pair under a different parent with a different job ID. The bridge recovers exactly the planted 16-byte component from the correct pair and ignores the decoy.

The test is `tests/test_h17_k04_native_spool_commitment_bridge.py`. It passed with the full targeted H-17 test suite, K08 profile scanner self-test, and revision/cache controls on [GitHub Actions run 45094353923](https://github.com/FlareZ123/workplace-v2/actions/runs/45094353923).

## Source application and limits

The supplied `h17-archive-dump.zip` has no native SPL/SHD members, so the bridge recovers no real K04 component in this run.

A job-ID string in SHD plus filename/container pairing is still a candidate association, not a full parse of undocumented SHD offsets. The wrapper does not infer class, destination, attempt or ACK state from the filename; independent queue/dispatch evidence must establish that the paired object is the routed `PS-261003-0417 / RECOVER / bench / ACK attempt 2` event. A commitment match establishes the 16-byte component, but event attribution must still be supported by the paired records.

When an already-authorized original spool directory or archive is available, run:

```bash
python agents/agent25/k04_native_spool_commitment_bridge.py --source /path/to/authorized/native-spool
```

The source is scanned in memory under the pairer's size/depth/path-safety limits. Preserve the original SPL/SHD files and independent queue/dispatch metadata.

## Confidence

- **High:** the source-pair and commitment-window composition passes the planted exact-hit and wrong-job decoy controls.
- **High:** the full targeted test suite and profile scanner self-test passed.
- **None:** no native SPL/SHD pair was present in the supplied export, so no actual K04 component or historical event attribution was recovered.
