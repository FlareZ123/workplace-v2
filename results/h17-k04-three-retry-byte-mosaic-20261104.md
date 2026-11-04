# K04: exhaustive three-retry byte mosaic

Agent 7 | 4 November 2026. This report documents a finite complete-candidate reconstruction hypothesis for H-17 K04. It does not recover a K04 value.

## Source-conditioned construction

The existing spool fragment source SHA256 is `7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083`. Job `PS-261003-0417` has three RECOVER records:

- Attempt 1, REQUESTED: `CD3E4F216ADB2FB180DA2AA90B33F7A4`
- Attempt 2, ACK: `A9A9DC5731A5E2AE879C47215C2559D5`
- Attempt 3, REQUESTED: `44D53DFC29D7943A95D89371DA58EC64`

Only attempt 2 is selected by the historical routing rule. For an exploratory reconstruction, independently select each of sixteen bytes from the corresponding position in any of these three observed records. XOR the resulting 16-byte buffer with the original routing mask and compare the full SHA256 of the resulting K04 value with the unchanged K04 commitment.

This allows changes at all sixteen positions, unlike already completed arbitrary four-byte replacement tests. It is a hypothetical byte-copy architecture, not an authenticated historical repair rule.

## Reproducible original-data result

The [standalone original-source-pinned C test](../agents/agent7/k04_recovers_mosaic_sft.c) tests exactly `3^16 = 43,046,721` complete assignments. It checks the original spool checksum, route mask and commitment before search and uses the same SHA256 path for a synthetic planted complete candidate.

The [manual original-source workflow run](https://github.com/FlareZ123/workplace-v2/actions/runs/41871875931) completed successfully on 4 November 2026, job `126720866248`. Its key output was:

```text
ORIGINAL_SPOOL_SHA_PIN_PASS; 0417 RECOVER_ATTEMPTS=1,2,3
COMPLETE_MOSAIC_ASSIGNMENTS=43046721 ORIGINAL_K04_HITS=0 SYNTHETIC_HITS=1
SOURCE_PIN_AND_FULL_DIGEST_POSITIVE_PASS; ORIGINAL_K04_NOT_RECOVERED
```

Thus no position-preserving byte mosaic from these three RECOVER attempts satisfies the original K04 commitment. The result does not rule out different copy/reassembly rules, independent original source, or a separately evidenced generator. It provides no authenticated selected-coupon bits. K04 and K08 remain unresolved, six of eight original components individually PASS and combined acceptance INCOMPLETE.

The one-shot manual workflow was removed after use to avoid persistent CI clutter. The reusable C source and GitHub Actions log remain available.
