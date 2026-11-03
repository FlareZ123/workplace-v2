"""Blind, source-masked historical caption rewrite and K08 recovery pilot.

The model sees prior notes and scenario hints but never sees withheld holdout
sentences. It produces ranked complete captions before any commitment scoring.
Read-only for official records. Writes JSONL only to this agent directory.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import random
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[2] / "resources"
NOTE_PATH = ROOT / "evidence/crew/noticeboard-and-desk-notes.txt"
OUT = Path(__file__).with_name("k08_rewrite_candidates.jsonl")
SOURCE_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
SEED = 20261103

def normalize(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", value.lower()).split())

def parse_notes(text: str) -> dict[int, tuple[str, str]]:
    result = {}
    lines = text.splitlines()
    for i, line in enumerate(lines[:-1]):
        match = re.fullmatch(r"N(\d{2}) / (.+)", line)
        if match:
            note = lines[i + 1].strip()
            result[int(match.group(1))] = (match.group(2), note)
    assert len(result) == 24
    return result

def phrase_of(note: str) -> str:
    return note.split(": ", 1)[-1].strip()

def caption_output(generated: str) -> str:
    line = generated.strip().split("\n")[0].strip()
    line = re.sub(r"^\s*(?:Caption|Draft|Answer)\s*:\s*", "", line, flags=re.I)
    line = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line)
    line = line.strip(" \t\"'‘’“”")
    pieces = re.split(r"(?<=[.!?])\s+", line)
    return pieces[0].strip(" \t\"'‘’“”") if pieces else ""

def write_record(file, record: dict) -> None:
    file.write(json.dumps(record, ensure_ascii=False) + "\n")
    file.flush()

def main() -> None:
    raw = NOTE_PATH.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    notes = parse_notes(raw.decode("utf-8"))
    routing = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    nonce = bytes.fromhex(routing["K08"]["desk_nonce"])
    target_sha = bytes.fromhex(acceptance["slot_sha256"]["K08"])

    def component(phrase: str) -> bytes:
        return hmac.digest(nonce, normalize(phrase).encode("utf-8"), "sha256")[:16]

    truth = {
        "holdout_n02": normalize(phrase_of(notes[2][1])),
        "holdout_n06": normalize(phrase_of(notes[6][1])),
    }
    assert component(phrase_of(notes[2][1])).hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"

    # Holdout N02: only earlier board/photograph notes are supplied.
    # Holdout N06: N06 itself and N10/N13 are withheld; independent
    # lamp/corridor hints are derived from MAIL12, not its absent words.
    # Final K08: complete surviving material is supplied, but there is
    # no exact terminal-margin phrase anywhere in the prompt.
    contexts = {
        "holdout_n02": {
            "notes": [1, 3, 4, 5],
            "scene": "First draft of a crew board caption about a long good watch, preparing the room for other people who follow.",
            "length": "one warm 9-15 word sentence",
            "n": 12,
        },
        "holdout_n06": {
            "notes": [1, 2, 3, 4, 5, 9, 11],
            "scene": "Second desk draft about the small lamp by a corridor window, mugs from the night crew, and a quiet end to the watch.",
            "length": "one understated 8-15 word sentence",
            "n": 12,
        },
        "k08_final": {
            "notes": [1, 2, 6, 8, 9, 10, 11, 13, 19, 20, 23],
            "scene": "The final, personal keeper-envelope margin about people making room for each other after a long watch, the sea outside, fading night, voices and a table. Avoid older standby and commissioning labels.",
            "length": "one evocative original 8-22 word sentence",
            "n": 24,
        },
    }
    models = [
        "Write the most likely caption Emily would actually have penned. Return the caption alone.",
        "Imitate the author's understated, concrete crew-board voice. Write a concise full sentence; return only that sentence.",
        "Write an original short margin sentence for the given scene, everyday diction, warmth without sentimentality. Output only the final sentence.",
    ]
    torch.manual_seed(SEED)
    random.seed(SEED)
    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32)
    model.eval()

    stats = {}
    with OUT.open("w", encoding="utf-8") as output:
        for case, data in contexts.items():
            notes_text = "\n".join(
                f"N{i:02d} {notes[i][0]}: {notes[i][1]}"
                for i in data["notes"]
            )
            count = 0
            unique = set()
            best_jaccard = 0.0
            exact = []
            hit = []
            for prompt_id, instruction in enumerate(models):
                messages = [
                    {
                        "role": "system",
                        "content": "You help restore historical handwritten crew captions. You only know the surviving notes supplied. Follow requested author voice. Never explain or list choices."
                    },
                    {
                        "role": "user",
                        "content": (
                            "Surviving contextual notes:\n" + notes_text
                            + "\n\nWriting assignment: " + data["scene"]
                            + "\nLength: " + data["length"]
                            + "\n" + instruction
                        ),
                    },
                ]
                prompt = tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                inputs = tokenizer([prompt], return_tensors="pt")
                torch.manual_seed(SEED + prompt_id + 100 * list(contexts).index(case))
                with torch.inference_mode():
                    result = model.generate(
                        **inputs,
                        max_new_tokens=56,
                        do_sample=True,
                        temperature=0.88,
                        top_p=0.92,
                        num_return_sequences=data["n"],
                        pad_token_id=tokenizer.eos_token_id,
                    )
                for sample_id, tokens in enumerate(result):
                    generated = tokenizer.decode(
                        tokens[inputs.input_ids.shape[1]:], skip_special_tokens=True
                    )
                    caption = caption_output(generated)
                    norm = normalize(caption)
                    if not norm:
                        continue
                    count += 1
                    unique.add(norm)
                    exact_match = norm == truth.get(case)
                    orig_hit = hashlib.sha256(component(norm)).digest() == target_sha
                    if exact_match:
                        exact.append((prompt_id, sample_id))
                    if orig_hit:
                        hit.append({"phrase": norm, "component": component(norm).hex().upper()})
                    if case in truth:
                        a, b = set(norm.split()), set(truth[case].split())
                        best_jaccard = max(best_jaccard, len(a & b) / len(a | b))
                    write_record(output, {
                        "case": case,
                        "prompt": prompt_id,
                        "sample": sample_id,
                        "caption": caption,
                        "normalized": norm,
                        "holdout_exact": exact_match if case in truth else None,
                        "k08_hit": orig_hit,
                    })
            stats[case] = {
                "samples": count,
                "unique_normalized": len(unique),
                "holdout_exact": exact,
                "best_holdout_word_set_jaccard": round(best_jaccard, 4) if case in truth else None,
                "original_k08_hits": hit,
            }
            print("CASE_RESULT " + json.dumps({"case": case, **stats[case]}), flush=True)
    print("FINAL_RESULT " + json.dumps({
        "model": MODEL,
        "seed": SEED,
        "source_sha256": SOURCE_SHA,
        "results": stats,
    }), flush=True)

if __name__ == "__main__":
    main()
