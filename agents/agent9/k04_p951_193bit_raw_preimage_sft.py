"""Run the conditional p951 193-bit carrier screen with raw K02/K03/K07 inputs.
Requires Python 3 and g++. Uses the repository's Agent49 symbolic MT basis.
"""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "mt_source", ROOT / "agents/agent49/k04_p951_symbolic_basis.py"
)
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
mt.LAST = 1578
basis, states = mt.source(ROOT / "resources")
assert basis.rank == 15365

SOURCE = {
    "K01-WN14": "049AAB2E1CDE7A82CD7C60234303C91A",
    "K05-TRP2": "FF8B78200A56E8586DCDA00EF01E4572",
    "K06-RC17": "5DBF40EE52FAAED9A536D3326CF0D95A",
    "K04-ROUTE-MASK": "8556C8CB6140A7F9A5123AC7571BEE1C",
    "K08-DESK-NONCE": "5F933DA6A1BD03C32DA5CBC25344F497",
    "K02-LT204-HASH": "0D7E3AB56FB75DA3EB0E2E06786D239E",
    "K03-PTW-HASH": "1384AF96E25D6ADA666209CB55E062FA",
    "K07-AX-HASH": "93495F5E425AB8E592123DABAEB68545",
    "K02-LT204-RAW": "E1A5E474BAD7E853A2E8C71D3317D507",
    "K03-PTW-RAW": "D7DAD6BC9714519B7DAD0AD4BE8E87FD",
    "K07-AX-RAW": "8947CEDCB9CC73BAB7E87BE63302C5C9",
}
SOURCE = {name: bytes.fromhex(value) for name, value in SOURCE.items()}
PARTIALS = ("native31", "temp2", "temp9", "temp13", "temp20", "temp27", "temp31")
MASK = SOURCE["K04-ROUTE-MASK"]
TARGET = json.loads((ROOT / "resources/acceptance.json").read_text())["slot_sha256"]["K04"]


def temper_number(x):
    x ^= x >> 11
    x ^= (x << 7) & 0x9D2C5680
    x ^= (x << 15) & 0xEFC60000
    x ^= x >> 18
    return x & 0xFFFFFFFF


class DonorMap:
    def __init__(self, source_basis):
        self.rows = {p: (e, c) for p, (e, c) in source_basis.rows.items()}
        self.syndromes = []

    def insert(self, expression, coefficient):
        while expression:
            pivot = expression.bit_length() - 1
            if pivot not in self.rows:
                self.rows[pivot] = (expression, coefficient)
                return
            row, value = self.rows[pivot]
            expression ^= row
            coefficient ^= value
        if coefficient:
            self.syndromes.append(coefficient)

    def reduce(self, expression):
        coefficient = 0
        while expression:
            pivot = expression.bit_length() - 1
            row, value = self.rows[pivot]
            expression ^= row
            coefficient ^= value
        return coefficient


def evaluate(donor_bits, coefficient):
    return (((donor_bits << 1) & coefficient).bit_count() & 1) ^ (coefficient & 1)


def component(donor_bits, targets):
    coupon = b"".join(
        temper_number(sum(
            evaluate(donor_bits, targets[lane * 32 + bit]) << bit
            for bit in range(32)
        )).to_bytes(4, "little")
        for lane in range(4)
    )
    return bytes(a ^ b for a, b in zip(coupon, MASK))


def native_words(carrier, encoding):
    words = [
        int.from_bytes(carrier[i:i + 4], "big" if encoding & 1 else "little")
        for i in (0, 4, 8, 12)
    ]
    if encoding & 4:
        words.reverse()
    if encoding & 2:
        words = [mt.untemper(word) for word in words]
    return words


def build_map(partial):
    donor = DonorMap(basis)
    for index, stage in enumerate((1180, 1181, 1347, 1348, 1574, 1575)):
        for bit, expression in enumerate(mt.get(states, stage)):
            donor.insert(expression, 1 << (index * 32 + bit + 1))
    if partial == "native31":
        expression = mt.get(states, 1179)[31]
    else:
        expression = mt.temper(mt.get(states, 1179))[int(partial[4:])]
    donor.insert(expression, 1 << 193)
    targets = [
        donor.reduce(expression)
        for stage in range(951, 955)
        for expression in mt.get(states, stage)
    ]
    assert len(donor.syndromes) == 1 and len(targets) == 128
    return donor, targets


def main():
    with tempfile.TemporaryDirectory(prefix="h17-193bit-") as temp:
        temp = Path(temp)
        maps = []
        for partial in PARTIALS:
            donor, targets = build_map(partial)
            constant = int.from_bytes(component(0, targets), "little")
            syndrome = donor.syndromes[0]
            syndrome_constant = evaluate(0, syndrome)
            columns, syndrome_columns = [], []
            for index in range(193):
                columns.append(
                    int.from_bytes(component(1 << index, targets), "little") ^ constant
                )
                syndrome_columns.append(
                    evaluate(1 << index, syndrome) ^ syndrome_constant
                )
            maps.append((constant, syndrome_constant, columns, syndrome_columns))

        with (temp / "maps_193.bin").open("wb") as output:
            for constant, syndrome_constant, columns, syndrome_columns in maps:
                output.write(constant.to_bytes(16, "little"))
                output.write(bytes([syndrome_constant]))
                for column, syndrome_column in zip(columns, syndrome_columns):
                    output.write(column.to_bytes(16, "little"))
                    output.write(bytes([syndrome_column]))

        views = []
        for value in SOURCE.values():
            for encoding in range(8):
                views.extend(native_words(value, encoding))
        with (temp / "views_193.bin").open("wb") as output:
            for word in views:
                output.write(struct.pack("<I", word))

        cpp = Path(__file__).with_suffix(".cpp")
        executable = temp / "search"
        subprocess.run(
            ["g++", "-O3", "-std=c++17", "-march=native", str(cpp), "-o", str(executable)],
            check=True,
        )
        run = subprocess.run(
            [str(executable), str(temp)], check=True, capture_output=True, text=True
        )
        candidates = (temp / "candidates_193.bin").read_bytes()
        assert len(candidates) % 16 == 0
        hits = []
        for offset in range(0, len(candidates), 16):
            candidate = candidates[offset:offset + 16]
            if hashlib.sha256(candidate).hexdigest() == TARGET:
                hits.append({
                    "candidate_index": offset // 16,
                    "component": candidate.hex().upper(),
                })
        print(run.stdout.strip())
        print({
            "source_rank": basis.rank,
            "source_families": len(SOURCE),
            "partial_views": PARTIALS,
            "candidate_hashes_checked": len(candidates) // 16,
            "K04_target_sha256": TARGET,
            "K04_matches": hits,
        })


if __name__ == "__main__":
    main()
