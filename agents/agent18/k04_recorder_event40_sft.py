"""H-17 source-only heldout event=1+randrange(40) emitter variation.
Run from repo root: python agents/agent18/k04_recorder_event40_sft.py
Extends agent18's fully reproduced 4,230-schema source-only negative.
"""
import importlib.util
from functools import lru_cache
from pathlib import Path

P = Path(__file__).with_name('k04_recorder_alt_stage_sft.py')
spec = importlib.util.spec_from_file_location('source_model', P)
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
original = s.consumes


@lru_cache(None)
def event40(pos, field, value, mode, epoch):
    if field != 'event':
        return original(pos, field, value, mode, epoch)
    n, bits = 40, 6
    if not 0 <= value < n:
        return ()
    current = s.observed(pos)
    if mode == 'u32scale':
        return (1,) if current is None or any(((x * n) >> 32) == value for x in current) else ()
    if mode == 'mod':
        return (1,) if current is None or any(((x >> (32-bits)) % n) == value for x in current) else ()
    assert mode == 'range'
    lengths=[]
    for length in range(1,13):
        valid=True
        for j in range(length):
            outputs = s.observed(pos+j)
            if outputs is None:
                continue
            if j+1 == length:
                if not any(x >> (32-bits) == value for x in outputs):
                    valid=False
                    break
            elif not any(x >> (32-bits) >= n for x in outputs):
                valid=False
                break
        if valid:
            lengths.append(length)
    return tuple(lengths)


if __name__ == '__main__':
    s.consumes = event40
    s.main()
