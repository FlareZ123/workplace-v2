"""Paired K08 lexical-evidence recovery test and final candidate contact.

Arm A removes every held-out word type from context (strict lexical denial).
Arm B removes exact whole-caption/quoted-span leakage but preserves independent
word occurrences in the surviving notes and correspondence.

The same Qwen2.5-3B scorer, 11 authentic decoys, purpose controls and scoring
rule are used in both arms. Case 0 generates final keeper candidates and checks
the original HMAC16 + SHA256 commitment. Original sources remain read-only.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CREW_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MODEL = "Qwen/Qwen2.5-3B-Instruct"
CASES = (2, 6, 17, 18, 0)
NOTE_PATTERN = re.compile(r"(?m)^N(\d{2}) / ([^\n]+)\n([^\n]+)")
QUOTE_PATTERN = re.compile(r'"([^"]+)"|“([^”]+)”|‘([^’]+)’')

ROLE = {
    2: "First draft for the crew common-area board: a human handover after a watch.",
    6: "Second private desk draft: a small light and an empty night corridor.",
    17: "Older standby-envelope label intended for the upcoming watch.",
    18: "Older commissioning-envelope label about a boat and the first crossing.",
}
WRONG_ROLE = {2: ROLE[6], 6: ROLE[2], 17: ROLE[18], 18: ROLE[17]}
STOPWORDS = {
    "a", "an", "and", "as", "at", "before", "by", "for", "from", "has",
    "have", "i", "in", "is", "it", "its", "leave", "of", "on", "or",
    "the", "to", "until", "when", "with", "you",
}


def tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", value.lower())


def norm(value: str) -> str:
    return " ".join(tokens(value))


def caption(value: str) -> str:
    return value.split(":", 1)[-1].strip()


def load_sources():
    raw = (ROOT / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CREW_SHA
    rows = NOTE_PATTERN.findall(raw.decode("utf-8"))
    notes = {
        int(number): {
            "author": author.split()[0],
            "heading": author.split()[1:] if len(author.split()) > 1 else [],
            "body": body,
            "caption": caption(body),
        }
        for number, author, body in rows
    }
    assert list(notes) == list(range(1, 25))
    assert {i for i, row in notes.items() if row["author"] == "Emily"} == {
        2, 6, 10, 13, 17, 18, 20, 23
    }

    mails = {}
    for path in sorted((ROOT / "resources/evidence/mail").glob("??.eml")):
        full = path.read_text("utf-8")
        header, body = full.split("\n\n", 1)
        sender = re.search(r"(?m)^From: ([^ <]+)", header)
        date = re.search(r"(?m)^Date: (.+)$", header)
        subject = re.search(r"(?m)^Subject: (.+)$", header)
        number = int(path.stem)
        mails[number] = {
            "sender": sender.group(1) if sender else "unknown",
            "date": date.group(1) if date else "undated",
            "subject": subject.group(1) if subject else "",
            "body": body.strip(),
        }
    assert list(mails) == list(range(1, 21))

    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text("utf-8"))
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text("utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"].lower()
    assert nonce.hex().upper() == "5F933DA6A1BD03C32DA5CBC25344F497"
    assert target == "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
    fixture = norm(notes[2]["caption"])
    assert hmac.digest(nonce, fixture.encode(), "sha256")[:16].hex().upper() == (
        "BF889359B0303F2B2B2FD96AE841210B"
    )
    return notes, mails, nonce, target


def decoys(notes: dict, held: int) -> list[tuple[int, str]]:
    target_words = len(tokens(notes[held]["caption"]))
    rows = [
        (i, row["caption"])
        for i, row in notes.items()
        if i != held
    ]
    rows.sort(key=lambda item: (abs(len(tokens(item[1])) - target_words), item[0]))
    selected = rows[:11]
    assert len(selected) == 11
    assert len({norm(text) for _, text in selected}) == 11
    return selected


def phrase_regex(phrase: str):
    words = tokens(phrase)
    if not words:
        return None
    middle = r"[\W_]+".join(re.escape(word) for word in words)
    return re.compile(r"(?<![A-Za-z0-9])" + middle + r"(?![A-Za-z0-9])", re.IGNORECASE)


def is_contiguous_subsequence(candidate_tokens: list[str], quote_tokens: list[str]) -> bool:
    if len(quote_tokens) < 3 or len(quote_tokens) > len(candidate_tokens):
        return False
    width = len(quote_tokens)
    return any(candidate_tokens[i:i + width] == quote_tokens
               for i in range(len(candidate_tokens) - width + 1))


def sanitize_record(source_id: str, text: str, phrases: list[tuple[str, str]]):
    """Remove only exact target/decoy phrase copies and quoted derived spans."""
    manifest = {"source": source_id, "exact_phrase_replacements": [], "quoted_span_replacements": []}
    for phrase_id, phrase in phrases:
        pattern = phrase_regex(phrase)
        if pattern is None:
            continue
        text, count = pattern.subn("[withheld exact inscription]", text)
        if count:
            manifest["exact_phrase_replacements"].append({"phrase_id": phrase_id, "count": count})

    phrase_token_sets = [
        (phrase_id, tokens(phrase))
        for phrase_id, phrase in phrases
    ]

    def replace_quote(match):
        nonlocal manifest
        quoted = next(group for group in match.groups() if group is not None)
        quote_tokens = tokens(quoted)
        matched = [
            phrase_id for phrase_id, candidate_tokens in phrase_token_sets
            if is_contiguous_subsequence(candidate_tokens, quote_tokens)
        ]
        if matched:
            manifest["quoted_span_replacements"].append({
                "phrase_ids": matched,
                "token_count": len(quote_tokens),
            })
            return "[withheld quoted inscription span]"
        return match.group(0)

    text = QUOTE_PATTERN.sub(replace_quote, text)
    return text, manifest


def source_records(notes, mails, held: int, excluded: set[int], phrases):
    records = []
    for number, row in notes.items():
        if number in excluded or number == held:
            continue
        label = f"N{number:02d} | {row['author']} | {row['body']}"
        clean, manifest = sanitize_record(f"N{number:02d}", label, phrases)
        records.append((f"N{number:02d}", clean, manifest))
    for number, row in mails.items():
        label = (
            f"MAIL{number:02d} | From {row['sender']} | Date {row['date']} | "
            f"Subject {row['subject']} | {row['body']}"
        )
        clean, manifest = sanitize_record(f"MAIL{number:02d}", label, phrases)
        records.append((f"MAIL{number:02d}", clean, manifest))
    return records


def make_prompt(notes, mails, held: int, arm: str, purpose: str):
    held_phrase = notes[held]["caption"]
    excluded_rows = decoys(notes, held)
    excluded = {number for number, _ in excluded_rows}
    phrase_rows = [(f"N{held:02d}", held_phrase)] + [
        (f"N{number:02d}", phrase) for number, phrase in excluded_rows
    ]
    records = source_records(notes, mails, held, excluded, phrase_rows)
    source = "\n".join(text for _, text, _ in records)
    if purpose == "proper":
        role = ROLE[held]
    elif purpose == "wrong":
        role = WRONG_ROLE[held]
    else:
        role = "A historical H-17 crew inscription."

    prompt = (
        "Recover one complete original English inscription from an incomplete archive. "
        "The held-out note and eleven length-matched candidate notes are absent. "
        "Use surviving source records as evidence, preserving each author's identity, "
        "chronology, and document purpose. Do not quote or reproduce another complete "
        "surviving note. Write one complete caption only.\n"
        f"Target purpose: {role}\n"
        "Surviving original notes and correspondence:\n"
        + source
        + "\nMissing complete inscription:"
    )

    target_vocab = set(tokens(held_phrase))

    def mask_target_words(value: str) -> str:
        return re.sub(
            r"\b[A-Za-z0-9]+\b",
            lambda match: "[withheld]" if match.group().lower() in target_vocab else match.group(),
            value,
        )

    if arm == "A":
        prompt = mask_target_words(prompt)
        assert not (set(tokens(prompt)) & target_vocab), (held, "Arm A word leakage")

    independent_counts = {}
    content_counts = {}
    content_vocab = target_vocab - STOPWORDS
    for source_id, text, _ in records:
        retained_text = mask_target_words(text) if arm == "A" else text
        retained_tokens = tokens(retained_text)
        overlap = [word for word in retained_tokens if word in target_vocab]
        content_overlap = [word for word in retained_tokens if word in content_vocab]
        if overlap:
            independent_counts[source_id] = len(overlap)
        if content_overlap:
            content_counts[source_id] = len(content_overlap)

    assert norm(held_phrase) not in norm(prompt), (held, "full phrase leakage")
    manifest = {
        "case": held,
        "arm": arm,
        "purpose": purpose,
        "excluded_decoys": sorted(excluded),
        "source_records": len(records),
        "phrase_removals": [item for _, _, item in records
                            if item["exact_phrase_replacements"] or item["quoted_span_replacements"]],
        "independent_word_overlap_by_source": independent_counts,
        "independent_word_overlap_total": sum(independent_counts.values()),
        "independent_content_word_overlap_by_source": content_counts,
        "independent_content_word_overlap_total": sum(content_counts.values()),
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "prompt_chars": len(prompt),
    }
    if arm == "B":
        assert manifest["independent_word_overlap_total"] > 0, (held, manifest)
    return prompt, manifest, excluded_rows


def final_prompt(notes, mails):
    phrases = [("N17", notes[17]["caption"]), ("N18", notes[18]["caption"])]
    records = []
    for number, row in notes.items():
        if number == 17:
            label = "N17 | Emily | Older standby-envelope label; exact wording withheld and explicitly not the final keeper inscription."
        elif number == 18:
            label = "N18 | Emily | Older commissioning-envelope label; exact wording withheld and explicitly not the final keeper inscription."
        else:
            label = f"N{number:02d} | {row['author']} | {row['body']}"
        clean, _ = sanitize_record(f"N{number:02d}", label, phrases)
        records.append(clean)
    for number, row in mails.items():
        label = (
            f"MAIL{number:02d} | From {row['sender']} | Date {row['date']} | "
            f"Subject {row['subject']} | {row['body']}"
        )
        clean, _ = sanitize_record(f"MAIL{number:02d}", label, phrases)
        records.append(clean)

    custodian = (ROOT / "resources/evidence/records-custodian.txt").read_text("utf-8")
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text("utf-8"))["K08"]
    prompt = (
        "Recover the keeper's caption for Emily's recovery envelope. The custodian identifies "
        "K08 as a personal desk phrase that distinguishes this recovery envelope from the "
        "similarly named commissioning and standby envelopes; it should be rememberable rather "
        "than a cabinet number. The route identifies the target as the keeper's desk phrase and "
        "asks for the spirit of the late watch rather than the technical incident title.\n"
        "The final wording may be a direct reuse of an existing caption, a light edit, or a new "
        "line. The surviving evidence does not establish which relationship applies. Do not "
        "assume the caption is novel, and do not forbid verbatim reuse of a surviving caption. "
        "N20 gives the sea / end-of-night / voices-at-table brief and rejects the shorter standby "
        "label. N23 identifies wording in Emily's margin and the words copied onto the envelope. "
        "N17 and N18 are labels for other envelopes, not the keeper's desk phrase.\n"
        "Custodian note:\n" + custodian + "\n"
        "K08 route source and rule:\n" + route["source"] + "\n" + route["rule"] + "\n"
        "Original notes and correspondence:\n"
        + "\n".join(records)
        + "\nFinal keeper-envelope caption candidate:"
    )
    assert norm(notes[17]["caption"]) not in norm(prompt)
    assert norm(notes[18]["caption"]) not in norm(prompt)
    return prompt


def chat_prefix(tokenizer, prompt: str) -> str:
    return tokenizer.apply_chat_template(
        [
            {"role": "system", "content": "Return one complete original English caption only."},
            {"role": "user", "content": prompt},
        ],
        tokenize=False,
        add_generation_prompt=True,
    )


def score_candidate(model, tokenizer, torch, prefix: str, sentence: str) -> float:
    prefix_ids = tokenizer(prefix, return_tensors="pt", add_special_tokens=False).input_ids
    suffix_ids = tokenizer(" " + sentence, return_tensors="pt", add_special_tokens=False).input_ids
    all_ids = torch.cat((prefix_ids, suffix_ids), dim=1)
    with torch.inference_mode():
        logits = model(all_ids).logits[0, prefix_ids.shape[1] - 1:-1]
    values = torch.nn.functional.log_softmax(logits, dim=-1).gather(
        1, suffix_ids[0].unsqueeze(1)
    )
    return round((values.sum() / suffix_ids.shape[1]).item(), 6)


def candidate_component(nonce: bytes, phrase: str) -> bytes:
    return hmac.digest(nonce, phrase.encode("utf-8"), "sha256")[:16]


def run_control(model, tokenizer, torch, notes, mails, case):
    expected = norm(notes[case]["caption"])
    candidates = [(case, expected)] + [
        (number, norm(phrase)) for number, phrase in decoys(notes, case)
    ]
    results = {}
    for arm in ("A", "B"):
        for purpose in ("proper", "generic", "wrong"):
            prompt, manifest, _ = make_prompt(notes, mails, case, arm, purpose)
            prefix = chat_prefix(tokenizer, prompt)
            scored = [
                {
                    "note": number,
                    "score": score_candidate(model, tokenizer, torch, prefix, phrase),
                    "candidate": phrase,
                }
                for number, phrase in candidates
            ]
            scored.sort(key=lambda item: (-item["score"], item["note"]))
            true = next(item for item in scored if item["note"] == case)
            best_decoy = max(item["score"] for item in scored if item["note"] != case)
            rank = next(i for i, item in enumerate(scored, 1) if item["note"] == case)
            results[f"{arm}_{purpose}"] = {
                "rank": rank,
                "out_of": len(scored),
                "true_logprob": true["score"],
                "best_decoy_logprob": best_decoy,
                "margin": round(true["score"] - best_decoy, 6),
                "manifest": manifest,
                "scores": scored,
            }
    return results


def run_final(model, tokenizer, torch, notes, mails, nonce, target, beams):
    prompt = final_prompt(notes, mails)
    prefix = chat_prefix(tokenizer, prompt)
    inputs = tokenizer(prefix, return_tensors="pt", add_special_tokens=False)
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=48,
            num_beams=beams,
            num_return_sequences=beams,
            early_stopping=True,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            return_dict_in_generate=True,
        )
    seen = set()
    hits = []
    candidates = []
    known = {norm(row["caption"]): number for number, row in notes.items()}
    for position, sequence in enumerate(output.sequences, 1):
        raw = tokenizer.decode(
            sequence[inputs.input_ids.shape[1]:], skip_special_tokens=True
        )
        phrase = norm(raw.splitlines()[0].strip().strip('"')) if raw.strip() else ""
        if not (3 <= len(phrase.split()) <= 32) or phrase in seen:
            continue
        seen.add(phrase)
        component = candidate_component(nonce, phrase)
        hit = hashlib.sha256(component).hexdigest() == target
        row = {
            "position": position,
            "phrase": phrase,
            "source_exact_note": known.get(phrase),
            "component": component.hex().upper(),
            "target_match": hit,
        }
        candidates.append(row)
        if hit:
            hits.append(row)
    return {
        "beams": beams,
        "unique_complete_candidates": len(candidates),
        "original_K08_hits": hits,
        "candidates": candidates,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "prompt_chars": len(prompt),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int, choices=CASES, required=True)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--beams", type=int, default=64)
    args = parser.parse_args()

    notes, mails, nonce, target = load_sources()
    if args.case == 0:
        prompt = final_prompt(notes, mails)
        print("FINAL_SOURCE", json.dumps({
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "prompt_chars": len(prompt),
            "notes": len(notes),
            "mails": len(mails),
            "withheld_wrong_purpose_labels": [17, 18],
        }), flush=True)
        if args.smoke:
            return
    else:
        for arm in ("A", "B"):
            for purpose in ("proper", "generic", "wrong"):
                _, manifest, _ = make_prompt(notes, mails, args.case, arm, purpose)
                print("MANIFEST", json.dumps(manifest), flush=True)
        if args.smoke:
            return

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float32, low_cpu_mem_usage=True
    )
    model.eval()

    if args.case == 0:
        result = run_final(model, tokenizer, torch, notes, mails, nonce, target, args.beams)
        print("FINAL_RESULT", json.dumps(result), flush=True)
    else:
        result = run_control(model, tokenizer, torch, notes, mails, args.case)
        print("CONTROL_RESULT", json.dumps({"case": args.case, "arms": result}), flush=True)


if __name__ == "__main__":
    main()
