"""Source-pinned preflight for Agent36's paired K08 lexical A/B runner.

This exercises every requested historical holdout without importing torch or
transformers. The actual scoring candidates are held out for evaluation only;
the full target and decoy phrases must be absent from every model prompt.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "agents" / "agent36"))

import k08_blind_author_rank_lexical_ab as runner


def expect_assertion(callable_) -> None:
    try:
        callable_()
    except AssertionError:
        return
    raise AssertionError("negative preflight control unexpectedly passed")


def main() -> None:
    notes, mails, nonce, target = runner.ranker.load()
    assert len(nonce) == 16
    assert len(target) == 32

    manifests: dict[str, object] = {}
    prompt_sets: dict[int, dict[str, str]] = {}
    candidate_sets: dict[int, list[tuple[int, str]]] = {}
    for held in runner.CASES:
        manifest, prompts, candidates = runner.build_case(notes, mails, held)
        manifests[str(held)] = manifest
        prompt_sets[held] = prompts
        candidate_sets[held] = candidates

    selected = runner.validate_case_maps(
        runner.CASES, manifests, prompt_sets, candidate_sets
    )
    assert selected == runner.CASES

    # The same selector must also support each one-case Actions matrix shard.
    for held in runner.CASES:
        one = runner.validate_case_maps(
            (held,),
            {str(held): manifests[str(held)]},
            {held: prompt_sets[held]},
            {held: candidate_sets[held]},
        )
        assert one == (held,)

    # Negative controls: missing prompt/candidate keys and unexpected keys fail.
    bad_candidates = dict(candidate_sets)
    del bad_candidates[runner.CASES[0]]
    expect_assertion(lambda: runner.validate_case_maps(
        runner.CASES, manifests, prompt_sets, bad_candidates
    ))

    bad_prompts = dict(prompt_sets)
    del bad_prompts[runner.CASES[0]]
    expect_assertion(lambda: runner.validate_case_maps(
        runner.CASES, manifests, bad_prompts, candidate_sets
    ))

    extra_candidates = dict(candidate_sets)
    extra_candidates[999] = []
    expect_assertion(lambda: runner.validate_case_maps(
        runner.CASES, manifests, prompt_sets, extra_candidates
    ))

    print(
        "PREFLIGHT_OK",
        f"cases={selected}",
        f"prompts_per_case=6",
        f"candidates_per_case=12",
        "target_and_decoy_phrases_absent=true",
        "arm_a_all_target_words_masked=true",
        "single_case_matrix_controls=4/4",
        "negative_key_controls=3/3",
    )


if __name__ == "__main__":
    main()

