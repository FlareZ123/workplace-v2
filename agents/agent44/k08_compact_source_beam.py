#!/usr/bin/env python3
"""Generate a small, role-specific K08 candidate set and test the exact commitment."""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

MODEL = "Qwen/Qwen2.5-3B-Instruct"
NOTE_RE = re.compile(r"(?m)^N(\d{2}) / ([^\n]+)\n([^\n]+)")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def note_caption(value: str) -> str:
    return value.split(":", 1)[-1].strip()


def email_paragraphs(path: Path) -> list[str]:
    raw = path.read_bytes()
    header = re.search(rb"\r?\n\r?\n", raw)
    if not header:
        raise ValueError(f"Missing email header separator: {path}")
    body = raw[header.end():]
    return [part.decode("utf-8").strip() for part in
            re.split(rb"\r?\n[ \t]*\r?\n", body) if part.strip()]


def load_inputs(resources: Path, acceptance_path: Path) -> dict[str, Any]:
    evidence = resources / "evidence"
    notes_path = evidence / "crew" / "noticeboard-and-desk-notes.txt"
    notes_raw = notes_path.read_bytes()
    rows = NOTE_RE.findall(notes_raw.decode("utf-8"))
    notes = {int(number): {"author": author.split()[0], "body": body}
             for number, author, body in rows}
    if set(notes) != set(range(1, 25)):
        raise ValueError("Expected exactly N01 through N24")

    mail11_path = evidence / "mail" / "11.eml"
    mail14_path = evidence / "mail" / "14.eml"
    mail20_path = evidence / "mail" / "20.eml"
    mail11 = email_paragraphs(mail11_path)
    mail14 = email_paragraphs(mail14_path)
    mail20 = email_paragraphs(mail20_path)
    if len(mail11) < 3 or len(mail14) < 3 or len(mail20) < 3:
        raise ValueError("Expected the source paragraphs used by the K08 role map")

    route_path = evidence / "recovery-routing.json"
    route = json.loads(route_path.read_text("utf-8"))["K08"]
    acceptance = json.loads(acceptance_path.read_text("utf-8"))
    nonce = bytes.fromhex(route["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"].lower()

    custodian_path = evidence / "records-custodian.txt"
    custodian_lines = custodian_path.read_text("utf-8").splitlines()
    custodian_start = next(i for i, line in enumerate(custodian_lines)
                           if line.startswith("The archive supplier's commissioning note"))
    custodian_context = "\n".join(custodian_lines[custodian_start:custodian_start + 5])
    mail11_intent = mail11[2]
    mail11_intent = mail11_intent.replace('"Back before the first boat"', '[withheld old commissioning label]')
    mail11_intent = mail11_intent.replace('"Leave the light on for the next watch."', '[withheld old standby label].')

    known_note_phrases = {normalize(note_caption(row["body"])): number
                          for number, row in notes.items()}
    sources = {
        "MAIL11_p3_intent": mail11_intent,
        "MAIL14_p3_folder_context": mail14[2],
        "MAIL20_p2_exact_words": mail20[1],
        "MAIL20_p3_bundle_context": mail20[2],
        "N02_author_draft": notes[2]["body"],
        "N06_author_draft": notes[6]["body"],
        "N10_photo_reference": notes[10]["body"],
        "N13_author_reminiscence": notes[13]["body"],
        "N20_semantic_brief": notes[20]["body"],
        "N23_final_carrier_locator": notes[23]["body"],
        "photo_captions": {f"N{n:02d}": notes[n]["body"] for n in (1, 3, 4, 8, 14)},
        "galley_caption": notes[9]["body"],
        "custodian_K08_context": custodian_context,
        "route_source": route["source"],
        "excluded_old_labels": "N17 and N18 are older labels for other envelopes, not K08. Their exact wording is intentionally withheld.",
    }
    prompt = (
        "Recover one complete original English keeper caption for the H-17 recovery envelope. "
        "The caption is Emily's personal wording used to distinguish this envelope from similarly "
        "named commissioning and standby envelopes. The final words were written on the envelope "
        "margin. The exact wording is not quoted in the surviving author-intent note.\n\n"
        "Source roles and evidence:\n"
        + "\n".join(f"[{key}] {value}" for key, value in sources.items())
        + "\n\n"
        "The author wanted a line about people making room for one another after a long watch, "
        "with water outside and the night almost finished. N20 describes the intended anchors as "
        "the sea, the end of the night, and voices at the table. The final caption may reuse, "
        "lightly edit, or newly phrase the surviving source language. Do not assume novelty. "
        "Use Emily's own drafts and reminiscence as style references. Do not impose a novelty "
        "constraint. Return one complete caption only, "
        "with no explanation or quotation marks."
    )
    if "issue receipt for revision C of RC-17" in prompt:
        raise ValueError("K06 paragraph leaked into the K08 prompt")
    if "Back before the first boat" in prompt or "Leave the light on for the next watch" in prompt:
        raise ValueError("An excluded old label leaked into the K08 prompt")
    if "people making room for each other after" not in prompt or "voices at the table" not in prompt:
        raise ValueError("K08 intent anchors are missing from the prompt")

    hashes = {
        str(path.relative_to(resources)): sha256(path.read_bytes())
        for path in (notes_path, mail11_path, mail14_path, mail20_path,
                     route_path, custodian_path)
    }
    hashes["acceptance.json"] = sha256(acceptance_path.read_bytes())
    return {"prompt": prompt, "nonce": nonce, "target": target,
            "normalization_rule": route["rule"],
            "source_hashes": hashes, "source_roles": list(sources), "sources": sources,
            "prompt_sha256": sha256(prompt.encode("utf-8")),
            "prompt_chars": len(prompt), "known_note_phrases": known_note_phrases}


def save_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     delete=False, newline="\n") as temp:
        temp.write(encoded)
        temp_path = Path(temp.name)
    os.replace(temp_path, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resources", type=Path,
                        default=Path(__file__).resolve().parents[2] / "resources")
    parser.add_argument("--acceptance", type=Path)
    parser.add_argument("--output", type=Path, default=Path("k08-compact-source-beam.json"))
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--beams", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=32)
    parser.add_argument("--max-time", type=float, default=480.0)
    args = parser.parse_args()
    acceptance_path = args.acceptance or (args.resources / "acceptance.json")
    data = load_inputs(args.resources, acceptance_path)
    if args.smoke:
        print(json.dumps({k: data[k] for k in ("prompt_sha256", "prompt_chars", "source_roles",
                                                  "normalization_rule", "target", "source_hashes")}, indent=2))
        return

    import platform
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_num_threads(2)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=torch.float32, low_cpu_mem_usage=True
    )
    model.eval()
    messages = [
        {"role": "system", "content": "Return one complete keeper caption candidate only. It may reuse or edit source wording."},
        {"role": "user", "content": data["prompt"]},
    ]
    formatted = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(formatted, return_tensors="pt", add_special_tokens=False)
    with torch.inference_mode():
        generated = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            max_time=args.max_time,
            num_beams=args.beams,
            num_return_sequences=args.beams,
            early_stopping=True,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            return_dict_in_generate=True,
            output_scores=True,
        )

    known = {
        normalize(note_caption(data["sources"]["N02_author_draft"])): 2,
        normalize(note_caption(data["sources"]["N06_author_draft"])): 6,
        normalize(note_caption(data["sources"]["N13_author_reminiscence"])): 13,
    }
    candidates = []
    seen = set()
    sequence_scores = getattr(generated, "sequences_scores", None)
    for i, sequence in enumerate(generated.sequences):
        raw = tokenizer.decode(sequence[inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        first_line = next((line.strip() for line in raw.splitlines() if line.strip()), "")
        first_line = re.sub(r"^(caption|candidate)\s*:\s*", "", first_line, flags=re.IGNORECASE)
        phrase = normalize(first_line.strip().strip('"“”‘’'))
        if not (1 <= len(phrase.split()) <= 32) or phrase in seen:
            continue
        seen.add(phrase)
        component = hmac.digest(data["nonce"], phrase.encode("utf-8"), "sha256")[:16]
        component_sha = sha256(component)
        candidates.append({
            "rank": i + 1,
            "beam_score": float(sequence_scores[i].item()) if sequence_scores is not None else None,
            "raw_output": first_line,
            "phrase_normalized": phrase,
            "source_exact_note": data["known_note_phrases"].get(phrase),
            "component_hex": component.hex().upper(),
            "component_sha256": component_sha,
            "target_match": component_sha == data["target"],
        })

    result = {
        "model": MODEL,
        "model_revision_requested": "main",
        "model_revision_resolved": getattr(model.config, "_commit_hash", None),
        "runtime": {"python": platform.python_version(), "torch": torch.__version__,
                    "transformers": transformers.__version__, "torch_threads": torch.get_num_threads()},
        "generation": {"strategy": "deterministic_beam_search", "num_beams": args.beams,
                       "num_return_sequences": args.beams, "do_sample": False,
                       "max_new_tokens": args.max_new_tokens, "max_time_seconds": args.max_time},
        "prompt_sha256": data["prompt_sha256"],
        "prompt_chars": data["prompt_chars"],
        "source_roles": data["source_roles"],
        "normalization_rule": data["normalization_rule"],
        "target_sha256": data["target"],
        "prompt_tokens": int(inputs["input_ids"].shape[1]),
        "source_hashes": data["source_hashes"],
        "candidate_count": len(candidates),
        "target_hits": [c for c in candidates if c["target_match"]],
        "candidates": candidates,
    }
    save_atomic(args.output, result)
    print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()