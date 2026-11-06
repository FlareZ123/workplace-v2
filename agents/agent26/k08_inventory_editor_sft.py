"""K08 sentence-free lexical inventory editor with blind historical controls.

Every source sentence is reduced to an alphabetized word-count inventory.
N02/N06 and their 11 length-matched decoys are genuinely withheld from each
calibration prompt. Correct, generic and swapped source-role prompts are scored.
Only if both historical controls recover at rank <=3 with correct purpose beating
both controls is a frozen 64-sample final-caption search run against K08.
"""
import argparse
import hashlib
import hmac
import json
import re
from collections import Counter
from email import policy
from email.parser import BytesParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
CASES = (2, 6)
CREW_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MAIL_HASHES = {
    1: "df0729237a3d6d5e90bcaffa95b396d54e511007ec4b0c7e5e8490280aa1d698",
    2: "a4ac849e45362b93eea9950e61132213494ab3a7cc3967e353850dc221de3a11",
    3: "3cf886c12e094cb0362999c5a4d93f913c848a64471f833fbddbfdc2d57ff889",
    4: "c9e83a610f9240c3abd4b4d435588bd9056de34edf6fa3e6d7aca88d8a21f439",
    5: "29d6d60c6addc16b6f3fd1803b582481a22ce0e757e0a1601a3dc7e116730272",
    6: "6049994562a82e46afd3f0231e136a1e6911cc3040d848e32eaa5771a6f8c2f3",
    7: "ee0830aba2e08cc862179aeca034e075f76a08914e5ee6d604ad17f4b806ac22",
    8: "2da71346103454b6743698103f4d80d79bc0b6013046646e4611c08e8d5f0937",
    9: "1bda8bbf1e7b661a04fd58c36c38f2b66d2e2410265c311cc09c8e2bf810f08c",
    10: "ccfc592fe570ca6928a74de813c378443030e841bba169434c0f413721122e48",
    11: "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29",
    12: "4cadd373aa676f97e64690a631eea3f3993e0908eaac0aacb86e76ed0c2c68fd",
    13: "80d7b086d77fe7036a596198825dd221fec82e34cbd5a5a43edae74569e171aa",
    14: "9c86de086a1727ca09b4df6f12cf5c634eaa22a3949424171cc50b4ef9983be5",
    15: "249ec45e7c21b66faf0d3310cc742ffdc70e88396a10272932ce821649b7c9e2",
    16: "02535cc5966a9215d01ecada4a14b6a403d78ca8d09310a5c3cf1a574f817a08",
    17: "67493c660dcd08de990c2490af5718072ee9e0991476c0272bf9fff9e96e8014",
    18: "7dc1f122f92ce23c110aa50fd78ae7a471bdf9e60a44e358e3b90e497f664cf0",
    19: "caff45f8c477f9fa6fc5fae0847c9c7f7842ba83c41319c8a47ddace00bd2fbd",
    20: "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71",
}
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
ROLE = {
    2: "First draft for the crew board, intended for a shared crew space.",
    6: "Second desk draft for private use.",
    0: "Final keeper-envelope desk margin: people making room after a late watch, the sea outside, night nearly finished, and voices around a table.",
}
GENERIC = "A historical H-17 crew note."
SWAPPED = {2: ROLE[6], 6: ROLE[2]}
NOTE_ROLES = {
    2: "early crew-board draft",
    6: "second private desk draft",
    10: "desk and photo-caption process note",
    13: "photo-scene recollection",
    20: "keeper-line intent note",
    23: "margin and envelope custody note",
}

def tokens(s):
    return re.findall(r"[a-z0-9]+", s.lower())

def norm(s):
    return " ".join(tokens(s))

def caption(t):
    return t.split(":", 1)[-1].strip()

def phrase_pattern(phrase):
    words = tokens(phrase)
    return r"(?<![A-Za-z0-9])" + r"[\W_]+".join(re.escape(w) for w in words) + r"(?![A-Za-z0-9])"

def load(source_root):
    evidence = Path(source_root) / "evidence"
    crew_raw = (evidence / "crew/noticeboard-and-desk-notes.txt").read_bytes()
    route_raw = (evidence / "recovery-routing.json").read_bytes()
    accept_raw = (Path(source_root) / "acceptance.json").read_bytes()
    assert hashlib.sha256(crew_raw).hexdigest() == CREW_SHA
    assert hashlib.sha256(route_raw).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(accept_raw).hexdigest() == ACCEPT_SHA
    mails = {}
    for mail_path in sorted((evidence / "mail").glob("*.eml")):
        raw = mail_path.read_bytes()
        mail_id = int(mail_path.stem)
        digest = hashlib.sha256(raw).hexdigest()
        assert digest == MAIL_HASHES[mail_id], (mail_id, digest)
        msg = BytesParser(policy=policy.default).parsebytes(raw)
        assert not msg.is_multipart() and msg.get_content_type() == "text/plain"
        mails[mail_id] = {
            "from": str(msg.get("From", "")),
            "to": str(msg.get("To", "")),
            "date": str(msg.get("Date", "")),
            "subject": str(msg.get("Subject", "")),
            "body": msg.get_content(),
        }
    assert list(mails) == list(range(1, 21))
    records = re.findall(r"N(\d\d) / ([^\n]+)\n([^\n]+)", crew_raw.decode("utf-8"))
    notes = {int(n): (a.split()[0], t) for n, a, t in records}
    assert list(notes) == list(range(1, 25))
    assert {k for k, (a, _) in notes.items() if a == "Emily"} == {2, 6, 10, 13, 17, 18, 20, 23}
    route = json.loads(route_raw)
    acceptance = json.loads(accept_raw)
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = bytes.fromhex(acceptance["slot_sha256"]["K08"])
    assert nonce.hex().upper() == "5F933DA6A1BD03C32DA5CBC25344F497"
    assert target.hex() == "285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747"
    assert hmac.digest(nonce, norm(caption(notes[2][1])).encode(), "sha256")[:16].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    return notes, mails, nonce, target

def decoys(notes, held):
    n = len(tokens(caption(notes[held][1])))
    rows = [(i, caption(t)) for i, (author, t) in notes.items() if i != held]
    rows.sort(key=lambda x: (abs(len(tokens(x[1])) - n), x[0]))
    return rows[:11]

def quote_spans(text):
    return [m.group(1) or m.group(2) for m in re.finditer(r'"([^"]+)"|“([^”]+)”', text)]

def has_shared_ngram(quote, phrase, min_words=3):
    q, p = tokens(quote), tokens(phrase)
    if not q or not p:
        return False
    qset = {tuple(q[i:i+n]) for n in range(min_words, min(len(q), len(p)) + 1) for i in range(len(q)-n+1)}
    return any(tuple(p[i:i+n]) in qset for n in range(min_words, min(len(q), len(p)) + 1) for i in range(len(p)-n+1))

def scrub_leaks(text, phrases):
    manifest = []
    for phrase_id, phrase in phrases:
        text, count = re.subn(phrase_pattern(phrase), "[withheld quotation]", text, flags=re.IGNORECASE)
        if count:
            manifest.append({"id": phrase_id, "kind": "exact_phrase", "count": count})
    def replace_quote(match):
        quoted = match.group(1) or match.group(2)
        offenders = [phrase_id for phrase_id, phrase in phrases if has_shared_ngram(quoted, phrase)]
        if offenders:
            manifest.append({"id": ",".join(map(str, offenders)), "kind": "quoted_shared_ngram", "text": quoted})
            return "[withheld quotation]"
        return match.group(0)
    return re.sub(r'"([^"]+)"|“([^”]+)”', replace_quote, text), manifest

def inventory(text):
    counts = Counter(tokens(text))
    return " ".join(f"{w}={counts[w]}" for w in sorted(counts))

def build_prompt(notes, mails, held, arm, mode, decoy_rows):
    excluded = {held, *(i for i, _ in decoy_rows)}
    phrases = [(held, caption(notes[held][1]))]
    phrases.extend((i, s) for i, s in decoy_rows)
    phrases.extend((i, caption(notes[i][1])) for i in (17, 18) if i not in {x[0] for x in phrases})
    forbidden = set(tokens(caption(notes[held][1]))) if arm == "strict" else set()
    parts, manifest = [], []
    for note_id, (author, text) in notes.items():
        if note_id in excluded:
            continue
        clean, removed = scrub_leaks(text, phrases)
        manifest.extend({"source": f"N{note_id:02d}", **x} for x in removed)
        role = NOTE_ROLES.get(note_id, "crew record")
        parts.append(f"N{note_id:02d} by {author} [{role}] word-count inventory: {inventory(clean)}")
    for mail_id, mail in mails.items():
        metadata = (
            f"From: {mail['from']}\nTo: {mail['to']}\nDate: {mail['date']}\n"
            f"Subject: {mail['subject']}"
        )
        metadata, meta_removed = scrub_leaks(metadata, phrases)
        body, body_removed = scrub_leaks(mail["body"], phrases)
        manifest.extend({"source": f"MAIL{mail_id:02d}", **x} for x in meta_removed + body_removed)
        parts.append(f"MAIL{mail_id:02d} {metadata}\nBody word-count inventory: {inventory(body)}")
    role = ROLE[held] if mode == "purpose" else GENERIC if mode == "generic" else SWAPPED[held]
    prompt = (
        "The source sentences have been removed. Each record is an alphabetized word-count inventory; "
        "word order in an inventory is not original syntax. Reconstruct the missing complete historical caption.\n"
        + "\n".join(parts)
        + "\nTarget purpose: " + role
        + "\nReturn one complete caption only:"
    )
    prompt, extra = scrub_leaks(prompt, phrases)
    manifest.extend({"source": "all", **x} for x in extra)
    if arm == "strict":
        prompt = re.sub(r"\b[A-Za-z0-9]+\b",
                        lambda m: "[withheld]" if m.group().lower() in forbidden else m.group(),
                        prompt)
    pnorm = norm(prompt)
    assert norm(caption(notes[held][1])) not in pnorm
    for note_id, (_, note_text) in notes.items():
        if note_id not in excluded:
            assert norm(caption(note_text)) not in pnorm, (held, note_id, "source sentence leaked")
    for decoy_id, text in decoy_rows:
        assert norm(text) not in pnorm
    for q in quote_spans(prompt):
        assert not any(has_shared_ngram(q, phrase) for _, phrase in phrases)
    stopwords = {"a", "an", "the", "for", "of", "to", "and", "in", "on"}
    overlap = (set(tokens(ROLE[held])) & set(tokens(caption(notes[held][1]))) - stopwords)
    assert not overlap, (held, "role leakage", overlap)
    survivors = sorted(set(tokens(caption(notes[held][1]))) & set(tokens(prompt)))
    return prompt, manifest, survivors, sorted(excluded)

def build_final_prompt(notes, mails):
    excluded = {17, 18}
    phrases = [(i, caption(notes[i][1])) for i in excluded]
    parts, manifest = [], []
    for note_id, (author, text) in notes.items():
        if note_id in excluded:
            continue
        clean, removed = scrub_leaks(text, phrases)
        manifest.extend({"source": f"N{note_id:02d}", **x} for x in removed)
        role = NOTE_ROLES.get(note_id, "crew record")
        parts.append(f"N{note_id:02d} by {author} [{role}] word-count inventory: {inventory(clean)}")
    for mail_id, mail in mails.items():
        metadata = (
            f"From: {mail['from']}\nTo: {mail['to']}\nDate: {mail['date']}\n"
            f"Subject: {mail['subject']}"
        )
        metadata, meta_removed = scrub_leaks(metadata, phrases)
        body, body_removed = scrub_leaks(mail["body"], phrases)
        manifest.extend({"source": f"MAIL{mail_id:02d}", **x} for x in meta_removed + body_removed)
        parts.append(f"MAIL{mail_id:02d} {metadata}\nBody word-count inventory: {inventory(body)}")
    prompt = (
        "Recover Emily's exact final keeper-envelope caption. The source sentences are absent; "
        "each record below is an alphabetized word-count inventory, not original word order.\n"
        + "\n".join(parts)
        + "\nEditorial purpose independently stated in MAIL11 and N20: human connection, making room, "
        "a long watch, water outside, the night nearly finished, sea, voices and a table.\n"
        "Return one complete historical caption only. Do not copy any surviving sentence:"
    )
    prompt, extra = scrub_leaks(prompt, phrases)
    manifest.extend({"source": "all", **x} for x in extra)
    pnorm = norm(prompt)
    assert "leave the light on for the next watch" not in pnorm
    assert "back before the first boat" not in pnorm
    for note_id, (_, note_text) in notes.items():
        if note_id not in excluded:
            assert norm(caption(note_text)) not in pnorm, (note_id, "source sentence leaked")
    return prompt, manifest

def chat(tokenizer, prompt):
    return tokenizer.apply_chat_template([
        {"role": "system", "content": "Return one complete crew caption only."},
        {"role": "user", "content": prompt},
    ], tokenize=False, add_generation_prompt=True)

def logprob(model, tokenizer, torch, prefix, sentence):
    ids = tokenizer(prefix, return_tensors="pt", add_special_tokens=False).input_ids
    suffix = tokenizer(" " + sentence, return_tensors="pt", add_special_tokens=False).input_ids
    all_ids = torch.cat((ids, suffix), dim=1)
    with torch.inference_mode():
        logits = model(all_ids).logits[0, ids.shape[1]-1:-1]
    score = torch.nn.functional.log_softmax(logits, dim=-1).gather(1, suffix[0].unsqueeze(1)).sum()
    return round((score / suffix.shape[1]).item(), 6)

def run_model(notes, mails, nonce, target):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32, low_cpu_mem_usage=True)
    model.eval()
    ranks = {}
    for case in CASES:
        rows = decoys(notes, case)
        candidates = [(case, norm(caption(notes[case][1])))] + [(i, norm(s)) for i, s in rows]
        case_result = {"case": case, "decoys": [i for i, _ in rows], "conditions": {}}
        for arm in ("strict", "shared"):
            for mode in ("purpose", "generic", "swapped"):
                prompt, manifest, survivors, excluded = build_prompt(notes, mails, case, arm, mode, rows)
                prefix = chat(tokenizer, prompt)
                scores = [{"note": i, "score": logprob(model, tokenizer, torch, prefix, sentence)}
                          for i, sentence in candidates]
                scores.sort(key=lambda x: -x["score"])
                rank = next(i for i, x in enumerate(scores, 1) if x["note"] == case)
                case_result["conditions"][f"{arm}_{mode}"] = {
                    "rank": rank, "out_of": 12, "scores": scores,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "retained_target_words": survivors, "quote_scrub_manifest": manifest,
                    "excluded_note_ids": excluded,
                }
        ranks[case] = case_result
        print("INVENTORY_RANK", json.dumps(case_result, ensure_ascii=False), flush=True)
    passed = all(
        ranks[c]["conditions"]["shared_purpose"]["rank"] <= 3
        and ranks[c]["conditions"]["shared_purpose"]["rank"] < ranks[c]["conditions"]["shared_generic"]["rank"]
        and ranks[c]["conditions"]["shared_purpose"]["rank"] < ranks[c]["conditions"]["shared_swapped"]["rank"]
        for c in CASES
    )
    if not passed:
        print("FINAL_GENERATION_SKIPPED", json.dumps({"reason":"both blind historical controls did not pass the predeclared gate"}), flush=True)
        return ranks, []
    final_prompt, final_manifest = build_final_prompt(notes, mails)
    inputs = tokenizer(chat(tokenizer, final_prompt), return_tensors="pt", add_special_tokens=False)
    seen, outputs, hits = set(), [], []
    for j in range(64):
        torch.manual_seed(20261107 + j)
        with torch.inference_mode():
            out = model.generate(**inputs, max_new_tokens=48, do_sample=True,
                temperature=0.8, top_p=0.95, pad_token_id=tokenizer.eos_token_id)
        raw = tokenizer.decode(out[0, inputs.input_ids.shape[1]:], skip_special_tokens=True).splitlines()[0]
        phrase = norm(raw)
        if not phrase or phrase in seen:
            continue
        seen.add(phrase)
        component = hmac.digest(nonce, phrase.encode("utf-8"), "sha256")[:16]
        hit = hashlib.sha256(component).digest() == target
        row = {"sample":j+1,"phrase":phrase,"hmac16":component.hex().upper(),"hit":hit}
        outputs.append(row)
        if hit:
            hits.append(row)
    print("INVENTORY_FINAL", json.dumps({
        "unique":len(seen),"hits":hits,"candidates":outputs,
        "final_prompt_sha256":hashlib.sha256(final_prompt.encode()).hexdigest(),
        "quote_scrub_manifest":final_manifest
    }, ensure_ascii=False), flush=True)
    return ranks, outputs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", default=str(ROOT / "resources"))
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    notes, mails, nonce, target = load(Path(args.source_root))
    controls = []
    for case in CASES:
        rows = decoys(notes, case)
        assert len(rows) == 11
        for arm in ("strict", "shared"):
            for mode in ("purpose", "generic", "swapped"):
                prompt, manifest, survivors, excluded = build_prompt(notes, mails, case, arm, mode, rows)
                controls.append({
                    "case":case,"arm":arm,"mode":mode,
                    "prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest(),
                    "retained_target_words":survivors,"excluded_note_ids":excluded,
                    "inventory_word_count":len(tokens(prompt)),"quote_scrub_manifest":manifest
                })
    final_prompt, final_manifest = build_final_prompt(notes, mails)
    print("INVENTORY_SOURCE_CONTROLS", json.dumps({
        "crew_sha256":CREW_SHA,"mail_sha256":MAIL_HASHES,
        "route_sha256":ROUTE_SHA,"acceptance_sha256":ACCEPT_SHA,
        "controls":controls,"final_prompt_sha256":hashlib.sha256(final_prompt.encode()).hexdigest(),
        "final_quote_scrub_manifest":final_manifest
    }, ensure_ascii=False), flush=True)
    if args.smoke:
        return
    if not args.run:
        parser.error("choose --smoke or --run")
    run_model(notes, mails, nonce, target)

if __name__ == "__main__":
    main()
