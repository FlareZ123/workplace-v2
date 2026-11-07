#!/usr/bin/env python3
"""Read-only, source-pinned North/South cassette catch comparison."""
import csv
import hashlib
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PINS = {
    "print-fleet-retirement-note.txt": "10c3a6e46b2c8475fd5fd8333cd8546633bda7ca3eac4e813ac059cd045e3cbf",
    "supplier-reconciliation-L29.csv": "73b85da6d358cfc57dd340c1d6b84a5434d50693c6b12b256238ef3ff8c5c87e",
    "spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
}


def read_pinned(path):
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != PINS[path.name]:
        raise ValueError(f"{path.name}: expected {PINS[path.name]}, got {digest}")
    return data.decode("utf-8")


def parts(note, set_name):
    pattern = re.compile(rf"^{re.escape(set_name)}\s+(\d{{2}})\s+(ST-\d{{3}})\s+(.+)$")
    rows = []
    for line in note.splitlines():
        match = pattern.match(line)
        if match:
            tab, ticket, part = match.groups()
            rows.append({"tab": tab, "ticket": ticket, "part": part})
    if len(rows) != 5:
        raise ValueError(f"{set_name}: expected 5 tabs, found {len(rows)}")
    return rows


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    evidence = root / "resources" / "evidence"
    if not evidence.is_dir():
        evidence = root / "evidence"
    office = evidence / "h17-supplemental-office-files"
    note = read_pinned(office / "print-fleet-retirement-note.txt")
    raw_csv = read_pinned(office / "supplier-reconciliation-L29.csv")
    spool = read_pinned(evidence / "print" / "spool-reconstruction.log")
    docket = list(csv.DictReader(io.StringIO("\n".join(
        line for line in raw_csv.splitlines() if not line.startswith("#")
    ))))

    def settlement(ticket, run):
        found = [x for x in docket if x["line_ref"] == ticket and x["run"] == run]
        if len(found) != 1:
            raise ValueError(f"{ticket}/{run}: expected one settlement, found {len(found)}")
        return found[0]

    north, south = parts(note, "L-29/N"), parts(note, "L-29/S")
    categories = lambda rows: [x["part"].split(",", 1)[0] for x in rows]
    if categories(north) != categories(south):
        raise ValueError("North/South cassette part categories do not align by tab")
    for rows, account, folio in (
        (north, "FA-17", "H17-POL-17/A3"),
        (south, "LV-42", "CS-18/5"),
    ):
        for item in rows:
            row = settlement(item["ticket"], "R3")
            if (row["posting"], row["account"], row["folio_or_jacket"]) != (
                "POSTED", account, folio
            ):
                raise ValueError(f"{item['ticket']}: unexpected R3 settlement")

    watch = [
        x for x in docket
        if x["line_ref"] in {"ST-157", "ST-164"} and x["run"] == "R3"
    ]
    if len(watch) != 2 or any(
        (x["posting"], x["account"], x["folio_or_jacket"])
        != ("POSTED", "ST-09", "STORES/FLT")
        for x in watch
    ):
        raise ValueError("Watch-Spare R3 control mismatch")

    n112_r3 = settlement("ST-112", "R3")
    n112_r4 = settlement("ST-112", "R4")
    s142_r3 = settlement("ST-142", "R3")
    assert (
        n112_r3["posting"], n112_r3["account"], n112_r3["folio_or_jacket"],
        n112_r3["description"]
    ) == ("POSTED", "FA-17", "H17-POL-17/A3", "catch cleaning")
    assert (
        n112_r4["posting"], n112_r4["account"], n112_r4["folio_or_jacket"],
        n112_r4["description"]
    ) == ("HELD", "FA-17", "H17-POL-17/A4", "duplicate settlement")
    assert (
        s142_r3["posting"], s142_r3["account"], s142_r3["folio_or_jacket"],
        s142_r3["description"]
    ) == ("POSTED", "LV-42", "CS-18/5", "catch pin")

    prefix = "2026-10-03T18:02:00Z JOB=PS-261003-0417 "
    events = [x for x in spool.splitlines() if x.startswith(prefix)]
    if len(events) != 1 or "ATTEMPT=2 STATE=ACK CLASS=RECOVER" not in events[0]:
        raise ValueError("MAIL-16 selected event header not found uniquely")
    # Only the event timestamp is used; PAYLOAD is never extracted or printed.
    job_time = datetime.fromisoformat(events[0].split(" ", 1)[0].replace("Z", "+00:00"))
    stamp = re.search(r"reconciled (\d{2} \w{3} \d{4}, \d{2}:\d{2}) UTC", note)
    if not stamp:
        raise ValueError("return-register reconciliation timestamp missing")
    register_time = datetime.strptime(
        stamp.group(1), "%d %b %Y, %H:%M"
    ).replace(tzinfo=timezone.utc)
    gap = register_time - job_time
    if gap.total_seconds() <= 0:
        raise ValueError("return-register reconciliation predates selected job")

    output = {
        "source_sha256": PINS,
        "north_selected": {
            "job": "PS-261003-0417", "route": "ESC-N", "return_set": "L-29/N",
            "account": "FA-17", "folio": "H17-POL-17/A3", "tickets": north
        },
        "south_control": {
            "job": "PS-261003-0448", "route": "ESC-S", "return_set": "L-29/S",
            "account": "LV-42", "folio": "CS-18/5", "tickets": south
        },
        "watch_spare_control": [
            {k: x[k] for k in (
                "line_ref", "run", "posting", "account", "folio_or_jacket", "description"
            )}
            for x in watch
        ],
        "north_ST112_R3": {
            k: n112_r3[k] for k in (
                "run", "posting", "account", "folio_or_jacket", "amount_eur", "description"
            )
        },
        "north_ST112_R4": {
            k: n112_r4[k] for k in (
                "run", "posting", "account", "folio_or_jacket", "amount_eur", "description"
            )
        },
        "south_ST142_R3": {
            k: s142_r3[k] for k in (
                "run", "posting", "account", "folio_or_jacket", "amount_eur", "description"
            )
        },
        "selected_job_time_utc": job_time.isoformat(),
        "return_register_reconciled_utc": register_time.isoformat(),
        "elapsed_between_selected_job_and_register_reconciliation": str(gap),
        "inference": (
            "The matched cassette-part sequence and South 'catch pin' description "
            "support a mechanical-catch hypothesis; they do not prove the North "
            "catch's exact location or that a coupon was recovered."
        ),
        "selected_payload_bytes_used": False,
        "original_coupon_recovered": False,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
