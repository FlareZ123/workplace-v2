"""K08 paired lexical A/B with exact generated-caption controls.

Arm A globally withholds target word types. Arm B withholds exact target/decoy
caption copies and quoted spans while retaining independent source vocabulary.
Each arm generates 100 unique normalized captions from the proper-purpose
prompt; exact whole-caption hit rank is measured in that ordered stream.
Proper, generic and swapped-purpose log-probability ranks remain secondary
controls. The same frozen Qwen2.5-3B editor and decoding settings produce N23
candidates, which are checked against the original HMAC16/SHA256 commitment.
"""
import hashlib
import hmac

import k08_independent_lexical_ab_3b_sft as base

base.ROLE = {
    2: "First draft for the crew board.",
    6: "Second desk draft.",
    17: "Standby-envelope label.",
    18: "Commissioning-envelope label.",
}
base.WRONG_ROLE = {
    2: base.ROLE[6],
    6: base.ROLE[2],
    17: base.ROLE[18],
    18: base.ROLE[17],
}

notes, mails, nonce, target = base.load_sources()
log_path = base.ROOT / "resources/evidence/crew/galley-and-stores.log"
galley_log = log_path.read_text("utf-8").strip()
galley_sha = hashlib.sha256(log_path.read_bytes()).hexdigest()
assert galley_sha == "23dfef679a125e725654b95e7d27dffc46e7c3e9980f64b8b65fbfc2f7b75d46"

for case, role in base.ROLE.items():
    content_vocab = set(base.tokens(notes[case]["caption"])) - base.STOPWORDS
    assert not (set(base.tokens(role)) & content_vocab), (
        case, "purpose label contains held-out content vocabulary"
    )
for case, role in base.WRONG_ROLE.items():
    content_vocab = set(base.tokens(notes[case]["caption"])) - base.STOPWORDS
    assert not (set(base.tokens(role)) & content_vocab), (
        case, "swapped purpose label contains held-out content vocabulary"
    )

original_source_records = base.source_records


def source_records_with_galley_log(notes, mails, held, excluded, phrases):
    records = original_source_records(notes, mails, held, excluded, phrases)
    clean, manifest = base.sanitize_record(
        "GALLEY_LOG", "GALLEY_LOG | " + galley_log, phrases
    )
    records.append(("GALLEY_LOG", clean, manifest))
    return records


base.source_records = source_records_with_galley_log
original_final_prompt = base.final_prompt


def final_prompt_with_galley_log(notes, mails):
    prompt = original_final_prompt(notes, mails)
    phrases = [("N17", notes[17]["caption"]), ("N18", notes[18]["caption"])]
    clean, _ = base.sanitize_record(
        "GALLEY_LOG", "GALLEY_LOG | " + galley_log, phrases
    )
    marker = "\nFinal keeper-envelope caption candidate:"
    assert prompt.count(marker) == 1
    return prompt.replace(marker, "\n" + clean + marker)


base.final_prompt = final_prompt_with_galley_log

STREAM_TARGET = 100
BATCH_SIZE = 4
MAX_BATCHES = 40
MAX_NEW_TOKENS = 48


def generate_stream(model, tokenizer, torch, prompt, seed_base):
    prefix = base.chat_prefix(tokenizer, prompt)
    inputs = tokenizer(prefix, return_tensors="pt", add_special_tokens=False)
    seen = set()
    stream = []
    batches = 0
    while len(stream) < STREAM_TARGET and batches < MAX_BATCHES:
        torch.manual_seed(seed_base + batches)
        with torch.inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                num_beams=1,
                num_return_sequences=BATCH_SIZE,
                do_sample=True,
                temperature=0.8,
                top_p=0.95,
                top_k=50,
                return_dict_in_generate=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        batches += 1
        print(f"STREAM_PROGRESS seed={seed_base} batch={batches}/{MAX_BATCHES} unique={len(stream)}/{STREAM_TARGET}", flush=True)
        for sequence_index, sequence in enumerate(output.sequences):
            raw = tokenizer.decode(
                sequence[inputs.input_ids.shape[1]:], skip_special_tokens=True
            )
            phrase = base.norm(raw.splitlines()[0].strip().strip('"')) if raw.strip() else ""
            if not (3 <= len(phrase.split()) <= 32) or phrase in seen:
                continue
            seen.add(phrase)
            stream.append({
                "rank": len(stream) + 1,
                "phrase": phrase,
                "batch": batches,
                "sequence": sequence_index + 1,
            })
            print("STREAM_CANDIDATE " + json.dumps(stream[-1], ensure_ascii=False), flush=True)
            if len(stream) >= STREAM_TARGET:
                break
    return {
        "requested_unique": STREAM_TARGET,
        "unique_normalized_outputs": len(stream),
        "raw_sequences": batches * BATCH_SIZE,
        "batches": batches,
        "stream": stream,
    }


def score_decoys(model, tokenizer, torch, notes, mails, case, arm):
    expected = base.norm(notes[case]["caption"])
    candidates = [(case, expected)] + [
        (number, base.norm(phrase)) for number, phrase in base.decoys(notes, case)
    ]
    scores = {}
    for purpose in ("proper", "generic", "wrong"):
        prompt, manifest, _ = base.make_prompt(notes, mails, case, arm, purpose)
        prefix = base.chat_prefix(tokenizer, prompt)
        scored = [
            {
                "note": number,
                "score": base.score_candidate(model, tokenizer, torch, prefix, phrase),
                "candidate": phrase,
            }
            for number, phrase in candidates
        ]
        scored.sort(key=lambda item: (-item["score"], item["note"]))
        rank = next(i for i, item in enumerate(scored, 1) if item["note"] == case)
        best_decoy = max(item["score"] for item in scored if item["note"] != case)
        true = next(item for item in scored if item["note"] == case)
        scores[purpose] = {
            "decoy_rank": rank,
            "out_of": len(scored),
            "true_logprob": true["score"],
            "best_decoy_logprob": best_decoy,
            "margin": round(true["score"] - best_decoy, 6),
            "manifest": manifest,
            "scores": scored,
        }
    return scores


def run_control(model, tokenizer, torch, notes, mails, case):
    expected = base.norm(notes[case]["caption"])
    decoy_map = {
        base.norm(phrase): number for number, phrase in base.decoys(notes, case)
    }
    results = {}
    for arm_index, arm in enumerate(("A", "B")):
        prompt, manifest, _ = base.make_prompt(notes, mails, case, arm, "proper")
        stream = generate_stream(
            model, tokenizer, torch, prompt,
            20261106 + case * 1000 + arm_index * 10000
        )
        exact_rank = next(
            (item["rank"] for item in stream["stream"] if item["phrase"] == expected),
            None,
        )
        decoy_hits = [
            {"rank": item["rank"], "note": decoy_map[item["phrase"]]}
            for item in stream["stream"] if item["phrase"] in decoy_map
        ]
        results[arm] = {
            "exact_caption_rank_in_generated_stream": exact_rank,
            "hit_at_100": exact_rank is not None,
            "hit_at_10000": None,
            "hit_at_1000000": None,
            "larger_cutoffs": "not run; 100-unique stream is the predeclared feasible budget",
            "stream": stream,
            "proper_prompt_manifest": manifest,
            "decoy_stream_hits": decoy_hits,
            "purpose_scoring": score_decoys(
                model, tokenizer, torch, notes, mails, case, arm
            ),
        }
    return {
        "case": case,
        "editor": base.MODEL,
        "decoding": {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 50,
            "batch_size": BATCH_SIZE,
            "unique_target": STREAM_TARGET,
            "max_batches": MAX_BATCHES,
            "max_new_tokens": MAX_NEW_TOKENS,
            "seed_rule": "20261106 + case*1000 + arm_index*10000 + batch_index",
        },
        "arms": results,
    }


def run_final(model, tokenizer, torch, notes, mails, nonce, target, beams):
    prompt = base.final_prompt(notes, mails)
    stream = generate_stream(model, tokenizer, torch, prompt, 20261106 + 900000)
    known = {base.norm(row["caption"]): number for number, row in notes.items()}
    candidates = []
    hits = []
    for item in stream["stream"]:
        phrase = item["phrase"]
        component = hmac.digest(nonce, phrase.encode("utf-8"), "sha256")[:16]
        hit = hashlib.sha256(component).hexdigest() == target
        row = {
            **item,
            "source_exact_note": known.get(phrase),
            "component": component.hex().upper(),
            "target_match": hit,
        }
        candidates.append(row)
        if hit:
            hits.append(row)
    return {
        "editor": base.MODEL,
        "decoding": {
            "temperature": 0.8,
            "top_p": 0.95,
            "top_k": 50,
            "batch_size": BATCH_SIZE,
            "unique_target": STREAM_TARGET,
            "max_batches": MAX_BATCHES,
            "max_new_tokens": MAX_NEW_TOKENS,
            "seed_rule": "20261106 + 900000 + batch_index",
        },
        "unique_normalized_outputs": stream["unique_normalized_outputs"],
        "raw_sequences": stream["raw_sequences"],
        "original_K08_hits": hits,
        "candidates": candidates,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "prompt_chars": len(prompt),
    }


print("GALLEY_LOG_SOURCE", {
    "sha256": galley_sha,
    "chars": len(galley_log),
    "lines": len(galley_log.splitlines()),
    "purpose_labels_target_vocab_overlap": 0,
}, flush=True)
base.run_control = run_control
base.run_final = run_final
base.main()
