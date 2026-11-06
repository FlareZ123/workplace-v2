# H-17 original ZIP entry-order residual: one five-item root ordering

**Agent 41 | 6 November 2026 | Read-only original-container experiment.** This investigates the one remaining packaging-order variable highlighted by the [5 November 14:09 UTC Critic](../communications/broadcast/20261105T1409Z_Critic_portfolio-and-zip-order-residual.md). No original K04 or K08 component recovered. Original six individual PASS, K04/K08 missing, combined INCOMPLETE.

## Exact question and source

Could the **order of the existing 56 ZIP entries**, which is distinct from their exact decoded bytes, have been deliberately varied to carry a complete missing recovery input? Earlier [ZIP wrapper](h17-zip-container-channel-audit.md) and [DEFLATE](h17-zip-deflate-unused-bits-and-recompression-20261104.md) analyses accounted for container bytes and coding but had not characterized the remaining *entry-order degrees of freedom*. A free permutation of all entries misleadingly overestimates its potential entropy if the entries obey an ordinary recursive filesystem walk.

Use only the original uploaded 50,526-byte 56-entry ZIP, SHA256 `e778552c555fac652e24fd09e1c4f31bd066b4686e624b91f6e94e1d64342bf7`. The [standalone standard-library SFT](../agents/agent41/h17_zip_entry_order_sft.py) reads `ZipInfo.header_offset` for the physical local-header order, the central-directory order, and the 56 existing pathnames; it never rewrites the ZIP. All 46 files and 10 directory entries are counted. Construct exact parent/direct-child lists from POSIX paths, preserving existing entry order. Compare each nonroot directory's children against their independently reconstructed case-insensitive lexical sort; also check complete recursive depth-first placement.

## Original observations

1. **Local-header physical order and central-directory order are exactly identical**, so there is no independent two-order disagreement.
2. **All ten nonroot directories** have their direct children already in case-insensitive lexical order. Nine have at least two direct children; the tenth is a one-child trivial check. The distinctive `evidence/procedures/` child order is `document-register.log` then `RC-17-scans.txt`, consistent with casefold ordering and inconsistent with raw ASCII byte sorting. Entire nested `evidence/` subtree is also contiguous, recursive depth-first.
3. The *only* top-level noncanonical sibling set consists of five entries in this exact original order: `START_HERE.md`, `verify.py`, `evidence/`, `acceptance.json`, `candidate.template.json`. It is a plausible explicit package-argument order (intro, checker, evidence, acceptance, template), although this test cannot prove the actual archive-building command.
4. Relative to the observed casefold rule applied below root, **zero nonroot permutation choices remain**. The **unexplained root-only permutation capacity is log2(5!) = 6.90689 bits**. For comparison, the ten nonroot sibling groups *if* their order were unconstrained would collectively allow 106.47508 theoretical bits of order choice. The free 46-file permutation bound does not describe this archived layout.

Read-only program output:

```text
ORIGINAL_ZIP_SHA_OK members=56 files=46 dirs=10
LOCAL_CENTRAL_ENTRY_ORDER_EQUAL=True
RECURSIVE_CANONICAL_SIBLING_GROUPS=10/10
ONLY_NONCANONICAL_SIBLING_SET=root (5 members): ['START_HERE.md', 'verify.py', 'evidence/', 'acceptance.json', 'candidate.template.json']
RESIDUAL_ROOT_ORDER_CAPACITY_BITS=6.90689
CANONICAL_NONROOT_PERMUTATION_BITS=106.47508
SYNTHETIC_ONE_SIBLING_SWAP_FLAGGED=True
```

**Counterfactual detection control:** Swap the two original positions `evidence/mail/01.eml` and `evidence/mail/02.eml` **in memory only**. The same checker changes the canonical nonroot sibling count from 10/10 to 9/10, while preserving depth-first ordering. The real ZIP is unmodified.

## What this resolves and what it does not

This source experiment favors ordinary case-insensitive recursive packaging over a high-entropy, deliberately permuted file-order channel. The source's 56-member tree does not actually exhibit the hypothesized ~192-bit free-file permutation. The measured remaining top-level order has at most 6.9 bits under the now-explicit parent/sibling model. No source-selected text or 16-byte coupon is obtained from that order, and no K04/K08 digest is tested.

An unusual *small* root permutation could still expand through an undocumented KDF, or filenames and content could encode information by a completely different mechanism. This observation does **not** prove all ZIP-based steganography impossible, and the casefold rule is empirically inferred rather than historically attested. It does warrant **ending further arbitrary ZIP entry-order guessing** until a concrete root-order encoding or contrary packaging witness appears.

Original recorded six PASS / K04-K08 unresolved status remains unchanged. No original ZIP, route, candidate, acceptance, or verifier was altered.
