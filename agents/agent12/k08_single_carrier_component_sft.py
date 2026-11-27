#!/usr/bin/env python3
"""Bounded K08 single-carrier component-construction test.

Reads the 45 permitted members of the 46-file H-17 export under resources/.
The quarantined BX25-08 PDF is never read: its previously pinned SHA-256 is
used ONLY for the original manifest proof. The selected PS-261003-0417 ACK2
payload is excluded; the five frozen single-carrier maps are unchanged.
The official acceptance data and source files are read-only.
"""
from __future__ import annotations
import hashlib, hmac, json, re, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "resources"
SOURCE_PATHS = """
START_HERE.md
acceptance.json
candidate.template.json
evidence/archive-labels.ini
evidence/crew/galley-and-stores.log
evidence/crew/noticeboard-and-desk-notes.txt
evidence/h17-supplemental-office-files/BX25-08.pdf
evidence/h17-supplemental-office-files/print-fleet-retirement-note.txt
evidence/h17-supplemental-office-files/retired-office-bookmarks.html
evidence/h17-supplemental-office-files/supplier-reconciliation-L29.csv
evidence/mail/01.eml
evidence/mail/02.eml
evidence/mail/03.eml
evidence/mail/04.eml
evidence/mail/05.eml
evidence/mail/06.eml
evidence/mail/07.eml
evidence/mail/08.eml
evidence/mail/09.eml
evidence/mail/10.eml
evidence/mail/11.eml
evidence/mail/12.eml
evidence/mail/13.eml
evidence/mail/14.eml
evidence/mail/15.eml
evidence/mail/16.eml
evidence/mail/17.eml
evidence/mail/18.eml
evidence/mail/19.eml
evidence/mail/20.eml
evidence/mail/INDEX.md
evidence/maintenance/inspection-rounds.log
evidence/maintenance/seal-receipts.jsonl
evidence/maintenance/work-order-417.html
evidence/print/spool-reconstruction.log
evidence/procedures/RC-17-scans.txt
evidence/procedures/document-register.log
evidence/recorder/format-note.txt
evidence/recorder/trip-recorder.raw
evidence/records-custodian.txt
evidence/recovery-routing.json
evidence/telemetry/export-readme.txt
evidence/telemetry/freeze-export.jsonl
evidence/transfers/queue-note.txt
evidence/transfers/transfer-audit.jsonl
verify.py
""".split()
RESTRICTED_PDF = "evidence/h17-supplemental-office-files/BX25-08.pdf"
PINNED_PDF_SHA256 = "b6a6156f596575b988126c6d3e5cbb88d5794cc927a5564c37b6ddb8cecc3425"
EXPECTED_MANIFEST = "cf169f8c3f56455dd24c8ebbd41651b04b799252781ed910200660c9609f910d"
EXPECTED_SPOOL = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
EXPECTED_NOTES = "13f2318ccc54f35b590a2d76b3a80244fe24d70f0699c67c05858e8b8983c5cb"

def sha(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def read(rel: str) -> bytes:
    # Fail before opening the hash-only PDF, including any new PDF path.
    if rel.lower().endswith(".pdf"):
        raise ValueError("PDF inputs are quarantined; no content/derivative read")
    return (RES / rel).read_bytes()

def manifest_digest() -> str:
    # Reconstruct the historical manifest only from safe members and the
    # *already established* hash. This is NOT a PDF content verification.
    rows = []
    for rel in SOURCE_PATHS:
        digest = PINNED_PDF_SHA256 if rel == RESTRICTED_PDF else hashlib.sha256(read(rel)).hexdigest()
        rows.append(rel + "\0" + digest)
    return hashlib.sha256("\n".join(sorted(rows)).encode()).hexdigest()

def build_carriers() -> dict[bytes, str]:
    src: dict[bytes, str] = {}
    def add(label: str, value: bytes) -> None:
        if len(value) == 16:
            src.setdefault(value, label)

    # Exact 32-hex-character fields from the supplied export. Remove only the
    # disputed PS-0417 ACK2 row before scanning the spool source.
    for rel in SOURCE_PATHS:
        if rel == RESTRICTED_PDF or rel in ("acceptance.json", "verify.py", "candidate.template.json"):
            continue
        data = read(rel)
        if rel == "evidence/print/spool-reconstruction.log":
            data = b"\n".join(
                line for line in data.splitlines()
                if not (b"JOB=PS-261003-0417" in line and b"ATTEMPT=2 STATE=ACK" in line)
            )
        for match in re.finditer(rb"(?<![0-9A-Fa-f])([0-9A-Fa-f]{32})(?![0-9A-Fa-f])", data):
            add(f"HEX32:{rel}:{match.start()}", bytes.fromhex(match.group(1).decode()))

    # Four-word recorder windows in physical, sorted, and node/event order.
    raw = read("evidence/recorder/trip-recorder.raw")
    controls, records = [], []
    for i in range(88):
        record = raw[16 + i * 24:16 + (i + 1) * 24]
        _, node, event, latch, seq, control, aux, crc = struct.unpack("<IHBBI4sII", record)
        controls.append(control)
        records.append((node, event, latch, seq, control))
    for i in range(85):
        add(f"TRP2:physical:{i}", b"".join(controls[i:i+4]))
    ordered = sorted(records, key=lambda x: (x[0], x[1], x[3], x[2]))
    for i in range(85):
        add(f"TRP2:sorted:{i}", b"".join(x[4] for x in ordered[i:i+4]))
    for node, event in sorted(set((x[0], x[1]) for x in records)):
        group = sorted((x for x in records if (x[0], x[1]) == (node, event)), key=lambda x: x[3])
        for i in range(len(group) - 3):
            add(f"TRP2:node{node}ev{event}:{i}", b"".join(x[4] for x in group[i:i+4]))

    # Transfer checkpoint vectors and windows.
    transfers = [json.loads(line) for line in read("evidence/transfers/transfer-audit.jsonl").splitlines()]
    for name in ("AX-7778", "AX-7781", "AX-7782", "AX-7783"):
        rows = sorted((x for x in transfers if x["kind"] == "CHUNK" and x["transfer"] == name),
                      key=lambda x: (x["seq"], x["attempt"]))
        checkpoints = [bytes.fromhex(x["checkpoint"]) for x in rows]
        for i in range(len(checkpoints) - 7):
            add(f"{name}:sorted8:{i}", b"".join(checkpoints[i:i+8]))
        for attempt in (1, 2):
            add(f"{name}:attempt{attempt}",
                b"".join(bytes.fromhex(x["checkpoint"]) for x in rows if x["attempt"] == attempt))
        greatest = [
            bytes.fromhex(max((x for x in rows if x["seq"] == j), key=lambda x: x["attempt"])["checkpoint"])
            for j in range(8)
        ]
        add(f"{name}:greatest", b"".join(greatest))

    # RC-17 footer-control quartets.
    pages = read("evidence/procedures/RC-17-scans.txt").decode().split("\f")
    footers = []
    for page in pages:
        match = re.search(r"Footer control strip:\s*([0-9A-F]{8})", page)
        if match:
            rev = re.search(r"DOCUMENT RC-17 / REV ([^/]+) / SECTION ([^\n]+)", page)
            footers.append((rev.group(1).strip(), rev.group(2).strip(), bytes.fromhex(match[1])))
    for i in range(len(footers) - 3):
        add(f"RC17:scan:{i}", b"".join(x[2] for x in footers[i:i+4]))
    for revision in sorted(set(x[0] for x in footers)):
        by_section = {section: value for rev, section, value in footers if rev == revision}
        if len(by_section) == 4:
            add(f"RC17:{revision}:service",
                b"".join(by_section[k] for k in ("DRAIN", "ISOLATE", "PURGE", "VERIFY")))
            add(f"RC17:{revision}:alphabet", b"".join(by_section[k] for k in sorted(by_section)))

    # Telemetry DIAG_WORD eight-halfword windows.
    telemetry = [json.loads(line) for line in read("evidence/telemetry/freeze-export.jsonl").splitlines()]
    subsets = {
        "ALL": [x for x in telemetry if x.get("field") == "DIAG_WORD"],
        "LT204": [x for x in telemetry if x.get("tag") == "LT-204" and x.get("field") == "DIAG_WORD"],
        "GOODHOLD": [x for x in telemetry if x.get("tag") == "LT-204" and x.get("field") == "DIAG_WORD"
                     and x.get("quality") == "GOOD" and x.get("state") == "HOLD"],
    }
    for name, subset in subsets.items():
        orders = (
            ("source", subset),
            ("seq", sorted(subset, key=lambda x: (x["seq"], x["revision"]))),
            ("time", sorted(subset, key=lambda x: x["ts"])),
        )
        for order, rows in orders:
            words = [int(x["value"]).to_bytes(2, "big") for x in rows
                     if isinstance(x.get("value"), int) and 0 <= x["value"] <= 65535]
            for i in range(len(words) - 7):
                add(f"TELEMETRY:{name}:{order}:{i}", b"".join(words[i:i+8]))

    # Four-serial seal windows in source and permit/bay order.
    seals = [json.loads(line) for line in read("evidence/maintenance/seal-receipts.jsonl").splitlines()]
    serials = [(x["permit"], x["bay"], x["serial"].split("-")[-1]) for x in seals]
    for i in range(len(serials) - 3):
        add(f"SEAL:source:{i}", b"".join(bytes.fromhex(x[2]) for x in serials[i:i+4]))
    for permit in sorted(set(x[0] for x in serials)):
        group = sorted((x for x in serials if x[0] == permit), key=lambda x: x[1])
        for i in range(len(group) - 3):
            add(f"SEAL:{permit}:{i}", b"".join(bytes.fromhex(x[2]) for x in group[i:i+4]))

    accepted = {
        "K01": "049AAB2E1CDE7A82CD7C60234303C91A",
        "K02": "0D7E3AB56FB75DA3EB0E2E06786D239E",
        "K03": "1384AF96E25D6ADA666209CB55E062FA",
        "K05": "FF8B78200A56E8586DCDA00EF01E4572",
        "K06": "5DBF40EE52FAAED9A536D3326CF0D95A",
        "K07": "93495F5E425AB8E592123DABAEB68545",
    }
    for name, value in accepted.items():
        add(f"DERIVED:{name}", bytes.fromhex(value))
    prehashes = {
        "K02_PREHASH": "E1A5E474BAD7E853A2E8C71D3317D507",
        "K03_PREHASH": "D7DAD6BC9714519B7DAD0AD4BE8E87FD",
        "K07_PREHASH": "8947CEDCB9CC73BAB7E87BE63302C5C9",
    }
    for name, value in prehashes.items():
        add(f"PREHASH:{name}", bytes.fromhex(value))

    route = json.loads(read("evidence/recovery-routing.json"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    known = {
        "N02": "A good watch leaves the room ready for the next pair of hands.",
        "N06": "The little lamp stays on until the corridor has gone quiet.",
        "N17": "Leave the light on for the next watch.",
        "N18": "Back before the first boat.",
    }
    def normalize(text: str) -> str:
        return " ".join(re.sub(r"[^a-z0-9\s]", " ", text.lower()).split())
    for name, text in known.items():
        add(f"EMILY_HMAC_{name}", hmac.digest(nonce, normalize(text).encode(), "sha256")[:16])
    return src

def candidate_methods(nonce: bytes):
    return {
        "identity": lambda value: value,
        "sha256_first16": lambda value: sha(value)[:16],
        "hmac_nonce_key_raw": lambda value: hmac.digest(nonce, value, "sha256")[:16],
        "sha256_nonce_prefix": lambda value: sha(nonce + value)[:16],
        "sha256_nonce_suffix": lambda value: sha(value + nonce)[:16],
    }

def scan(src, target, methods):
    hits, checks = [], 0
    for value, label in src.items():
        for method, transform in methods.items():
            component = transform(value)
            assert len(component) == 16
            checks += 1
            if sha(component).hex() == target:
                hits.append((label, method, component.hex().upper()))
    return checks, hits

def main():
    assert len(SOURCE_PATHS) == 46
    assert manifest_digest() == EXPECTED_MANIFEST
    assert hashlib.sha256(read("evidence/print/spool-reconstruction.log")).hexdigest() == EXPECTED_SPOOL
    assert hashlib.sha256(read("evidence/crew/noticeboard-and-desk-notes.txt")).hexdigest() == EXPECTED_NOTES
    route = json.loads(read("evidence/recovery-routing.json"))
    acceptance = json.loads(read("acceptance.json"))
    nonce = bytes.fromhex(route["K08"]["desk_nonce"])
    target = acceptance["slot_sha256"]["K08"]
    src = build_carriers()
    assert 0 < len(src) <= 536, len(src)
    assert all(RESTRICTED_PDF not in label for label in src.values())
    assert bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5") not in src
    methods = candidate_methods(nonce)
    checks, original_hits = scan(src, target, methods)

    planted_source = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
    assert planted_source not in src
    controls = {}
    for name, transform in methods.items():
        planted_component = transform(planted_source)
        planted_target = sha(planted_component).hex()
        synthetic_src = dict(src)
        synthetic_src[planted_source] = "SYNTHETIC_PLANTED_SOURCE"
        _, planted_hits = scan(synthetic_src, planted_target, {name: transform})
        controls[name] = any(
            label == "SYNTHETIC_PLANTED_SOURCE" and method == name and value == planted_component.hex().upper()
            for label, method, value in planted_hits
        )
        assert controls[name]

    report = {
        "source_files_in_manifest": len(SOURCE_PATHS),
        "readable_source_files": len(SOURCE_PATHS) - 1,
        "restricted_pdf_read": False,
        "restricted_pdf_hash_only": PINNED_PDF_SHA256,
        "source_manifest_sha256": EXPECTED_MANIFEST,
        "distinct_16_byte_carriers": len(src),
        "selected_k04_ack2_excluded": True,
        "methods": list(methods),
        "complete_original_component_checks": checks,
        "original_k08_commitment_hits": original_hits,
        "synthetic_positive_controls": controls,
        "status": "NO_MATCH" if not original_hits else "HIT",
        "target_k08_sha256": target,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if original_hits:
        raise SystemExit(10)

if __name__ == "__main__":
    main()
