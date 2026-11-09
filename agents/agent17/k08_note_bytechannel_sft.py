"""Whole-historical-control byte channel test for the conditional Nxx -> PS-0300+xx link."""
import hashlib
import hmac
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2] / "resources" / "evidence"
NOTES = ROOT / "crew" / "noticeboard-and-desk-notes.txt"
SPOOL = ROOT / "print" / "spool-reconstruction.log"
SHA_NOTES = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"
SHA_SPOOL = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
NONCE = bytes.fromhex("5F933DA6A1BD03C32DA5CBC25344F497")


def normalize(s):
    return " ".join(re.findall("[a-z0-9]+", s.lower())).encode()


def component(phrase):
    return hmac.new(NONCE, normalize(phrase), "sha256").digest()[:16]


def read_original():
    src = NOTES.read_bytes()
    ps = SPOOL.read_bytes()
    assert hashlib.sha256(src).hexdigest() == SHA_NOTES
    assert hashlib.sha256(ps).hexdigest() == SHA_SPOOL
    notes = {}
    for mt in re.finditer(r"^N(\d\d) / [^\n]+\n([^\n]*)", src.decode(), re.M):
        n = int(mt.group(1))
        body = mt.group(2)
        notes[n] = body.split(": ", 1)[-1]
    assert len(notes) == 24
    packets = {}
    for line in ps.decode().splitlines():
        m = re.search(r"JOB=PS-261003-(\d+) ATTEMPT=(\d+) STATE=(\w+) CLASS=(\w+) PAYLOAD=([A-F0-9]{32}) DEST=(\w+)", line)
        if m and 300 <= int(m[1]) <= 427 and m[2] == "1" and m[3] == "ACK":
            packets[int(m[1])] = (m[4], m[6], bytes.fromhex(m[5]))
    assert len(packets) == 128
    return notes, packets


def byte_links(htexts, packets, train, held):
    """Fit P[j] = H[perm[j]] ^ ((a[j]*job + b[j]) & 255) on two notes.

    Job difference must be odd. Test complete 8-bit predictions on every other note.
    """
    x, y = train
    dx = (x - y) % 256
    assert dx & 1
    inv = pow(dx, -1, 256)
    links = []
    for j in range(16):
        row = []
        for i in range(16):
            a = (((packets[x][j] ^ htexts[x][i]) - (packets[y][j] ^ htexts[y][i])) * inv) % 256
            b = ((packets[x][j] ^ htexts[x][i]) - a*x) % 256
            if all(packets[z][j] == htexts[z][i] ^ ((a*z+b) & 255) for z in held):
                row.append((i, a, b))
        links.append(row)
    return links


def solve_matching(links):
    destination_for_source = {}

    def take(j, seen):
        for i, a, b in links[j]:
            if i in seen:
                continue
            seen.add(i)
            if i not in destination_for_source or take(destination_for_source[i], seen):
                destination_for_source[i] = j
                return True
        return False

    for j in range(16):
        if not take(j, set()):
            return None
    return {j: next((i, a, b) for i, a, b in links[j]
                    if i in destination_for_source and destination_for_source[i] == j)
            for j in range(16)}


def run():
    notes, ps = read_original()
    pattern = {17: ("LABEL", "store"), 18: ("RECOVER", "store"), 20: ("RECOVER", "bench"),
               23: ("RECOVER", "store"), 24: ("LABEL", "store")}
    offsets = range(-1, 104)
    two = [shift for shift in offsets if all(ps[300+n+shift][:2] == v
                                          for n, v in list(pattern.items())[:2])]
    three = [shift for shift in offsets if all(ps[300+n+shift][:2] == v
                                            for n, v in list(pattern.items())[:3])]
    five = [shift for shift in offsets if all(ps[300+n+shift][:2] == v
                                           for n, v in pattern.items())]
    assert two == [0, 7] and three == five == [0], (two, three, five)
    print("CATEGORY_OFFSET_COUNT=105 two_roles=" + str(two) +
          " three_roles=" + str(three) + " five_roles=" + str(five))
    ids = (2, 6, 13, 17, 18)
    hs = {300+n: component(notes[n]) for n in ids}
    ps16 = {300+n: ps[300+n][2] for n in ids}
    assert hs[302].hex().upper() == "BF889359B0303F2B2B2FD96AE841210B"
    checked = 0
    passed = 0
    rows_with_any = 0
    for x in ps16:
        for y in ps16:
            if x == y or not ((x-y) & 1):
                continue
            held = [z for z in ps16 if z not in (x, y)]
            links = byte_links(hs, ps16, (x, y), held)
            checked += 1
            rows_with_any += sum(bool(line) for line in links)
            if solve_matching(links):
                passed += 1
    assert checked == 12
    print("SOURCE_OBSERVED calibration_pairs", checked,
          "total_byte_rows_with_any_link", rows_with_any,
          "full_source_survivors", passed)
    assert not passed

    # Genuinely generated, blinded whole-candidate channel control.
    perm = [(5*j+3) % 16 for j in range(16)]
    aa = [(9*j+5) % 256 for j in range(16)]
    bb = [(17*j+31) % 256 for j in range(16)]
    synthetic = {z: bytes(hs[z][perm[j]] ^ ((aa[j]*z+bb[j]) & 255)
                          for j in range(16)) for z in ps16}
    planted_final = component("A real synthetic caption for the late watch")
    synthetic[323] = bytes(planted_final[perm[j]] ^ ((aa[j]*323+bb[j]) & 255)
                           for j in range(16))
    for x, y in ((317, 318), (302, 313), (306, 317)):
        held = [z for z in ps16 if z not in (x, y)]
        links = byte_links(hs, synthetic, (x, y), held)
        match = solve_matching(links)
        assert match is not None
        output = bytearray(16)
        for j, (i, a, b) in match.items():
            output[i] = synthetic[323][j] ^ ((a*323+b) & 255)
        assert bytes(output) == planted_final
        assert hashlib.sha256(output).digest() == hashlib.sha256(planted_final).digest()
    print("SYNTHETIC positives PASS 3/3; chosen final component recovers exactly")
    print("HISTORICAL_K08_PASS=0; historical PS-0323 undecodable by tested channel")


if __name__ == "__main__":
    run()
