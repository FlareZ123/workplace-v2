"""H-17 original-source-masked, four-target author-voice generative pilot.

A source-grounded retrospective calibration and exploratory terminal K08 search.
This program does not modify any official evidence, verifier or commitment.
Use --mask-check-only without loading the external language model.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import random
import re
import tempfile
from pathlib import Path

MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
SEED = 20261104
SOURCE_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MAIL_SHA = {
    11: "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    20: "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71",
}
RESOURCES = Path(os.environ["H17_RESOURCES"]) if "H17_RESOURCES" in os.environ else Path(__file__).resolve().parents[2] / "resources"
OUT = Path(__file__).with_name("k08_author_voice_15b_candidates.jsonl")
CONTROL_IDS = (2, 6, 17, 18)
NOTE_IDS = (1, 2, 3, 4, 6, 8, 9, 10, 11, 13, 17, 18, 19, 20, 23)


def normalize(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", s.lower()).split())


def sha_pin(path: Path, expected: str) -> str:
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected, path
    return raw.decode("utf-8")


def parse_notes(text: str) -> dict[int, tuple[str, str]]:
    items: dict[int, tuple[str, str]] = {}
    lines = text.splitlines()
    for index, line in enumerate(lines[:-1]):
        m = re.fullmatch(r"N(\d{2}) / (\w+) \[censored\]", line)
        if m:
            items[int(m.group(1))] = (m.group(2), lines[index + 1].strip())
    assert list(items) == list(range(1, 25))
    return items


def authored_text(note: str) -> str:
    return note.split(": ", 1)[-1]


def mask_all_occurrences(text: str, truth: str) -> str:
    # Applies to note contents and mail quotations; exact normalized literals are
    # independently asserted absent from every generated model prompt.
    escaped = re.escape(truth.rstrip("."))
    text = re.sub(escaped + r"\.?", "[WITHHELD AUTHOR TEXT]", text, flags=re.I)
    return text


def read_evidence():
    raw = sha_pin(RESOURCES / "evidence/crew/noticeboard-and-desk-notes.txt", SOURCE_SHA)
    notes = parse_notes(raw)
    mail = {number: sha_pin(RESOURCES / f"evidence/mail/{number:02d}.eml", digest)
            for number, digest in MAIL_SHA.items()}
    route = json.loads((RESOURCES / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((RESOURCES / "acceptance.json").read_text())
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    assert hmac.digest(nonce, normalize(authored_text(notes[2][1])).encode(), "sha256")[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    return notes, mail, nonce, target


def make_context(case: str, swapped: bool, notes, mail) -> str:
    hold_id = int(case[1:]) if case.startswith("N") else None
    answers = [authored_text(notes[i][1]) for i in CONTROL_IDS]
    note_rows = []
    for i in NOTE_IDS:
        author, content = notes[i]
        if i == hold_id:
            prefix = content.split(": ", 1)[0] if ": " in content else f"N{i:02d} description"
            content = f"{prefix}: [WITHHELD AUTHOR TEXT]"
        elif case == "K08" and i in (17, 18):
            content = "Earlier envelope label: [OLDER ENVELOPE LABEL OMITTED]"
        else:
            content = mask_all_occurrences(content, answers[CONTROL_IDS.index(hold_id)]) if hold_id in CONTROL_IDS else content
        if swapped and author == "Emily":
            # Source-context control: replace Emily's writing with actual
            # comparable non-Emily caption text while retaining metadata.
            replacement_id = (1, 9, 11, 19, 8, 4)[len(note_rows) % 6]
            content = notes[replacement_id][1]
        note_rows.append(f"N{i:02d} {author}: {content}")
    selected_mail = []
    for number in (11, 20):
        body = mail[number].split("\n\n", 1)[-1]
        for answer in answers:
            body = mask_all_occurrences(body, answer)
        # Avoid surplus technical procedure details, retain the source's
        # explicit description of what a keeper phrase was meant to convey.
        if number == 11:
            body = body[body.index("Also, the final desk phrase is"):] if "Also, the final desk phrase is" in body else body
        selected_mail.append(f"MAIL{number}: {body.strip()}")
    context = "Surviving notes:\n" + "\n".join(note_rows) + "\n\nRelated preserved correspondence:\n" + "\n".join(selected_mail)
    if hold_id is not None:
        truth = normalize(authored_text(notes[hold_id][1]))
        assert truth not in normalize(context), (case, "leaked masked source")
    for i in (17,18):
        if case == "K08":
            assert normalize(authored_text(notes[i][1])) not in normalize(context)
    return context


def task_for(case: str) -> str:
    if case == "N02":
        return "Reconstruct Emily's *first crew-board draft* as one complete understated sentence. The wording of that draft is withheld."
    if case == "N06":
        return "Reconstruct Emily's *second desk draft* as one complete understated sentence. The wording of that draft is withheld."
    if case == "N17":
        return "Reconstruct Emily's *standby envelope label* as one complete short sentence. Its text is withheld."
    if case == "N18":
        return "Reconstruct Emily's *commissioning envelope label* as one complete short sentence. Its text is withheld."
    return ("Reconstruct the personal *final keeper-envelope margin* Emily wrote about the late watch. "
            "It suggests the sea outside, the end of night, the voices at a table, and crew making room for one another. "
            "The surviving draft/older envelope labels are distinct and must not be reused verbatim.")


def make_prompt(case, mode, swapped, notes, mail):
    context = make_context(case, swapped, notes, mail)
    instructions = (
        "You are reconstructing a historical offshore crew-board sentence from fragmentary original source. "
        "Write one plausible complete original inscription in Emily's understated, concrete prose voice. "
        "Answer with the sentence only. Avoid explanations and quotation marks."
        if mode == 0 else
        "You are a records copy editor recreating an absent full envelope inscription. "
        "Keep a natural, economical sentence with precise lived-in nouns and a recognizable human scene. "
        "Answer with one plausible complete sentence only."
    )
    task = task_for(case)
    prompt = context + "\n\nTASK: " + task + "\n" + instructions
    if case.startswith("N"):
        truth = normalize(authored_text(notes[int(case[1:])][1]))
        assert truth not in normalize(prompt), (case, "prompt leak")
    return prompt


def clean_generated(text: str) -> str:
    line = text.strip().split("\n")[0].strip()
    line = re.sub(r"^(?:Caption|Answer|Draft|Emily's caption)\s*:\s*", "", line, flags=re.I)
    line = re.sub(r"^\s*(?:\d+[.)]|[-*])\s*", "", line)
    line = line.strip(" \t\"'“”‘’")
    return re.split(r"(?<=[.!?])\s+", line)[0].strip(" \t\"'“”‘’")


def commit_records(records: list[dict]) -> None:
    from filelock import FileLock
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(OUT) + ".lock"):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=OUT.parent, prefix=OUT.name + ".", delete=False) as f:
            temp = Path(f.name)
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, OUT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mask-check-only", action="store_true")
    args = parser.parse_args()
    notes, mail, nonce, target = read_evidence()
    cases = ("N02", "N06", "N17", "N18", "K08")
    for case in cases:
        for mode in (0, 1):
            prompt = make_prompt(case, mode, False, notes, mail)
            print(f"MASK_OK case={case} mode={mode} chars={len(prompt)}", flush=True)
        if case != "K08":
            prompt = make_prompt(case, 0, True, notes, mail)
            print(f"SWAP_MASK_OK case={case} chars={len(prompt)}", flush=True)
    if args.mask_check_only:
        print("PASS four full literal source masks, final older-label masks, original N02 K08 HMAC control")
        return
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    random.seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16)
    model.eval()
    records: list[dict] = []
    observed: set[tuple[str, str]] = set()
    for case in cases:
        combos = [(m, False, 8 if case != "K08" else 14) for m in (0, 1)]
        if case != "K08":
            combos.append((0, True, 4))
        for mode, swapped, n in combos:
            task = make_prompt(case, mode, swapped, notes, mail)
            chat = [
                {"role": "system", "content": "Reconstruct the exact historical style when possible. Return one complete caption only."},
                {"role": "user", "content": task},
            ]
            rendered = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(rendered, return_tensors="pt")
            torch.manual_seed(SEED + 1000 * cases.index(case) + 111 * mode + int(swapped))
            with torch.inference_mode():
                sampled = model.generate(
                    **inputs,
                    do_sample=True,
                    temperature=0.72 if mode == 0 else 0.90,
                    top_p=0.92,
                    max_new_tokens=57,
                    num_return_sequences=n,
                    pad_token_id=tokenizer.eos_token_id,
                )
            for sample_id, tokens in enumerate(sampled):
                generated = tokenizer.decode(tokens[inputs.input_ids.shape[1]:], skip_special_tokens=True)
                caption = clean_generated(generated)
                normalized = normalize(caption)
                if not normalized:
                    continue
                full_key = (case + ("-swapped" if swapped else ""), normalized)
                duplicate = full_key in observed
                observed.add(full_key)
                value = hmac.digest(nonce, normalized.encode("utf-8"), "sha256")[:16]
                slot_match = hashlib.sha256(value).digest() == target
                truth = normalize(authored_text(notes[int(case[1:])][1])) if case.startswith("N") else None
                exact = normalized == truth if truth is not None else None
                item = {"case": case, "context_swapped": swapped, "mode": mode, "sample": sample_id,
                        "caption": caption, "normalized": normalized,
                        "duplicate_within_case": duplicate, "heldout_exact": exact,
                        "K08_original_match": slot_match}
                if slot_match:
                    item["K08_component"] = value.hex().upper()
                    print("K08 ORIGINAL COMMITMENT MATCH " + json.dumps(item), flush=True)
                records.append(item)
            commit_records(records)
            print(f"BATCH case={case} mode={mode} swapped={swapped} requested={n} cumulative={len(records)} "
                  f"control_exact={sum(1 for r in records if r['case']==case and r['heldout_exact'])} "
                  f"original_hits={sum(1 for r in records if r['K08_original_match'])}", flush=True)
    print("FINAL " + json.dumps({"model": MODEL, "seed": SEED, "records": len(records),
                                  "unique_by_case": len(observed),
                                  "original_hits": sum(1 for r in records if r["K08_original_match"]),
                                  "masked_exact_controls": {
                                      case: sum(1 for r in records if r['case']==case and r['heldout_exact'])
                                      for case in cases[:4]}
                                  }), flush=True)

if __name__ == "__main__":
    main()
