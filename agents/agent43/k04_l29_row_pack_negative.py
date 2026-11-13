#!/usr/bin/env python3
"""Reproduce the frozen L-29 five-row binary-pack and shared-XOR negatives."""
import csv, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv": "73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e",
    "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt": "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf",
    "evidence/print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "evidence/recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
    "acceptance.json": "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f",
}
NORTH = ["ST-094", "ST-081", "ST-106", "ST-099", "ST-112"]
SOUTH = ["ST-130", "ST-151", "ST-121", "ST-135", "ST-142"]

def pack(order, by_ticket):
    out = bytearray()
    for ticket in order:
        row = by_ticket[ticket]
        assert row["run"] == "R3" and row["posting"] == "POSTED"
        out.append(int(ticket.split("-")[1]))
        out.extend(round(float(row["amount_eur"]) * 100).to_bytes(2, "big"))
    out.append(3)
    assert len(out) == 16
    return bytes(out)

def main():
    for rel, expected in PINS.items():
        actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        assert actual == expected, (rel, actual)
    fleet = (ROOT / "evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt").read_text()
    def order(set_name):
        return re.findall(rf"^{re.escape(set_name)}\s+0[1-5]\s+(ST-[0-9]{3})\s+", fleet, re.M)
    assert order("L-29/N") == NORTH and order("L-29/S") == SOUTH
    csv_path = ROOT / "evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv"
    lines = [line for line in csv_path.read_text().splitlines() if not line.startswith("#")]
    rows = list(csv.DictReader(lines))
    by_ticket = {}
    for ticket in NORTH + SOUTH:
        found = [r for r in rows if r["line_ref"] == ticket and r["run"] == "R3" and r["posting"] == "POSTED"]
        assert len(found) == 1, (ticket, len(found))
        r = found[0]
        if ticket in NORTH:
            assert r["account"] == "FA-17" and r["folio_or_jacket"] == "H17-POL-17/A3"
        else:
            assert r["account"] == "LV-42" and r["folio_or_jacket"] == "CS-18/5"
        by_ticket[ticket] = r
    north, south = pack(NORTH, by_ticket), pack(SOUTH, by_ticket)
    spool = (ROOT / "evidence/print/spool-reconstruction.log").read_text()
    m = re.findall(r"^2026-10-03T18:24:00Z JOB=PS-261003-0448 ATTEMPT=1 STATE=ACK CLASS=RECOVER PAYLOAD=([0-9A-F]{32}) DEST=desk$", spool, re.M)
    assert len(m) == 1
    south_ack = bytes.fromhex(m[0])
    route = json.loads((ROOT / "evidence/recovery-routing.json").read_text())
    acceptance = json.loads((ROOT / "acceptance.json").read_text())
    mask = bytes.fromhex(route["K04"]["masked_component"])
    required = acceptance["slot_sha256"]["K04"]
    direct = bytes(a ^ b for a, b in zip(north, mask))
    direct_hash = hashlib.sha256(direct).hexdigest().upper()
    pad = bytes(a ^ b for a, b in zip(south, south_ack))
    north_payload = bytes(a ^ b for a, b in zip(north, pad))
    shared = bytes(a ^ b for a, b in zip(north_payload, mask))
    shared_hash = hashlib.sha256(shared).hexdigest().upper()
    print("north_raw", north.hex().upper())
    print("south_raw", south.hex().upper())
    print("south_ack", south_ack.hex().upper())
    print("south_direct_match", south == south_ack)
    print("direct_component", direct.hex().upper(), "sha256", direct_hash)
    print("shared_pad", pad.hex().upper(), "north_payload", north_payload.hex().upper())
    print("shared_component", shared.hex().upper(), "sha256", shared_hash)
    print("required_K04_sha256", required.upper())
    assert north.hex().upper() == "5E07305101A46A04E263000070000003"
    assert south.hex().upper() == "8201369700007902F88703D48E025803"
    assert direct_hash == "947DCC2B4AFC6E15468EAC037FCCF3431ACFD4751660EF09921BE2A10EC877FF"
    assert direct_hash.lower() != required.lower() and shared_hash.lower() != required.lower()
    assert south != south_ack

if __name__ == "__main__":
    main()
