# Agent 5 research continuity: H-17 REC8/1

**Lease:** claimed UTC 2026-10-20T05:34:28Z; run_id `1e0259e7-49b8-4e6a-839c-a905d6b0e91a`. Do not refresh. After every checkpoint, measure actual UTC lease age; only self-release at >=70 minutes. Selected normal research mode by executed secure 1..10 RNG draw = 2.

## Primary state

- Read repo `README.md`: do **not** create per-commit workflows. Repo: `FlareZ123/workplace-v2`, main branch. Successfully claimed and verified Agent 5 lease.
- Actual user-supplied ZIP: `/mnt/data/h17-archive-dump.zip`, SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`; extracted locally under `/mnt/data/h17/`. Agent 4's published Git SHA tree check proves 46 source file bytes equal `resources/` on main. Prior-v1 reports (>180) cover the same original source corpus; study `results/h17-v1-prior-art-gate.md` and v1 `results/README.md` before any new attempt.
- Independently ran user's untouched ZIP `verify.py` against six known K values: **K01 K02 K03 K05 K06 K07 PASS; K04/K08 MISSING; combined INCOMPLETE, accepted=false**. Their canonical hex values are `candidate.json`.
- **K04:** logical route ESC-N selects PS-261003-0417, last ACK RECOVER attempt2. Retained XOR candidate `2CFF149C50E54557228E7DE60B3EB7C9` fails immutable K04 SHA256. v1 completely exhausted arbitrary one/two/three different-byte corrections (9.28557 billion three-byte cases, independent positive controls), leaving >=4 byte changes relative to baseline but no authentic payload bytes. Global MT19937 conditional source studies show zero selected bits without independent source-indexed target ancestors. No unguided 4-byte CI.
- **K08:** actual final personal caption in Emily's margin is absent. N02/N06 drafts, N17/N18 other envelopes, N13/N20/N23 semantic notes. HMAC verifier cannot invert unquoted phrase; all original source-carrier tests negative. Zero authenticated final words.
- Historical missing source leads: original ESC-N coupon/integrity witness, Emily's literal final margin, or authorized preserved `file:///R:/Records/INDEX/IR-261003-H17.txt` index. `Issues/1` is a precise source request; no reply at inspection.

## This incarnation's narrow new work

- **Examined ZIP container itself**, distinct from Agent4's extracted-file Git blobs. Reproducible script committed: `work/h17_zip_container_audit.py`; findings: `results/h17-zip-container-channel-audit.md`.
- 56 members, 46 deflated files +10 stored dirs; 46 normal data descriptors, no duplicate paths, no comments, no prefix/trailer/between-member gaps; 112 standard Unix UID/GID and timestamp extra fields, timestamps 19–20 October packaging period, no target text. All 46 compressed streams **reproduce exactly** with local zlib 1.3.1 raw DEFLATE level6. No free-standing ZIP-layer target witness found. This is a negative bounded source-location finding, not solved recovery.
- Discovered **v1 has older 43-member ZIP forensic reports** `h17-zip-header-redundancy.md`, `h17-zip-deflate-padding.md`, `h17-zip-deterministic-repack.md`. They studied different ZIP SHA `a801d9...`; our result is specific to newly supplied 56-member ZIP and should not be promoted as new actual key information.
- External keyword web search for public Noyes H-17/caption surfaced nothing authenticated; prior v1 public-site/media census already inspected 11 reachable pages plus asset links. Do not probe protected portal.

## Worthwhile next research

Identify a genuinely new original independent target-bearing source and test it against withheld intact-source controls, or an evidenced producer/ordering rule that reduces 128-bit K04 quotient. Preserve no fabricated K08 wording and avoid repetitive ZIP/CIR/MT speculation. If no authentic witness appears, maintain precise six-of-eight status rather than claim success.


## Further source-bound QA and cross-agent state (2026-10-20 ~06:21Z)

- First raw ZIP parser had a blind spot: mutating local extended-time mtime while central-directory mtime remained unchanged was accepted. **Corrected** `work/h17_zip_container_audit.py` to explicitly compare local/central required version, flags, method, DOS time/date, UT mtime, UID/GID; reject nonzero descriptor-backed local CRC/size placeholders; validate expected ZIP creator OS, permissions, central entry offsets and EOCD size/offset.
- Ran original supplied ZIP under the corrected parser: all 56 entries pass. Built/committed `work/test_h17_zip_container_audit.py`, read-only positive-control SFT. Original SHA remains e778...; **8/8 deliberately corrupted scratch copies** rejected (trailer, local UID, UT mtime, DOS time, local CRC, data descriptor, central creator, central mode) and original source untouched. Strengthened `results/h17-zip-container-channel-audit.md` with falsification controls and precise time distribution. All 46 deflate streams are exact standard zlib1.3.1 level6 reproductions.
- Source ZIP timestamps: all 46 file ctime = 2026-10-19 20:09:30Z; file mtime split 26 at 2026-10-20 04:12:14Z and 20 at 04:12:16Z. atimes are four packaging-cluster values. No incident-time information.
- Published `communications/broadcast/20261020T0600Z_agent5-zip-container-channel-audit.md`. Added source-bound paragraph and links in `results/README.md`.
- Cross-project Files tool confirmed only the two user uploads `h17-archive-dump.zip` and `prompt.md`; no separate caption/index file exists among current Project files. `private/` contains only `.gitkeep`. This is a current-invocation source-location observation, not a permanent guarantee.
- Agent6's 20261020T0620Z broadcast checked v1/v2 Git path histories: each original content file has only its import commit, main only, no published release. No alternate original from visible commits. Earlier v1 source research confirmed public Noyes/Wayback/urlscan/credential-free index checks negative. Avoid repeating.
- Worker-agent consultation attempted; external worker endpoint returned HTTP 404/unavailable. No independent worker result.
- No additional original coupon or exact final caption was located, so six-slot canonical candidate unchanged. Prior v1 K04 model-dependent future-donor XOR relations would require historically indexed independent words at 1412/1866 or authentic coupon; no available original source gives those indexed words. Human custodian issue #1 remains open with zero comments at 06:10Z.

