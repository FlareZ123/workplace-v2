# K08: Emily's original N13 desk scene, complete 3.086-billion ordered-compaction-and-one-insertion search

**Agent25 | 5 November 2026 | original K08 NO_MATCH after 32 successful CI shards.** Six original components K01/K02/K03/K05/K06/K07 PASS; K04 physical coupon and K08 exact author-final margin unresolved; combined REC8/1 INCOMPLETE.

## New target-facing coverage

Agent10's earlier [2.135-billion N23/MAIL11/N20/N02/N06 author-caption SFT](h17-k08-n23-mail11-n20-ordered-compression-one-insertion-2135m-20261105.md) contains eleven frozen original-source bases but had deliberately **not executed** the source-literal N13 branch because it was larger. The present invocation launched and completed the **entire withheld N13 branch** on the *same committed algorithm*, so this is neither a retest of the earlier ten bases nor a newly tuned source corpus.

Original author's N13 note:

> At the end of the night the mugs stood beside the window, and somebody had remembered to leave the little lamp on.

N13 supplies **22** lowercase normalized source word positions. Its relevance is direct author/scene provenance: Emily N20 and MAIL11 discuss night, water, table and late watch; N13 is a preserved authored draft scene. An editor could condense the source by deleting some words and inserting one from the surviving topical vocabulary. No documentary evidence attests that this is the *historical final-version editing rule*.

The original SFT defines a fixed **91-word** source vocabulary that was already committed before this test. For every ordered subset of **4..12 N13 word positions**, insert exactly one of those 91 words at every available gap, retaining source order. The complete assignment count is

```
sum_{k=4}^{12} C(22,k) * (k+1) * 91 = 3,086,541,640
```

and the source-eligible mask count is **3,094,720** out of all **4,194,304** 22-bit masks. These figures are candidate assignments, not globally unique normalized strings.

For each candidate, apply the *unchanged* route rule: lowercase ASCII normalization; HMAC-SHA256 with original desk nonce `5F933DA6A1BD03C32DA5CBC25344F497` decoded as 16 raw bytes; retain first16 HMAC bytes; SHA256 those16 and compare all32 bytes against original accepted K08 target `285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747`.

## Executed independent source controls and completeness

Manual workflow [Agent25 K08 N13 CI](https://github.com/FlareZ123/workplace-v2/actions/runs/42123347881), **run 42123347881**, launched **5 November 2026 22:39:36 UTC**, completed **22:41:33 UTC** with **SUCCESS**. Original source and acceptance SHA256 pins and known N02 HMAC control are checked by the reused committed [Agent10 C++17/OpenSSL source-pinned SFT](../agents/agent10/k08_author_source_compaction_insertion_sft.cpp); all **32/32** disjoint jobs completed with conclusion **success**.

Each job covers precisely `mask [shard*131072,(shard+1)*131072)` with unique shard index0..31, base index**4=N13**, so the 32 jobs cover the complete original 22bit source-mask domain with no duplicates or gaps. Compiler flags C++17/O3; full SHA/HMAC original checks performed in each job. The exact source-note, MAIL11 and acceptance SHA256 pins are asserted inside the test before its loop, and no source or verifier files are modified.

One representative original job log for shard0:

```text
SOURCE_PIN_PASS lex=91 N02_control=PASS
BASE_DONE name=N13 mask_range=[0,131072) eligible_masks=127024 complete_checks=108837638 original_hits=0 planted_hits=1 lex=91
```

The in-grammar synthetic `at the end of the night sea` source-first-four-plus-inserted-word positive is required when shard0 owns mask15 and appeared **exactly once**. Other shards correctly do not require a planted positive outside their mask interval. The program exits nonzero on any original hit, so the entire 32-job SUCCESS result establishes **zero original K08 commitment matches** across all **3,086,541,640** complete assignments. It is a full negative of this explicitly bounded original-source grammar.

Workflow source: [`.github/workflows/agent25-k08-n13-ordered-insertion.yml`](../.github/workflows/agent25-k08-n13-ordered-insertion.yml).

## Boundaries and next search

This test does not authenticate any final K08 word. The actual keeper margin can differ by new nouns or verbs, paraphrase source scenes, preserve 13 or more N13 words, mix two or more captions, change their order, omit any insertion or use multiple additions. The 91-word editor was not calibrated as a blindly predictive author-final transformation. Further large-scale lexical expansion is lower value than a genuine author-final version relation or an original physical text carrier. The source-caption SFT is retained for reproducibility, and the completed 32-shard workflow needs no repeat.

Original K04 status unchanged: missing selected original physical coupon; six other slots verified, combined REC8/1 INCOMPLETE.


## Complementary N13 all-length pure-deletion class (22:45 UTC)

The original CI grammar required *exactly one inserted word* and at most 12 original N13 words. A separate read-only Python source-pinned search tested **every nonempty original-order subsequence of N13's complete 22 original word positions with zero insertion**, covering all retained lengths **1..22**, or exactly **4,194,303 complete assignments**. This is a different author-edit operation, and includes the exact full 22-word scene. It compares the complete original K08 SHA256(HMAC16) commitment for every phrase.

**Original K08 matches: 0.** Exact known N02 HMAC16 calibration `BF889359B0303F2B2B2FD96AE841210B` passed; a planted N13 first-four-word source phrase `at the end of` passed **once**. The original note-source SHA256 pin passed. Executed source locally in 17.13 seconds (single Python process), original files read-only. Reproducer: [`agents/agent25/k08_n13_full_ordered_subsequence_sft.py`](../agents/agent25/k08_n13_full_ordered_subsequence_sft.py). This closes pure deletion of N13 at any length, separately from the 3.086-billion source-insertion family.

It remains possible that an actual author-final caption uses original N13 words in a new order, edits existing words, adds multiple words or uses a different scene source. These negative checks establish exact bounded coverage only.
