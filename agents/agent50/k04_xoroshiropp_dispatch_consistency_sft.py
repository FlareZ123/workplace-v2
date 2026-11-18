"""Six-output same-job dispatcher consistency test for xoroshiro128++ 1.0.

It uses the *untrusted copied* ACK2 payload solely to falsify or support a
proposed common PRNG dispatch producer. SAT would not prove media integrity.
No physical K04 candidate is created or tested by this script.
"""
import argparse
import json
from k04_xoroshiropp_meet_sft import (
    SEED, decode, parse_source, solve, stream, test_circuit,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--view', type=int, choices=range(4), default=0)
    parser.add_argument('--limit-seconds', type=float, default=100)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    test_circuit()
    if args.self_test:
        return
    planted = stream(SEED)
    control = solve(planted, args.limit_seconds, 16, SEED[0] & 65535)
    print(json.dumps({'experiment': 'planted_complete_six_output', **control}), flush=True)
    if control['status'] != 'SAT':
        raise SystemExit(2)
    assert control['state'] == [f'{w:016X}' for w in SEED]
    source = parse_source()
    copied = [w for block in source for w in decode(block, args.view)]
    result = solve(copied, args.limit_seconds)
    print(json.dumps({'experiment': 'original_copied_three_attempt_dispatch',
                      'view': args.view, 'status_meaning': 'dispatch_only',
                      'source_has_no_media_integrity': True,
                      **result}), flush=True)


if __name__ == '__main__':
    main()
