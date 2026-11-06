"""Paired K08 missingness-matched recovery test.

Arm A removes the held-out caption's word types globally (strict author-style
stress test). Arm B removes only the whole held-out line and exact quotations,
retaining independently authored occurrences of its words. Both arms use the
same Qwen model, purpose/generic prompts, and 11 authentic note decoys.
Arm B also emits a frozen candidate stream for each authentic holdout and for
the N23 final keeper caption, then contacts the untouched K08 commitment.

Run from the repository root:
  python agents/agent5/k08_absence_matched_exact_recovery_sft.py --smoke
  python agents/agent5/k08_absence_matched_exact_recovery_sft.py --samples 100 --final-samples 256
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
CREW_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MAIL11_SHA = "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"
ROUTE_NONCE = "5F933DA6A1BD03C32DA5CBC25344F497"
K08_TARGET = "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
ROLE = {
    2: "First draft for a crew common-area board: human handover after a watch.",
    6: "Second private desk draft: a small light and an empty night corridor.",
    17: "Older standby-envelope label intended for the upcoming watch.",
    18: "Older commissioning-envelope label, a boat and the first crossing.",
    0: "Final keeper-envelope desk margin: people making room after a late watch, the sea outside, night nearly finished, and voices around a table.",
}
CASES = (2, 6, 17, 18)
COMPETING_LABELS = (17, 18)


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def norm(text: str) -> str:
    return " ".join(tokens(text))


def caption(text: str) -> str:
    return text.split(":", 1)[-1].strip()


def line_pattern(phrase: str) -> re.Pattern[str]:
    words = tokens(phrase)
    assert words
    return re.compile(
        r"(?<![A-Za-z0-9])" + r"[^A-Za-z0-9]+".join(re.escape(w) for w in words)
        + r"(?![A-Za-z0-9])",
        re.IGNORECASE,
    )


def load(root: Path):
    notes_raw = (root / "evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    mail11_raw = (root / "evidence/mail/11.eml").read_bytes()
    assert hashlib.sha256(notes_raw).hexdigest() == CREW_SHA
    assert hashlib.sha256(mail11_raw).hexdigest() == MAIL11_SHA
    parsed = re.findall(r"N(\d\d) / ([^\n]+)\n([^\n]+)", notes_raw.decode("utf-8"))
    notes = {int(n): (author.split()[0], text) for n, author, text in parsed}
    assert list(notes) == list(range(1, 25))
    assert {i for i, (author, _) in notes.items() if author == "Emily"} == {
        2, 6, 10, 13, 17, 18, 20, 23
    }
    mails = {
        i: (root / f"evidence/mail/{i:02d}.eml").read_text(encoding="utf-8").split("\n\n", 1)[-1]
        for i in (11, 20)
    }
    route = json.loads((root / "evidence/recovery-routing.json").read_text(encoding="utf-8"))
    acceptance = json.loads((root / "acceptance.json").read_text(encoding="utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    assert nonce.hex().upper() == ROUTE_NONCE
    assert target.hex() == K08_TARGET
    n02 = norm(caption(notes[2][1]))
    assert hmac.digest(nonce, n02.encode(), "sha256")[:16].hex().upper() == (
        "BF889359B0303F2B2B2FD96AE841210B"
    )
    return notes, mails, nonce, target


def decoys(notes: dict[int, tuple[str, str]], held: int):
    target = caption(notes[held][1])
    target_len = len(tokens(target))
    rows = [(i, caption(text)) for i, (_, text) in notes.items() if i != held]
    rows.sort(key=lambda item: (abs(len(tokens(item[1])) - target_len), item[0]))
    return rows[:11]


def replace_exact_phrase(text: str, phrase: str) -> tuple[str, int]:
    pattern = line_pattern(phrase)
    return pattern.subn("[withheld exact quotation]", text)


def purpose(held: int, use_purpose: bool) -> str:
    role_id = 0 if held == 23 else held
    return ROLE[role_id] if use_purpose else "A historical H-17 crew note."


def prompt_parts(notes, mails, held: int, excluded: frozenset[int], use_purpose: bool):
    parts = [
        f"N{i:02d} by {author}: {text}"
        for i, (author, text) in notes.items()
        if i != held and i not in excluded
    ]
    parts += [f"MAIL{i:02d}: {body}" for i, body in mails.items()]
    return (
        "Predict one missing original caption by Emily using the incomplete record.\n"
        "Historical excerpts:\n" + "\n".join(parts)
        + "\nTarget purpose: " + purpose(held, use_purpose)
        + "\nRespond with one full line only:"
    )


def sanitized_mails(notes, mails, held: int, excluded: frozenset[int], arm: str):
    cleaned = {}
    removed = {}
    phrases = [caption(notes[i][1]) for i in sorted(excluded)]
    if arm == "B":
        phrases.append(caption(notes[held][1]))
        if held in COMPETING_LABELS:
            phrases.extend(caption(notes[i][1]) for i in COMPETING_LABELS)
    for mail_id, original in mails.items():
        body = original
        counts = {}
        for phrase in dict.fromkeys(phrases):
            body, count = replace_exact_phrase(body, phrase)
            if count:
                counts[norm(phrase)] = count
        cleaned[mail_id] = body
        removed[mail_id] = counts
    return cleaned, removed


def strict_arm_a(notes, mails, held: int, excluded: frozenset[int], use_purpose: bool):
    target = caption(notes[held][1])
    forbidden = set(tokens(target))
    safe_mails, _ = sanitized_mails(notes, mails, held, excluded, "A")
    prompt = prompt_parts(notes, safe_mails, held, excluded, use_purpose)
    prompt = re.sub(
        r"\b[A-Za-z0-9]+\b",
        lambda match: "[withheld]" if match.group().lower() in forbidden else match.group(),
        prompt,
    )
    assert not (set(tokens(prompt)) & forbidden), (held, sorted(set(tokens(prompt)) & forbidden))
    return prompt


def phrase_only_arm_b(notes, mails, held: int, excluded: frozenset[int], use_purpose: bool):
    target = caption(notes[held][1])
    safe_mails, mail_removals = sanitized_mails(notes, mails, held, excluded, "B")
    prompt = prompt_parts(notes, safe_mails, held, excluded, use_purpose)
    # The held-out full line and all exact quotations of removed decoys are
    # absent. Independent uses of individual words remain intact.
    phrases_to_remove = [target]
    if held in COMPETING_LABELS:
        phrases_to_remove.extend(caption(notes[i][1]) for i in COMPETING_LABELS)
    prompt_removals = {}
    for phrase in dict.fromkeys(phrases_to_remove):
        prompt, count = replace_exact_phrase(prompt, phrase)
        if count:
            prompt_removals[norm(phrase)] = count
    assert norm(target) not in norm(prompt), (held, "full target quotation remains")
    source_parts = [
        f"N{i:02d} by {author}: {text}"
        for i, (author, text) in notes.items()
        if i != held and i not in excluded
    ]
    source_parts += [f"MAIL{i:02d}: {body}" for i, body in safe_mails.items()]
    source_only = "\n".join(source_parts)
    for phrase in dict.fromkeys(phrases_to_remove):
        source_only, _ = replace_exact_phrase(source_only, phrase)
    source_words = tokens(source_only)
    retained = {
        word: source_words.count(word)
        for word in sorted(set(tokens(target)))
    }
    assert sum(retained.values()) > 0, (held, "Arm B retained no target vocabulary")
    return prompt, {
        "mail_exact_quote_removals": mail_removals,
        "remaining_context_exact_quote_removals": prompt_removals,
        "retained_independent_word_occurrences": retained,
    }


def exact_source_occurrences(root: Path, phrase: str):
    occurrences = []
    pattern = line_pattern(phrase)
    for path in sorted((root / "evidence").rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        count = len(pattern.findall(text))
        if count:
            occurrences.append({"path": path.relative_to(root).as_posix(), "count": count})
    return occurrences


def chat(tokenizer, prompt: str) -> str:
    return tokenizer.apply_chat_template(
        [
            {"role": "system", "content": "Return one complete crew caption only."},
            {"role": "user", "content": prompt},
        ],
        tokenize=False,
        add_generation_prompt=True,
    )


def logprob(model, tokenizer, torch, prefix: str, sentence: str) -> float:
    ids = tokenizer(prefix, return_tensors="pt", add_special_tokens=False).input_ids
    suffix = tokenizer(" " + sentence, return_tensors="pt", add_special_tokens=False).input_ids
    all_ids = torch.cat((ids, suffix), dim=1)
    with torch.inference_mode():
        logits = model(all_ids).logits[0, ids.shape[1] - 1:-1]
    score = torch.nn.functional.log_softmax(logits, dim=-1).gather(
        1, suffix[0].unsqueeze(1)
    ).sum()
    return round((score / suffix.shape[1]).item(), 6)


def generate_stream(model, tokenizer, torch, prompt: str, count: int, seed: int):
    prefix = chat(tokenizer, prompt)
    inputs = tokenizer(prefix, return_tensors="pt", add_special_tokens=False)
    outputs = []
    batch_size = 8
    for start in range(0, count, batch_size):
        batch = min(batch_size, count - start)
        torch.manual_seed(seed + start)
        with torch.inference_mode():
            generated = model.generate(
                input_ids=inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=42,
                do_sample=True,
                temperature=0.8,
                top_p=0.9,
                top_k=50,
                num_return_sequences=batch,
                pad_token_id=tokenizer.eos_token_id,
            )
        for row in generated:
            text = tokenizer.decode(
                row[inputs.input_ids.shape[1]:], skip_special_tokens=True
            ).splitlines()[0].strip()
            outputs.append(text)
    return outputs


def smoke(root: Path):
    notes, mails, nonce, target = load(root)
    report = []
    for held in CASES:
        excluded = frozenset(i for i, _ in decoys(notes, held))
        phrase = norm(caption(notes[held][1]))
        arm_a = strict_arm_a(notes, mails, held, excluded, True)
        arm_b, manifest = phrase_only_arm_b(notes, mails, held, excluded, True)
        assert phrase not in norm(arm_a)
        assert phrase not in norm(arm_b)
        report.append({
            "case": held,
            "decoys": sorted(excluded),
            "target_words": len(tokens(phrase)),
            "arm_a_sha256": hashlib.sha256(arm_a.encode()).hexdigest(),
            "arm_b_sha256": hashlib.sha256(arm_b.encode()).hexdigest(),
            "arm_b_manifest": manifest,
            "exact_occurrences_in_evidence": exact_source_occurrences(root, phrase),
        })
    final_prompt, final_manifest = phrase_only_arm_b(
        notes, mails, 23, frozenset(), True
    )
    assert norm(caption(notes[23][1])) not in norm(final_prompt)
    report.append({
        "case": "N23-final",
        "prompt_sha256": hashlib.sha256(final_prompt.encode()).hexdigest(),
        "manifest": final_manifest,
        "exact_occurrences_in_evidence": exact_source_occurrences(
            root, norm(caption(notes[23][1]))
        ),
    })
    print(json.dumps({
        "status": "SMOKE_OK",
        "crew_sha256": CREW_SHA,
        "mail11_sha256": MAIL11_SHA,
        "nonce": ROUTE_NONCE,
        "target_sha256": K08_TARGET,
        "cases": report,
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd() / "resources")
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--final-samples", type=int, default=256)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("h17-k08-absence-matched-output.json"))
    args = parser.parse_args()
    if args.samples < 1 or args.final_samples < 1:
        raise SystemExit("sample counts must be positive")
    if args.smoke:
        smoke(args.root)
        return

    notes, mails, nonce, target = load(args.root)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float32, low_cpu_mem_usage=True
    )
    model.eval()

    result = {
        "model": MODEL,
        "crew_sha256": CREW_SHA,
        "mail11_sha256": MAIL11_SHA,
        "nonce": ROUTE_NONCE,
        "target_sha256": K08_TARGET,
        "controls": [],
        "final_candidates": [],
    }

    for case_index, held in enumerate(CASES):
        target_sentence = norm(caption(notes[held][1]))
        excluded = frozenset(i for i, _ in decoys(notes, held))
        candidates = [(held, target_sentence)] + [
            (i, norm(text)) for i, text in decoys(notes, held)
        ]
        arm_data = {}
        for arm_name, builder in (("A", strict_arm_a), ("B", phrase_only_arm_b)):
            ranks = {}
            for purpose_name, use_purpose in (("proper", True), ("generic", False)):
                built = builder(notes, mails, held, excluded, use_purpose)
                prompt, manifest = built if arm_name == "B" else (built, {})
                prefix = chat(tokenizer, prompt)
                scores = [
                    {"note": note_id, "score": logprob(model, tokenizer, torch, prefix, sentence)}
                    for note_id, sentence in candidates
                ]
                scores.sort(key=lambda item: (-item["score"], item["note"]))
                rank = next(i for i, item in enumerate(scores, 1) if item["note"] == held)
                ranks[purpose_name] = {
                    "rank": rank,
                    "out_of": len(scores),
                    "true_logprob": next(item["score"] for item in scores if item["note"] == held),
                    "scores": scores,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "manifest": manifest,
                }
            arm_data[arm_name] = ranks

        arm_b_prompt, arm_b_manifest = phrase_only_arm_b(
            notes, mails, held, excluded, True
        )
        generated = generate_stream(
            model, tokenizer, torch, arm_b_prompt, args.samples,
            20261106 + case_index * 10000,
        )
        stream = []
        seen = set()
        first_exact_raw = None
        first_exact_unique = None
        for raw_rank, text in enumerate(generated, 1):
            phrase = norm(text)
            if not phrase:
                continue
            exact = phrase == target_sentence
            if exact and first_exact_raw is None:
                first_exact_raw = raw_rank
            if phrase not in seen:
                seen.add(phrase)
                stream.append({"raw_rank": raw_rank, "phrase": phrase, "exact": exact})
                if exact and first_exact_unique is None:
                    first_exact_unique = len(stream)
        result["controls"].append({
            "held_note": held,
            "target_normalized": target_sentence,
            "decoy_note_ids": sorted(excluded),
            "arm_a": arm_data["A"],
            "arm_b": arm_data["B"],
            "arm_b_candidate_stream": {
                "raw_samples": len(generated),
                "unique_normalized": len(stream),
                "exact_hit_at_raw_rank": first_exact_raw,
                "exact_hit_at_unique_rank": first_exact_unique,
                "hit_at_100": first_exact_raw is not None and first_exact_raw <= 100,
                "stream": stream,
            },
            "arm_b_manifest": arm_b_manifest,
            "evidence_exact_occurrences": exact_source_occurrences(
                args.root, target_sentence
            ),
        })

    final_prompt, final_manifest = phrase_only_arm_b(
        notes, mails, 23, frozenset(), True
    )
    final_generated = generate_stream(
        model, tokenizer, torch, final_prompt, args.final_samples, 20261106 + 90000
    )
    final_seen = set()
    for raw_rank, text in enumerate(final_generated, 1):
        phrase = norm(text)
        if not phrase or phrase in final_seen:
            continue
        final_seen.add(phrase)
        component = hmac.digest(nonce, phrase.encode("utf-8"), "sha256")[:16]
        full_digest = hashlib.sha256(component).hexdigest()
        result["final_candidates"].append({
            "raw_rank": raw_rank,
            "phrase": phrase,
            "component_hex": component.hex().upper(),
            "sha256": full_digest,
            "hit": full_digest == target.hex(),
        })
    hits = [candidate for candidate in result["final_candidates"] if candidate["hit"]]
    result["final_summary"] = {
        "raw_samples": len(final_generated),
        "unique_normalized": len(result["final_candidates"]),
        "target_hits": len(hits),
        "hits": hits,
        "prompt_sha256": hashlib.sha256(final_prompt.encode()).hexdigest(),
        "manifest": final_manifest,
        "evidence_exact_occurrences": exact_source_occurrences(
            args.root, norm(caption(notes[23][1]))
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "COMPLETE",
        "controls": [
            {
                "case": item["held_note"],
                "arm_a_proper_rank": item["arm_a"]["proper"]["rank"],
                "arm_b_proper_rank": item["arm_b"]["proper"]["rank"],
                "arm_a_generic_rank": item["arm_a"]["generic"]["rank"],
                "arm_b_generic_rank": item["arm_b"]["generic"]["rank"],
                "arm_b_hit_at_100": item["arm_b_candidate_stream"]["hit_at_100"],
                "arm_b_unique": item["arm_b_candidate_stream"]["unique_normalized"],
            }
            for item in result["controls"]
        ],
        "final_summary": result["final_summary"],
        "output": str(args.output),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
