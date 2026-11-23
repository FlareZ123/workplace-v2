#!/usr/bin/env python3
"""H-17 offline, read-only final physical coupon / exact keeper caption intake.

Do not infer a paper coupon from the archived copied ACK or infer a keeper
caption from themes. Only independently authenticated source transcriptions
may be supplied. A completed candidate is written ONLY after the unchanged
original slot commitments and combined commitment all PASS.

For original local ZIP extraction:
    python h17_verified_manual_intake.py --root /path/to/export \
      --coupon-hex 00000000000000000000000000000000 \
      --caption 'Exact transcribed author-final phrase' \
      --output /tmp/h17-completed.json
For shared GitHub checkout, root defaults to the repository root when placed
at agents/agent31/h17_verified_manual_intake.py.
"""
from __future__ import annotations
import argparse
import os
import hashlib
import hmac
import json
from pathlib import Path
import re


def normalize_caption(s: str) -> str:
    # Route text literally says lowercase -> replace chars outside ASCII
    # a-z, digits and whitespace with spaces -> collapse whitespace and trim.
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9\s]', ' ', s.lower())).strip()


def manual_components(coupon_hex: str, caption: str, route: dict) -> tuple[str, str, str]:
    if not re.fullmatch(r'[0-9A-Fa-f]{32}', coupon_hex):
        raise ValueError('Coupon must be exactly 32 hexadecimal characters (16 bytes)')
    physical_coupon = bytes.fromhex(coupon_hex)
    mask = bytes.fromhex(route['K04']['masked_component'])
    if len(mask) != 16:
        raise ValueError('Original K04 route mask is not 16 bytes')
    k04 = bytes(a ^ b for a, b in zip(physical_coupon, mask)).hex().upper()
    normalized = normalize_caption(caption)
    if not normalized:
        raise ValueError('The normalized physical envelope caption is empty')
    nonce = bytes.fromhex(route['K08']['desk_nonce'])
    k08 = hmac.new(nonce, normalized.encode('utf-8'), hashlib.sha256).digest()[:16].hex().upper()
    return k04, k08, normalized


def paths(root: Path) -> tuple[Path, Path, Path, Path]:
    r = root / 'resources' if (root / 'resources' / 'acceptance.json').is_file() else root
    acceptance = r / 'acceptance.json'
    routing = r / 'evidence' / 'recovery-routing.json'
    baseline = root / 'candidate.json'
    if not baseline.is_file():
        baseline = r / 'candidate.json'
    verifier = r / 'verify.py'
    if not verifier.is_file():
        verifier = root / 'verify.py'
    return acceptance, routing, baseline, verifier


def original_verify(candidate: dict, targets: dict, verifier_path: Path) -> dict:
    import importlib.util
    spec = importlib.util.spec_from_file_location('h17_official_verify_for_intake', verifier_path)
    if spec is None or spec.loader is None:
        raise ValueError('Original verifier could not be imported')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.evaluate(candidate, targets)


ORIGINAL_PINS = {
    'acceptance': '681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f',
    'routing': 'f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5',
    'verifier': '01cedbfa08a28b388f8ab09b96c9c562a920d8ae9a7cc582ba3c79d138681cd0',
}

def read_coupon(path: Path) -> str:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 128:
        raise ValueError('Coupon file must be a regular file of <=128 bytes')
    raw = path.read_bytes()
    if len(raw) == 16:
        return raw.hex().upper()
    try:
        return raw.decode('ascii').strip()
    except UnicodeDecodeError as exc:
        raise ValueError('Coupon file must contain exactly 16 raw bytes or 32 hexadecimal digits') from exc

def read_caption(path: Path) -> str:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1_000_000:
        raise ValueError('Caption file must be a regular UTF-8 text file under 1 MB')
    return path.read_text(encoding='utf-8-sig')

def execute(root: Path, coupon_hex: str, caption: str, output: Path | None, *, allow_synthetic_targets: bool=False) -> dict:
    acceptance, routing, baseline, verifier = paths(root)
    if not (acceptance.is_file() and routing.is_file() and baseline.is_file() and verifier.is_file()):
        raise ValueError('Original acceptance, routing, candidate and verifier must be present')
    if not allow_synthetic_targets:
        for label, file in [('acceptance', acceptance), ('routing', routing), ('verifier', verifier)]:
            if hashlib.sha256(file.read_bytes()).hexdigest() != ORIGINAL_PINS[label]:
                raise ValueError('Original '+label+' has changed: refusing non-original commitment check')
    targets = json.loads(acceptance.read_text(encoding='utf-8'))
    route = json.loads(routing.read_text(encoding='utf-8'))
    candidate = json.loads(baseline.read_text(encoding='utf-8'))
    k04, k08, normalized = manual_components(coupon_hex, caption, route)
    candidate = {**candidate, 'K04': k04, 'K08': k08}
    result = original_verify(candidate, targets, verifier)
    if not result['accepted']:
        return {'accepted': False, 'verification': result,
                'notice': 'No completed recovery was written; authenticate original physical evidence and retry'}
    if output is not None:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        # Never overwrite an existing output artifact; avoid stale key confusion.
        fd = os.open(str(output), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(candidate, f, indent=2)
            f.write('\n')
    return {'accepted': True, 'verification': result, 'candidate': candidate,
            'normalized_caption': normalized, 'written': str(output) if output else None}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    coupon = parser.add_mutually_exclusive_group(required=True)
    coupon.add_argument('--coupon-hex', help='Exact 16-byte physical RECOVER coupon, not the copied log packet')
    coupon.add_argument('--coupon-file', type=Path, help='Secure regular file with exactly 16 raw bytes or 32 ASCII hexadecimal digits')
    caption = parser.add_mutually_exclusive_group(required=True)
    caption.add_argument('--caption', help='Complete author-final recovery-envelope caption, not a draft or paraphrase')
    caption.add_argument('--caption-file', type=Path, help='Secure UTF-8 file containing complete author-final caption')
    parser.add_argument('--output', type=Path, help='Write accepted eight-component candidate only; never overwrite')
    args = parser.parse_args(argv)
    try:
        coupon_hex = args.coupon_hex if args.coupon_hex is not None else read_coupon(args.coupon_file)
        caption_text = args.caption if args.caption is not None else read_caption(args.caption_file)
        result = execute(args.root, coupon_hex, caption_text, args.output)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as e:
        print(json.dumps({'accepted': False, 'error': str(e)}, indent=2))
        return 2
    if args.output is not None and result['accepted']:
        # The completed key is in a 0600 output; avoid echoing secret bytes or caption.
        result = {k: v for k, v in result.items() if k not in ('candidate','normalized_caption')}
    print(json.dumps(result, indent=2))
    return 0 if result['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
