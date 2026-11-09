"""Source-first node50 recorder control prediction under conditional p951 MT model.

Uses the unchanged printer-only symbolic basis, with the disputed K04 row
omitted, and withholds a record's CONTROL during metadata-based stage search.
Shows one successful complete original holdout and direct counterexamples.
"""
import hashlib
import random
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'agents/agent49'))
from k04_p951_symbolic_basis import source, get, temper

REC_SHA = '5ebc6204ed773102237dd287772de96d19740e163b49b4075537d937888657ba'


def original_rows():
    raw = (ROOT / 'resources/evidence/recorder/trip-recorder.raw').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == REC_SHA
    rows = {}
    for i in range(88):
        row = raw[16 + i * 24:16 + (i + 1) * 24]
        timestamp, node, event, latch, seq = struct.unpack_from('<IHBBI', row)
        control, aux, crc = struct.unpack_from('<III', row, 12)
        if node == 50:
            assert zlib.crc32(row[:20]) == crc
            rows[seq] = dict(latch=latch, aux=aux, event=event, control=control)
    assert set(rows) == set(range(72))
    return rows


def predicted_original():
    basis, symbolic = source(ROOT / 'resources')
    assert basis.rank == 15365
    prediction = {}
    for stage in range(-950, -250):
        mask = val = 0
        for bit, equation in enumerate(temper(get(symbolic, stage))):
            known = basis.predict(equation)
            if known is not None:
                mask |= 1 << bit
                val |= known << bit
        prediction[stage] = (mask, val)
    return prediction


def matches(prediction, stage, width, expected):
    mask, val = prediction[stage]
    return (((val ^ expected << (32 - width)) & mask) >> (32 - width)) == 0


def could_reject(prediction, stage, width, bound):
    mask, val = prediction[stage]
    mask >>= 32 - width
    val >>= 32 - width
    return (val | (((1 << width) - 1) ^ mask)) >= bound


def metadata_only(prediction, fields, stage):
    if not matches(prediction, stage - 1, 3, fields['latch']):
        return False
    for skip_aux in range(4):
        aux_stage = stage + 1 + skip_aux
        if not all(could_reject(prediction, i, 13, 6000)
                   for i in range(stage + 1, aux_stage)):
            continue
        if not matches(prediction, aux_stage, 13, fields['aux'] - 2000):
            continue
        for skip_event in range(4):
            event_stage = aux_stage + 1 + skip_event
            if not all(could_reject(prediction, i, 6, 40)
                       for i in range(aux_stage + 1, event_stage)):
                continue
            if matches(prediction, event_stage, 6, fields['event'] - 1):
                return True
    return False


def trace_from_anchor(prediction, rows, seq0, start_stage, seq_end):
    candidates = {start_stage}
    trace = {}
    for seq in range(seq0 + 1, seq_end + 1):
        fields = {key: rows[seq][key] for key in ('latch', 'aux', 'event')}
        candidates = {
            stage
            for prev in candidates
            for stage in range(prev + 4, prev + 12)
            if stage in prediction and stage - 1 in prediction
            and stage + 9 in prediction
            and metadata_only(prediction, fields, stage)
        }
        trace[seq] = sorted(candidates)
        if not candidates:
            break
    return trace


class CountingRandom(random.Random):
    def __init__(self, seed):
        super().__init__(seed)
        self.draws = 0

    def getrandbits(self, width):
        self.draws += 1
        return super().getrandbits(width)


def synthetic_control(seed):
    generator = CountingRandom(seed)
    rec = {}
    starts = {}
    for seq in range(5):
        latch = generator.getrandbits(3)
        starts[seq] = generator.draws
        control = generator.getrandbits(32)
        aux = 2000 + generator.randrange(6000)
        event = 1 + generator.randrange(40)
        generator.getrandbits(32)  # independent clock/context draw
        rec[seq] = dict(latch=latch, control=control, aux=aux, event=event)
    shadow = random.Random(seed)
    pred = {i: (0xffffffff, shadow.getrandbits(32))
            for i in range(generator.draws + 12)}
    result = trace_from_anchor(pred, rec, 0, starts[0], 4)
    assert all(result[i] == [starts[i]] for i in range(1, 5)), (seed, result)
    assert all(pred[starts[i]][1] == rec[i]['control'] for i in range(5))


def main():
    for seed in (0, 1, 2345, 20261109, 123456789, 0xDEADBEEF):
        synthetic_control(seed)
    pred = predicted_original()
    rec = original_rows()
    late = trace_from_anchor(pred, rec, 41, -568, 46)
    assert late[42] == [-563, -562, -561]
    assert late[43] == [-559, -552, -551]
    assert late[44] == [-545]
    assert late[45] == [-540]
    assert late[46] == []
    mask44, val44 = pred[-545]
    mask45, val45 = pred[-540]
    assert mask44 == 0xffffffff
    assert val44 == rec[44]['control']
    assert mask45.bit_count() == 26
    assert ((val45 ^ rec[45]['control']) & mask45) == 0

    early = trace_from_anchor(pred, rec, 25, -677, 29)
    assert early[28] == [-654] and early[29] == [-650]
    assert all(pred[early[i][0]][0] == 0xffffffff for i in (28, 29))
    assert all(pred[early[i][0]][1] != rec[i]['control'] for i in (28, 29))

    print('6/6 genuine seeded synthetic whole-packet controls PASS')
    print('seq41 source-anchor -568; stage candidates:',
          {i: late[i] for i in range(42, 47)})
    print('metadata-only complete original seq44 CONTROL:',
          val44.to_bytes(4, 'little').hex().upper(),
          'observed:', rec[44]['control'].to_bytes(4, 'little').hex().upper())
    print('seq45 26/32 predicted control bits MATCH')
    print('UNSUPPORTED GLOBAL WRITER: seq46 no path; seq28/29 full values FAIL')
    print('No recovered original K04 coupon or K08 author-final wording')


if __name__ == '__main__':
    main()
