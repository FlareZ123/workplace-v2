"""K04 ordinary-spool bitserial recurrence holdout; does not train on selected retry."""
import hashlib
import pathlib
import re
import sys

SHA = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"

def bm(bits):
    c = b = 1
    order, shift, history = 0, 1, 0
    for n, value in enumerate(bits):
        history = (history << 1) | value
        if (c & history).bit_count() & 1:
            old = c
            c ^= b << shift
            if 2 * order <= n:
                order, b, shift = n + 1 - order, old, 1
            else:
                shift += 1
        else:
            shift += 1
    return c, order

def holdout(bits, training=12288):
    c, order = bm(bits[:training])
    history = 0
    for bit in bits[:training]:
        history = (history << 1) | bit
    matched = 0
    for bit in bits[training:]:
        matched += (((c >> 1) & history).bit_count() & 1) == bit
        history = (history << 1) | bit
    return order, matched

def main(path):
    original = pathlib.Path(path).read_bytes()
    assert hashlib.sha256(original).hexdigest() == SHA
    pattern = re.compile(rb"JOB=PS-261003-(\d+) ATTEMPT=1 STATE=ACK .* PAYLOAD=([0-9A-F]{32})")
    data = {
        int(job): bytes.fromhex(value.decode("ascii"))
        for job, value in pattern.findall(original)
        if 300 <= int(job) <= 427
    }
    assert sorted(data) == list(range(300, 428))
    assert data[300].hex().upper() == "FBBBC54356483F5864BB3F06794518A5"
    synthetic = [int(x) for x in "10100111001010101"]
    for index in range(len(synthetic), 512):
        synthetic.append(synthetic[index - 17] ^ synthetic[index - 3])
    assert holdout(synthetic, 256) == (17, 256)
    print("Positive synthetic LFSR: 256/256 heldout bits exact")
    expected = {
        (False, False): (6147, 2044),
        (False, True): (6143, 2092),
        (True, False): (6143, 2025),
        (True, True): (6145, 2064),
    }
    for (reverse_words, lsb_first), wanted in expected.items():
        bits = []
        for job in range(300, 428):
            block = data[job]
            words = [block[i:i + 4] for i in range(0, 16, 4)]
            if reverse_words:
                words.reverse()
            for word in words:
                for byte in word:
                    sequence = range(8) if lsb_first else range(7, -1, -1)
                    bits.extend((byte >> shift) & 1 for shift in sequence)
        result = holdout(bits)
        assert result == wanted, (reverse_words, lsb_first, result, wanted)
        print(f"reverse_words={reverse_words} lsb_first={lsb_first}: BM order {result[0]}; holdout {result[1]}/4096")

if __name__ == "__main__":
    main(sys.argv[1])
