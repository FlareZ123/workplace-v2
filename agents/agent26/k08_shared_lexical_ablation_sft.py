"""K08 paired missing-line recovery test with quote-only vs global lexical masking.

Uses authentic held-out Emily captions N02/N06, identical 11 source-note decoys,
and one frozen Qwen2.5-3B-Instruct scorer. Arm A removes every target word type;
Arm B removes only the held-out note and exact/quoted target or decoy passages,
retaining independently authored word recurrences. A small final-caption sample
is generated once from the source-rich keeper prompt and checked against the
untouched original K08 HMAC/SHA commitment.
"""
import argparse
import hashlib
import hmac
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = "Qwen/Qwen2.5-3B-Instruct"
CASES = (2, 6)
CREW_SHA = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
MAIL11_SHA = "f4e1b8440582d494fa098d4726d9ad7995d24b7f48f8dc6336364b0c8cf51d29"
MAIL20_SHA = "e83391f77c3a41b97cf92c78d93abfa0bebeed0ddf7cbcb9309250973963ac71"
ROUTE_SHA = "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5"
ACCEPT_SHA = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
ROLE = {
    2: "First draft for a crew common-area board: human handover after a watch.",
    6: "Second private desk draft: a small light and an empty night corridor.",
    0: "Final keeper-envelope desk margin: people making room after a late watch, the sea outside, night nearly finished, and voices around a table.",
}
GENERIC = "A historical H-17 crew note."
SWAPPED = {2: ROLE[6], 6: ROLE[2]}

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
    mail11_raw = (evidence / "mail/11.eml").read_bytes()
    mail20_raw = (evidence / "mail/20.eml").read_bytes()
    route_raw = (evidence / "recovery-routing.json").read_bytes()
    accept_raw = (Path(source_root) / "acceptance.json").read_bytes()
    assert hashlib.sha256(crew_raw).hexdigest() == CREW_SHA
    assert hashlib.sha256(mail11_raw).hexdigest() == MAIL11_SHA
    assert hashlib.sha256(mail20_raw).hexdigest() == MAIL20_SHA
    assert hashlib.sha256(route_raw).hexdigest() == ROUTE_SHA
    assert hashlib.sha256(accept_raw).hexdigest() == ACCEPT_SHA
    records = re.findall(r"N(\d\d) / ([^\n]+)\n([^\n]+)", crew_raw.decode("utf-8"))
    notes = {int(n): (a.split()[0], t) for n, a, t in records}
    assert list(notes) == list(range(1, 25))
    assert {k for k, (a, _) in notes.items() if a == "Emily"} == {2, 6, 10, 13, 17, 18, 20, 23}
    mails = {
        11: mail11_raw.decode("utf-8").split("\n\n", 1)[-1],
        20: mail20_raw.decode("utf-8").split("\n\n", 1)[-1],
    }
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
    q = tokens(quote)
    p = tokens(phrase)
    if not q or not p:
        return False
    qset = {tuple(q[i:i+n]) for n in range(min_words, min(len(q), len(p)) + 1) for i in range(len(q)-n+1)}
    return any(tuple(p[i:i+n]) in qset for n in range(min_words, min(len(q), len(p)) + 1) for i in range(len(p)-n+1))

def scrub_leaks(text, phrases):
    """Remove exact full phrases and quoted fragments; retain unquoted independent words."""
    manifest = []
    for phrase_id, phrase in phrases:
        pattern = phrase_pattern(phrase)
        text, count = re.subn(pattern, "[withheld quotation]", text, flags=re.IGNORECASE)
        if count:
            manifest.append({"id": phrase_id, "kind": "exact_phrase", "count": count})
    def replace_quote(match):
        quoted = match.group(1) or match.group(2)
        offenders = [phrase_id for phrase_id, phrase in phrases if has_shared_ngram(quoted, phrase)]
        if offenders:
            manifest.append({"id": ",".join(map(str, offenders)), "kind": "quoted_shared_ngram", "text": quoted})
            return "[withheld quotation]"
        return match.group(0)
    text = re.sub(r'"([^"]+)"|“([^”]+)”', replace_quote, text)
    return text, manifest

def independent_word_sources(notes, mails, held, decoy_rows, phrases):
    excluded = {held, *(i for i, _ in decoy_rows)}
    source_tokens = {}
    for note_id, (author, text) in notes.items():
        if note_id in excluded:
            continue
        clean, _ = scrub_leaks(text, phrases)
        source_tokens[f"N{note_id:02d}"] = set(tokens(clean))
    for mail_id, body in mails.items():
        clean, _ = scrub_leaks(body, phrases)
        source_tokens[f"MAIL{mail_id:02d}"] = set(tokens(clean))
    target_words = set(tokens(caption(notes[held][1])))
    return {
        word: [source_id for source_id, words in source_tokens.items() if word in words]
        for word in sorted(target_words)
        if len(word) >= 3 and any(word in words for words in source_tokens.values())
    }

def build_prompt(notes, mails, held, arm, mode, decoy_rows):
    excluded = {held, *(i for i, _ in decoy_rows)}
    phrases = [(held, caption(notes[held][1]))]
    phrases.extend((i, s) for i, s in decoy_rows)
    # The two old-envelope labels are explicit competing quotations in MAIL11.
    # Scrub their quoted forms without removing their independent note records.
    phrases.extend((i, caption(notes[i][1])) for i in (17, 18) if i not in {x[0] for x in phrases})
    parts = [f"N{i:02d} by {author}: {text}" for i, (author, text) in notes.items() if i not in excluded]
    clean_mails = []
    manifest = []
    for mail_id, body in mails.items():
        clean, removed = scrub_leaks(body, phrases)
        clean_mails.append(f"MAIL{mail_id:02d}: {clean}")
        manifest.extend({"mail": mail_id, **item} for item in removed)
    parts.extend(clean_mails)
    if mode == "purpose":
        role = ROLE[held]
    elif mode == "generic":
        role = GENERIC
    elif mode == "swapped":
        role = SWAPPED[held]
    else:
        raise ValueError(mode)
    prompt = (
        "Predict one missing original caption by Emily using the incomplete record.\n"
        "Historical excerpts:\n" + "\n".join(parts) +
        "\nTarget purpose: " + role +
        "\nRespond with one complete original caption only:"
    )
    prompt, full_context_manifest = scrub_leaks(prompt, phrases)
    manifest.extend({"context": "all", **item} for item in full_context_manifest)
    if arm == "strict":
        forbidden = set(tokens(caption(notes[held][1])))
        prompt = re.sub(r"\b[A-Za-z0-9]+\b",
                        lambda m: "[withheld]" if m.group().lower() in forbidden else m.group(),
                        prompt)
    elif arm != "shared":
        raise ValueError(arm)
    target_norm = norm(caption(notes[held][1]))
    prompt_norm = norm(prompt)
    assert target_norm not in prompt_norm, (held, arm, mode, "full target phrase leaked")
    for decoy_id, decoy_text in decoy_rows:
        assert norm(decoy_text) not in prompt_norm, (held, arm, mode, decoy_id, "full decoy phrase leaked")
    # Explicit quote spans must not contain a 3+ word run from any withheld output.
    for q in quote_spans(prompt):
        assert not any(has_shared_ngram(q, phrase) for _, phrase in phrases), (held, arm, mode, q)
    survivors = sorted(set(tokens(caption(notes[held][1]))) & set(tokens(prompt)))
    provenance = independent_word_sources(notes, mails, held, decoy_rows, phrases)
    return prompt, manifest, survivors, sorted(excluded), provenance

def build_final_prompt(notes, mails):
    # Competing older envelope labels are removed; independent Emily drafts,
    # scene notes, photo captions, and legitimate shared words remain.
    excluded = {17, 18}
    phrases = [(i, caption(notes[i][1])) for i in excluded]
    parts = [f"N{i:02d} by {author}: {text}" for i, (author, text) in notes.items() if i not in excluded]
    manifest = []
    for mail_id, body in mails.items():
        clean, removed = scrub_leaks(body, phrases)
        parts.append(f"MAIL{mail_id:02d}: {clean}")
        manifest.extend({"mail": mail_id, **item} for item in removed)
    prompt = (
        "Recover Emily's exact final keeper-envelope caption from the surviving archive.\n"
        "Historical excerpts:\n" + "\n".join(parts) +
        "\nTarget purpose: " + ROLE[0] +
        "\nReturn one complete caption only. Preserve the original author's wording; do not explain:"
    )
    prompt, full_context_manifest = scrub_leaks(prompt, phrases)
    manifest.extend({"context": "all", **item} for item in full_context_manifest)
    assert "leave the light on for the next watch" not in norm(prompt)
    assert "back before the first boat" not in norm(prompt)
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

def run_model(args, notes, mails, nonce, target):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32, low_cpu_mem_usage=True)
    model.eval()
    all_results = []
    for case in CASES:
        rows = decoys(notes, case)
        candidates = [(case, norm(caption(notes[case][1])))] + [(i, norm(s)) for i, s in rows]
        for arm in ("strict", "shared"):
            arm_result = {"case": case, "arm": arm, "decoys": [i for i, _ in rows], "conditions": {}}
            for mode in ("purpose", "generic", "swapped"):
                prompt, manifest, survivors, excluded, provenance = build_prompt(notes, mails, case, arm, mode, rows)
                prefix = chat(tokenizer, prompt)
                scores = [{"note": i, "score": logprob(model, tokenizer, torch, prefix, sentence)}
                          for i, sentence in candidates]
                scores.sort(key=lambda x: -x["score"])
                rank = next(i for i, x in enumerate(scores, 1) if x["note"] == case)
                arm_result["conditions"][mode] = {
                    "rank": rank, "out_of": len(scores), "scores": scores,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "independent_target_words_retained": survivors,
                    "independent_word_sources": provenance,
                    "quote_scrub_manifest": manifest,
                    "excluded_note_ids": excluded,
                }
            print("PAIRED_RANK", json.dumps(arm_result, ensure_ascii=False), flush=True)
            all_results.append(arm_result)
    # Source-rich final candidate generation is a single frozen, small target-contact run.
    final_prompt, final_manifest = build_final_prompt(notes, mails)
    inputs = tokenizer(chat(tokenizer, final_prompt), return_tensors="pt", add_special_tokens=False)
    seen = set()
    hits = []
    outputs = []
    for j in range(64):
        torch.manual_seed(20261106 + j)
        with torch.inference_mode():
            out = model.generate(**inputs, max_new_tokens=48, do_sample=True,
                temperature=0.8, top_p=0.9, pad_token_id=tokenizer.eos_token_id)
        raw = tokenizer.decode(out[0, inputs.input_ids.shape[1]:], skip_special_tokens=True).splitlines()[0]
        phrase = norm(raw)
        if not phrase or phrase in seen:
            continue
        seen.add(phrase)
        component = hmac.digest(nonce, phrase.encode("utf-8"), "sha256")[:16]
        good = hashlib.sha256(component).digest() == target
        row = {"sample": j + 1, "phrase": phrase, "hmac16": component.hex().upper(), "hit": good}
        outputs.append(row)
        if good:
            hits.append(row)
    print("FINAL_GENERATION", json.dumps({
        "samples": 64, "unique_normalized": len(seen), "target_hits": hits,
        "candidates": outputs, "quote_scrub_manifest": final_manifest,
        "prompt_sha256": hashlib.sha256(final_prompt.encode()).hexdigest()
    }, ensure_ascii=False), flush=True)
    return all_results, outputs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", default=str(ROOT / "resources"))
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    source_root = Path(args.source_root)
    notes, mails, nonce, target = load(source_root)
    manifests = []
    for case in CASES:
        rows = decoys(notes, case)
        for arm in ("strict", "shared"):
            for mode in ("purpose", "generic", "swapped"):
                prompt, manifest, survivors, excluded, provenance = build_prompt(notes, mails, case, arm, mode, rows)
                assert len(rows) == 11
                manifests.append({
                    "case": case, "arm": arm, "mode": mode,
                    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                    "excluded_note_ids": excluded,
                    "independent_target_words_retained": survivors,
                    "independent_word_sources": provenance,
                    "quote_scrub_manifest": manifest,
                })
    final_prompt, final_manifest = build_final_prompt(notes, mails)
    print("SOURCE_CONTROLS", json.dumps({
        "crew_sha256": CREW_SHA, "mail11_sha256": MAIL11_SHA, "mail20_sha256": MAIL20_SHA,
        "route_sha256": ROUTE_SHA, "acceptance_sha256": ACCEPT_SHA,
        "cases": manifests, "final_prompt_sha256": hashlib.sha256(final_prompt.encode()).hexdigest(),
        "final_quote_scrub_manifest": final_manifest,
    }, ensure_ascii=False), flush=True)
    if args.smoke:
        return
    if not args.run:
        parser.error("choose --smoke or --run")
    run_model(args, notes, mails, nonce, target)

if __name__ == "__main__":
    main()
