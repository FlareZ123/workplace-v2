"""Original H-17 K08 absence-matched whole-caption beam reconstruction.

Separate genuine heldout captions from exact final target. Read-only.
Historical controls: Emily N02, N06, N17, N18; final case 0.
"""
import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTES_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
ROLES = {
    2: "Emily's first draft for the crew board, a handover after a good watch",
    6: "Emily's second personal desk draft, small lamp and night corridor",
    17: "Emily's older standby-envelope label for the next watch",
    18: "Emily's older commissioning-envelope label about returning before a boat",
    0: "Emily's final keeper-envelope margin, sea outside, late night nearly finished, the voices around a table, and space for another person",
}
SELECTED = (1, 2, 6, 8, 9, 10, 11, 12, 13, 17, 18, 19, 20, 23)


def norm(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def load():
    raw = (ROOT / "resources/evidence/crew/noticeboard-and-desk-notes.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == NOTES_SHA
    rows = re.findall(r"N(\d\d) / ([^\n]+)\n([^\n]+)", raw.decode("utf-8"))
    notes = {int(n): (name.split()[0], body) for n, name, body in rows}
    assert list(notes) == list(range(1, 25))
    assert {n for n,(name,_) in notes.items() if name == "Emily"} == {2,6,10,13,17,18,20,23}
    mails = {}
    for i in (11, 12, 20):
        text = (ROOT / f"resources/evidence/mail/{i:02}.eml").read_text("utf-8")
        mails[i] = text.split("\n\n", 1)[-1]
    route = json.loads((ROOT / "resources/evidence/recovery-routing.json").read_text("utf-8"))
    acceptance = json.loads((ROOT / "resources/acceptance.json").read_text("utf-8"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"].lower()
    assert nonce.hex().upper() == "5F933DA6A1BD03C32DA5CBC25344F497"
    assert target == "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
    caption2 = notes[2][1].split(":",1)[-1].strip()
    assert hmac.digest(nonce,norm(caption2).encode(),"sha256")[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    return notes, mails, nonce, target


def build_context(notes, mails, case):
    copied = dict(mails)
    # Both old inscriptions are exact MAIL11 quotations. Remove that literal
    # duplication for genuine blinded older-label controls, preserving
    # independent mention that different historical envelopes existed.
    if case in (17,18):
        copied[11] = copied[11].replace('"Back before the first boat"', "[earlier commissioning words withheld]")
        copied[11] = copied[11].replace('"Leave the light on for the next watch."', "[earlier standby words withheld]")
    parts = []
    for index in SELECTED:
        if index == case:
            continue
        author, body = notes[index]
        parts.append(f"N{index:02} {author}: {body}")
    for index, body in copied.items():
        parts.append(f"MAIL{index:02}: {body}")
    source = "\n".join(parts)
    if case:
        expected = norm(notes[case][1].split(":",1)[-1].strip())
        assert expected not in norm(source), f"Exact historical quote leaked: N{case:02}"
    instruction = (
        "A complete earlier inscription has been removed from the export. "
        "Predict its exact original words using the surviving independent notes. "
        if case else
        "An unquoted final inscription has been lost. Predict its exact original words. "
    )
    prompt = (
        instruction
        + "Use the historical text as evidence, including its author's voice and the purpose of the inscription. "
        + "Do not explain or cite notes. Output one natural caption sentence only.\n"
        + "Target: " + ROLES[case] + "\nSurviving notes and correspondence:\n"
        + source + "\nComplete missing caption:"
    )
    if case:
        assert expected not in norm(prompt), "Exact withheld caption leaked in instructions"
    return prompt


def candidate_component(nonce, sentence):
    return hmac.digest(nonce, sentence.encode("utf-8"), "sha256")[:16]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=int, choices=(0,2,6,17,18), required=True)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--beams", type=int, default=64)
    args = parser.parse_args()
    notes,mails,nonce,target = load()
    prompt = build_context(notes,mails,args.case)
    historical = norm(notes[args.case][1].split(":",1)[-1]) if args.case else None
    print("SOURCE",json.dumps({"case":args.case,"prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest(),
        "source_chars":len(prompt),"genuine_heldout":bool(historical),"beams":args.beams}),flush=True)
    if args.smoke:
        assert 1 <= args.beams <= 256
        if historical:
            print("CONTROL",json.dumps({"case":args.case,"exact_absent_from_prompt":historical not in norm(prompt)}))
        return
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32, low_cpu_mem_usage=True)
    model.eval()
    chat = tokenizer.apply_chat_template([
        {"role":"system","content":"You restore missing short English captions. Return only the missing caption, exactly one line."},
        {"role":"user","content":prompt}
    ], tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(chat,return_tensors="pt",add_special_tokens=False)
    with torch.inference_mode():
        output = model.generate(**inputs, max_new_tokens=48, num_beams=args.beams,
            num_return_sequences=args.beams, early_stopping=True, do_sample=False,
            pad_token_id=tokenizer.eos_token_id, return_dict_in_generate=True)
    seen = set()
    rank = None
    hits = []
    for position, sequence in enumerate(output.sequences,1):
        raw = tokenizer.decode(sequence[inputs.input_ids.shape[1]:],skip_special_tokens=True)
        sentence = norm(raw.splitlines()[0].strip().strip('"')) if raw.strip() else ""
        if not (3 <= len(sentence.split()) <= 32) or sentence in seen:
            continue
        seen.add(sentence)
        match = sentence == historical if historical else False
        if match and rank is None:
            rank = position
        component = candidate_component(nonce,sentence)
        accepted = hashlib.sha256(component).hexdigest() == target
        if accepted:
            hits.append({"phrase":sentence,"component":component.hex().upper(),"position":position})
        print("CANDIDATE",json.dumps({"case":args.case,"beam_position":position,
            "text":sentence,"historical_exact":match,"original_target_match":accepted}),flush=True)
    print("RESULT",json.dumps({"case":args.case,"beams":args.beams,"unique":len(seen),
        "historical_rank":rank,"historical_hit_at_beams":rank is not None,
        "original_K08_hits":hits}),flush=True)


if __name__ == "__main__":
    main()
