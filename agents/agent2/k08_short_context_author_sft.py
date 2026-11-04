"""K08 compressed-source author voice, masked controls N02/N06 and final.
Every generated phrase tested against original HMAC16 and SHA256 commitment.
"""
import argparse
import hashlib
import hmac
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents/agent49'))
import k08_author_15b_fourholdout_sft as prior

SHA_NOTES = '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'
TARGET = '285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747'
MODEL = 'Qwen/Qwen2.5-1.5B-Instruct'
NOTES = (2, 6, 13, 20, 23)


def setup(case):
    raw = (ROOT / 'resources/evidence/crew/noticeboard-and-desk-notes.txt').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA_NOTES
    notes = prior.get_notes(raw.decode())
    keep = [(i, notes[i][1]) for i in NOTES if i != case]
    examples = '\n'.join(f'Emily N{i:02d}: {v}' for i, v in keep)
    if case == 0:
        purpose = ('Lost final handwritten keeper-envelope caption. Emily wanted '
                   'the sea outside, the night almost finished, and the voices '
                   'of tired people making room for one another at the table.')
    elif case == 2:
        purpose = 'Missing first personal crew-board watch handover caption.'
    elif case == 6:
        purpose = 'Missing second personal desk draft about the little lamp and quiet corridor.'
    else:
        raise AssertionError(case)
    prompt = (
        'These are authentic short notes by one offshore crew member.\n'
        + examples
        + '\n\nRecover a plausible missing original sentence from her same personal '
        'writing voice. Purpose: ' + purpose
        + '\nUse a plain, gentle, concrete observation of roughly 10 to 20 words. '
        'No titles, no explanation, no quotation marks. One sentence only.'
    )
    if case:
        assert prior.norm(notes[case][1]) not in prior.norm(prompt)
    route = json.loads((ROOT / 'resources/evidence/recovery-routing.json').read_text())
    accept = json.loads((ROOT / 'resources/acceptance.json').read_text())
    nonce = bytes.fromhex(route['K08']['desk_nonce'])
    assert accept['slot_sha256']['K08'].lower() == TARGET
    control = hmac.digest(nonce, prior.norm(notes[2][1]).encode(), 'sha256')[:16]
    assert control.hex().upper() == 'BF889359B0303F2B2B2FD96AE841210B'
    return notes, prompt, nonce


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--case', type=int, choices=(0, 2, 6), required=True)
    p.add_argument('--smoke', action='store_true')
    a = p.parse_args()
    notes, prompt, nonce = setup(a.case)
    print('COMPACT_SOURCE_MASK_N02_POSITIVE', a.case,
          'prompt_chars', len(prompt), flush=True)
    if a.smoke:
        return
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    torch.set_num_threads(4)
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float32, low_cpu_mem_usage=True)
    model.eval()
    messages = [
        {'role':'system', 'content':'Write exactly one understated natural crew caption sentence.'},
        {'role':'user', 'content':prompt},
    ]
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    ins = tok(text, return_tensors='pt', add_special_tokens=False)
    seed = 20261104 + a.case * 173
    torch.manual_seed(seed)
    print('GENERATE_BEGIN', a.case, flush=True)
    with torch.inference_mode():
        out = model.generate(**ins, max_new_tokens=36,
                             temperature=0.72, top_p=0.9, do_sample=True,
                             num_return_sequences=8,
                             pad_token_id=tok.eos_token_id)
    rows = []
    for j, seq in enumerate(out):
        caption = prior.one_sentence(tok.decode(
            seq[ins.input_ids.shape[1]:], skip_special_tokens=True))
        norm = prior.norm(caption)
        component = hmac.digest(nonce, norm.encode(), 'sha256')[:16]
        hit = hashlib.sha256(component).hexdigest() == TARGET
        control_hit = (a.case in (2, 6) and norm == prior.norm(notes[a.case][1]))
        row = {'case':a.case, 'model':MODEL, 'seed':seed,
               'sample':j, 'caption':caption, 'normalized':norm,
               'heldout_exact':control_hit if a.case else None,
               'original_K08_hit':hit}
        if hit:
            row['verified_component_hex'] = component.hex().upper()
        rows.append(row)
        print('CANDIDATE', json.dumps(row, ensure_ascii=False), flush=True)
    target = Path(__file__).with_name(f'k08_shortvoice_case{a.case}.jsonl')
    temp = target.with_suffix('.jsonl.tmp')
    temp.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n'
                            for x in rows), encoding='utf-8')
    os.replace(temp, target)
    print('CASE_DONE',a.case,'unique',len({x['normalized'] for x in rows}),
          'exact_controls',sum(bool(x['heldout_exact']) for x in rows),
          'K08_hits',sum(x['original_K08_hit'] for x in rows),flush=True)


if __name__ == '__main__':
    main()
