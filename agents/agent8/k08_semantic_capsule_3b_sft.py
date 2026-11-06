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
MODEL = "Qwen/Qwen2.5-3B-Instruct"
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
    """Create independent scene capsules without giving source prose to the decoder.

    The source-preserved single-word imagery is retained. Whole lines and
    their long quotations are absent, as they are in the actual K08 loss.
    """
    original = {
        1: ("sea", "tea", "photograph"),
        8: ("water", "daylight", "window"),
        9: ("first cup", "alone", "night", "galley"),
        10: ("desk copy", "quarterly report", "photograph", "last cup"),
        12: ("repair", "after you"),
        13: ("end of the night", "mugs", "window", "lamp"),
        20: ("sea", "end of the night", "voices at the table"),
        23: ("margin", "envelope", "words i finally put"),
    }
    for index, fragments in original.items():
        source = notes[index][1].lower()
        assert all(fragment in source for fragment in fragments), (index,fragments)
    assert "making room for each other" in mails[11].lower()
    assert "the words she finally chose matter" in mails[20].lower()
    capsules = [
        "Jason's sea photographs contrast an empty bench and the water turning lighter after dawn.",
        "Zoey's galley scenes concern a first cup, late arrivals, clean mugs and including people who were awake overnight.",
        "David and Simon focus on an ordinary next person entering a shared room, and remembering who will come after the watch.",
        "Emily preferred domestic details such as a small lamp by a window and mugs on a table.",
        "Emily wanted the final wording to encompass the sea, a night nearly over and people talking at a table.",
        "Emily wanted it to feel like making room for each other, with the water still outside.",
        "Gabriel warned that the very last wording was different from old labels and from the technical incident description.",
    ]
    # This contextualization uses genuinely independent scene information;
    # nobody has supplied the final caption or a complete copy of a heldout.
    role = ROLES[case]
    prompt = (
        "Restore a lost English inscription in the author's own simple natural language. "
        "All original complete source sentences are deliberately replaced below by short scene descriptions. "
        "These are clues, never sentences to quote. Output just one original-sounding caption. "
        "Do not write a report, a note ID, an explanation or a caption about the search.\n"
        "Historical scene capsules:\n" + "\n".join(capsules)
        + "\nMissing inscription's independently described purpose:\n" + role
        + "\nWrite the whole inscription, one sentence:"
    )
    if case:
        expected = norm(notes[case][1].split(":",1)[-1])
        assert expected not in norm(prompt), "Exact historical heldout sentence leaked"
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
