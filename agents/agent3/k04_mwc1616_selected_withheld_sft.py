"""H-17: source-only MWC1616 printer hypotheses, selected ACK2 excluded."""
from pathlib import Path
import hashlib
import re

SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
MASK = 65535
A, B = 36969, 18000


def step(x, factor):
    return factor * (x & MASK) + (x >> 16)


def fullwords(y, full_w):
    y0, y1 = y[:2]
    wlo = y0 & MASK
    whi = ((y1 & MASK) - B*wlo) & MASK
    w = (whi << 16) | wlo
    nw = step(w, B)
    zlo = ((y0 >> 16) - (whi if full_w else 0)) & MASK
    nzlo = ((y1 >> 16) - ((nw >> 16) if full_w else 0)) & MASK
    z = (((nzlo - A*zlo) & MASK) << 16) | zlo
    for target in y:
        if (((z << 16) + (w if full_w else w & MASK)) & 0xffffffff) != target:
            return False
        z, w = step(z, A), step(w, B)
    return True


def halfwords(y, factor):
    x = ((((y[1]-factor*y[0]) & MASK) << 16) | y[0])
    for target in y:
        if (x & MASK) != target:
            return False
        x = step(x, factor)
    return True


def lowbytes(y, factor):
    b0, b1 = y[:2]
    hi_lo = (b1 - factor*b0) & 255
    for lo_hi in range(256):
        for hi_hi in range(256):
            x = (((hi_hi << 8) | hi_lo) << 16) | ((lo_hi << 8) | b0)
            for target in y:
                if (x & 255) != target:
                    break
                x = step(x, factor)
            else:
                return True
    return False


def or_necessary(y):
    lo = y[0] & MASK
    hi = ((y[1] & MASK)-B*lo) & MASK
    w = (hi << 16) | lo
    for target in y:
        if (w & MASK) != (target & MASK) or ((w >> 16) & (target >> 16)) != (w >> 16):
            return False
        w = step(w, B)
    return True


def controls():
    for z0, w0 in ((0xdeadbeef, 0x12345678), (1, 2), (0xffff1234, 0x33330001)):
        for full_w in (False, True):
            z, w = z0, w0
            ys = []
            for _ in range(4):
                z, w = step(z, A), step(w, B)
                ys.append(((z << 16) + (w if full_w else w & MASK)) & 0xffffffff)
            assert fullwords(ys, full_w)
        for factor in (A, B):
            state = w0
            ys, bs = [], []
            for _ in range(16):
                ys.append(state & MASK)
                bs.append(state & 255)
                state = step(state, factor)
            assert halfwords(ys[:8], factor)
            assert lowbytes(bytes(bs), factor)


def main():
    p = Path(__file__).resolve().parents[2] / "resources/evidence/print/spool-reconstruction.log"
    raw = p.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    packets = [bytes.fromhex(x.decode("ascii")) for x in
               re.findall(rb"PAYLOAD=([0-9A-F]{32})", raw)]
    assert len(packets) == 133
    controls()
    print("PLANTED_POSITIVES=PASS")
    counts = {"mwc32": [0,0], "or_necessary": [0,0], "mwc16": [0,0], "mwc8": [0,0]}
    for i, packet in enumerate(packets):
        if i == 129:  # selected 18:02 ESC-N ACK2: never inspect in model fitting
            continue
        for endian in ("little", "big"):
            words32 = [int.from_bytes(packet[j:j+4], endian) for j in range(0,16,4)]
            words16 = [int.from_bytes(packet[j:j+2], endian) for j in range(0,16,2)]
            for reverse in (False, True):
                y32 = words32[::-1] if reverse else words32
                y16 = words16[::-1] if reverse else words16
                for full_w in (False, True):
                    counts["mwc32"][0] += fullwords(y32, full_w)
                    counts["mwc32"][1] += 1
                counts["or_necessary"][0] += or_necessary(y32)
                counts["or_necessary"][1] += 1
                for factor in (A,B):
                    counts["mwc16"][0] += halfwords(y16, factor)
                    counts["mwc16"][1] += 1
        for reverse in (False, True):
            y8 = packet[::-1] if reverse else packet
            for factor in (A,B):
                counts["mwc8"][0] += lowbytes(y8, factor)
                counts["mwc8"][1] += 1
    for name, (hits, total) in counts.items():
        print(f"{name}: {hits}/{total} complete source-packet fits")
    assert counts == {"mwc32": [0,1056], "or_necessary": [0,528],
                      "mwc16": [0,1056], "mwc8": [0,528]}
    print("ROW129_WITHHELD=TRUE; NO_K04_BYTES_RECOVERED")


if __name__ == "__main__":
    main()
