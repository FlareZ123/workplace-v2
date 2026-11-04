"""K08 final-keeper source-masked Qwen1.5B, one prompt per short CI job.
Three independent final caption prompts. Never embeds K08 original phrase (unknown).
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

MODEL = 'Qwen/Qwen2.5-1.5B-Instruct'
SHA_NOTES = '13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb'


def build():
    resources = ROOT / 'resources'
    raw = (resources / 'evidence/crew/noticeboard-and-desk-notes.txt').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA_NOTES
    notes = prior.get_notes(raw.decode('utf-8'))
    mails = [(resources / f'evidence/mail/{i:02d}.eml').read_text()
             for i in range(1, 21)]
    material, author = prior.context(notes, mails, 0, False)
    assert author == 'Emily'
    existing = prior.prompts(0, author, material)
    extra = (
        f'Surviving H-17 original crew extracts:\n{material}\n\n'
        'The missing final envelope sentence was handwritten by Emily. '
        'Her authentic crew-board drafts have an understated personal cadence. '
        'N20 says she wanted the sea, the end of the night and the voices at '
        'the table; MAIL11 says people making room for one another. '
        'Write one complete original final keeper-envelope caption in her '
        'voice, using everyday imagery. Do not use either rejected old '
        'standby or commissioning label. Output the sentence alone.'
    )
    assert len(existing) == 2
    route = json.loads((resources / 'evidence/recovery-routing.json').read_text())
    acceptance = json.loads((resources / 'acceptance.json').read_text())
    nonce = bytes.fromhex(route['K08']['desk_nonce'])
    digest = bytes.fromhex(acceptance['slot_sha256']['K08'])
    assert nonce.hex().upper() == '5F933DA6A1BD03C32DA5CBC25344F497'
    assert digest.hex() == '285eb6b4196d21eaf47e251449e61e0bce28749881ccc5a065ca733b0c3fd747'
    assert hmac.digest(nonce, prior.norm(notes[2][1]).encode(), 'sha256')[:16].hex().upper() == 'BF889359B0303F2B2B2FD96AE841210B'
    return existing + [extra], nonce, digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt-id', type=int, choices=(0, 1, 2), required=True)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    prompts, nonce, wanted = build()
    print('ORIGINAL_SOURCE_N02_REDUCER_AND_K08_TARGET_PASS',
          'prompt', args.prompt_id, 'chars', len(prompts[args.prompt_id]), flush=True)
    if args.smoke:
        return
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(4)
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float32, low_cpu_mem_usage=True)
    model.eval()
    messages = [
        {'role': 'system', 'content': 'Recover a missing handwritten archival caption. Reply with one complete sentence only.'},
        {'role': 'user', 'content': prompts[args.prompt_id]}
    ]
    chat = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    ins = tok(chat, return_tensors='pt', add_special_tokens=False)
    seed = 20261104 + 80000 + 100 * args.prompt_id
    torch.manual_seed(seed)
    print('GENERATE_BEGIN', args.prompt_id, 'seed', seed, flush=True)
    with torch.inference_mode():
        outs = model.generate(**ins, max_new_tokens=44, do_sample=True,
                              temperature=0.85, top_p=0.93,
                              num_return_sequences=4,
                              pad_token_id=tok.eos_token_id)
    rows = []
    for i, sequence in enumerate(outs):
        decoded = tok.decode(sequence[ins.input_ids.shape[1]:], skip_special_tokens=True)
        caption = prior.one_sentence(decoded)
        normalized = prior.norm(caption)
        component = hmac.digest(nonce, normalized.encode(), 'sha256')[:16]
        match = hashlib.sha256(component).digest() == wanted
        row = {
            'case': 'K08_final', 'prompt_id': args.prompt_id,
            'model': MODEL, 'seed': seed, 'sample': i,
            'caption': caption, 'normalized': normalized,
            'component_hex': component.hex().upper() if match else None,
            'original_k08_match': match,
        }
        rows.append(row)
        print('CANDIDATE', json.dumps(row, ensure_ascii=False), flush=True)
    path = Path(__file__).with_name(f'k08_qwen_final_p{args.prompt_id}.jsonl')
    data = ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows)
    temp = path.with_suffix('.jsonl.tmp')
    temp.write_text(data, encoding='utf-8')
    os.replace(temp, path)
    print('CASE_COMPLETED', args.prompt_id, 'generated', len(rows),
          'unique', len({r['normalized'] for r in rows}),
          'original_hits', sum(r['original_k08_match'] for r in rows), flush=True)


if __name__ == '__main__':
    main()
