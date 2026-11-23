#!/usr/bin/env python3
"""Read-only pairing and exact-hit intake for native Windows spool SPL/SHD members.

Pairs are keyed strictly by container + parent path + normalized filename stem.
The script does not parse undocumented SHD offsets or infer a job ID from a filename.
Run from repository root; no archive members are extracted to disk.
"""
from __future__ import annotations
import argparse, gzip, hashlib, io, json, os, re, stat, tarfile, zipfile
from collections import defaultdict
from pathlib import Path, PurePosixPath

PINS = {
    "print/spool-reconstruction.log": "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083",
    "recovery-routing.json": "f8fcbca73d23bf1066edb88c088f89cd24cf22e7c78a4a412166254a4764d8a5",
}
ACCEPTANCE_PIN = "681739241b757b471acca4c0fef9d9d97e9493883887736d5db3b92bfb0c137f"
MAX_MEMBER = 32 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_DEPTH = 2

def safe_member(name, mode=0):
    path = PurePosixPath(name.replace("\\", "/"))
    return not (path.is_absolute() or ".." in path.parts or stat.S_ISLNK(mode))

def normalized_stem(name):
    return "".join(c for c in Path(name).stem.casefold() if c.isalnum())

def read_evidence(root):
    for name, expected in PINS.items():
        actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
        assert actual == expected, (name, actual)
    assert hashlib.sha256((root.parent / "acceptance.json").read_bytes()).hexdigest() == ACCEPTANCE_PIN
    route = json.loads((root / "recovery-routing.json").read_text())
    payloads = defaultdict(list)
    for line in (root / "print/spool-reconstruction.log").read_text().splitlines():
        match = re.search(r"JOB=(PS-261003-\d{4}) ATTEMPT=(\d+) STATE=(\S+) CLASS=(\S+) PAYLOAD=([0-9A-F]{32})", line)
        if match:
            job, attempt, state, job_class, hex_payload = match.groups()
            if job in {"PS-261003-0300", "PS-261003-0317", "PS-261003-0318", "PS-261003-0323", "PS-261003-0417"}:
                payloads[job].append({
                    "attempt": attempt, "state": state, "class": job_class,
                    "hex": hex_payload.upper(), "raw": bytes.fromhex(hex_payload),
                })
    return payloads, bytes.fromhex(route["K04"]["masked_component"]), bytes.fromhex(route["K08"]["desk_nonce"])

def make_patterns(payloads, mask, nonce):
    patterns = []
    jobs = set()
    for job, items in payloads.items():
        jobs.add(job)
        patterns.extend([(f"job:{job}", job.encode()), (f"job-utf16:{job}", job.encode("utf-16le"))])
        for item in items:
            label = f"{job}:attempt{item['attempt']}:{item['state']}:{item['class']}"
            patterns.extend([
                (label + ":raw", item["raw"]),
                (label + ":hex", item["hex"].encode()),
                (label + ":hex-lower", item["hex"].lower().encode()),
            ])
    for name, value in (("K04-mask", mask), ("K08-nonce", nonce)):
        patterns.extend([
            (name + ":raw", value),
            (name + ":hex", value.hex().upper().encode()),
            (name + ":hex-lower", value.hex().encode()),
        ])
    for term in ("AX-7782", "IR-261003-H17", "Emily", "N23", "final envelope",
                 "caption", "margin", "keeper", "words I finally put on it", "recovery envelope"):
        patterns.extend([
            ("text:" + term, term.encode()),
            ("text-utf16:" + term, term.encode("utf-16le")),
        ])
    return patterns, sorted(jobs)

def occurrences(data, patterns):
    hits = []
    for label, needle in patterns:
        if not needle:
            continue
        start = 0
        while True:
            position = data.find(needle, start)
            if position < 0:
                break
            hits.append({"pattern": label, "offset": position, "length": len(needle)})
            start = position + 1
    return hits

def magic(data):
    if data.startswith((b"PK\x03\x04", b"PK\x05\x06")):
        return "zip"
    if data.startswith(b"\x1f\x8b"):
        return "gzip"
    if len(data) > 262 and data[257:262] == b"ustar":
        return "tar"
    return "raw"

class Intake:
    def __init__(self, patterns, max_member=MAX_MEMBER, max_total=MAX_TOTAL, max_depth=MAX_DEPTH):
        self.patterns = patterns
        self.max_member = max_member
        self.max_total = max_total
        self.max_depth = max_depth
        self.spool_bytes = 0
        self.archive_bytes = 0
        self.members = []
        self.errors = []

    def add(self, name, container, parent, data):
        if len(data) > self.max_member:
            self.errors.append({"name": name, "reason": "member exceeds size cap", "size": len(data)})
            return
        self.spool_bytes += len(data)
        if self.spool_bytes > self.max_total:
            self.errors.append({"name": name, "reason": "total spool-member byte cap exceeded"})
            return
        extension = Path(name).suffix.casefold()
        if extension not in (".spl", ".shd"):
            return
        self.members.append({
            "name": name, "container": container, "parent": parent,
            "stem": Path(name).stem, "normalized_stem": normalized_stem(name),
            "ext": extension[1:].upper(), "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "hits": occurrences(data, self.patterns),
        })

    def walk_bytes(self, name, container, data, depth=0):
        kind = magic(data)
        # A native spool file can itself be an OPC ZIP/XPS package. Preserve
        # its SPL identity for pairing and let the commitment scanner decode
        # the package's rendered content.
        if kind == "raw" or Path(name).suffix.casefold() in (".spl", ".shd"):
            self.add(name, container, str(PurePosixPath(name).parent), data)
            return
        if depth >= self.max_depth:
            self.errors.append({"name": name, "reason": "maximum nested-container depth reached"})
            return
        if kind == "zip":
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    for item in archive.infolist():
                        mode = (item.external_attr >> 16) & 0xFFFF
                        if item.is_dir() or item.file_size > self.max_member or not safe_member(item.filename, mode):
                            continue
                        self.archive_bytes += item.file_size
                        if self.archive_bytes > self.max_total:
                            self.errors.append({"name": name, "reason": "total archive-member byte cap exceeded"})
                            break
                        with archive.open(item) as stream:
                            child = stream.read(self.max_member + 1)
                        if len(child) > self.max_member:
                            self.errors.append({"name": item.filename, "reason": "decompressed ZIP member exceeds size cap"})
                            continue
                        child_name = f"{name}!/{item.filename}"
                        if Path(item.filename).suffix.casefold() in (".spl", ".shd"):
                            self.add(item.filename, container, str(PurePosixPath(item.filename).parent), child)
                        elif magic(child) in ("zip", "tar", "gzip"):
                            self.walk_bytes(child_name, child_name, child, depth + 1)
                        else:
                            self.add(item.filename, container, str(PurePosixPath(item.filename).parent), child)
            except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
                self.errors.append({"name": name, "reason": str(exc)})
        elif kind == "tar":
            try:
                with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
                    for item in archive.getmembers():
                        if not item.isfile() or item.size > self.max_member or not safe_member(item.name, item.mode):
                            continue
                        self.archive_bytes += item.size
                        if self.archive_bytes > self.max_total:
                            self.errors.append({"name": name, "reason": "total archive-member byte cap exceeded"})
                            break
                        stream = archive.extractfile(item)
                        if stream is None:
                            continue
                        child = stream.read(self.max_member + 1)
                        if len(child) > self.max_member:
                            self.errors.append({"name": item.name, "reason": "decompressed TAR member exceeds size cap"})
                            continue
                        child_name = f"{name}!/{item.name}"
                        if Path(item.name).suffix.casefold() in (".spl", ".shd"):
                            self.add(item.name, container, str(PurePosixPath(item.name).parent), child)
                        elif magic(child) in ("zip", "tar", "gzip"):
                            self.walk_bytes(child_name, child_name, child, depth + 1)
                        else:
                            self.add(item.name, container, str(PurePosixPath(item.name).parent), child)
            except (tarfile.TarError, OSError) as exc:
                self.errors.append({"name": name, "reason": str(exc)})
        elif kind == "gzip":
            try:
                with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
                    child = stream.read(self.max_member + 1)
                if len(child) > self.max_member:
                    raise ValueError("GZIP payload exceeds member-size cap")
                self.archive_bytes += len(child)
                if self.archive_bytes > self.max_total:
                    raise ValueError("total archive-member byte cap exceeded")
                child_name = f"{name}!/<gzip-payload>"
                self.walk_bytes(child_name, child_name, child, depth + 1)
            except (OSError, EOFError, ValueError) as exc:
                self.errors.append({"name": name, "reason": str(exc)})

    def walk_path(self, source):
        source = Path(source)
        if source.is_symlink():
            self.errors.append({"name": str(source), "reason": "source symlink not followed"})
            return
        if source.is_dir():
            for base, directories, files in os.walk(source, followlinks=False):
                directories[:] = [d for d in directories if not (Path(base) / d).is_symlink()]
                for filename in files:
                    path = Path(base) / filename
                    if path.is_symlink():
                        continue
                    if path.suffix.casefold() in (".spl", ".shd"):
                        self.add(str(path), "directory", str(path.parent.relative_to(source)), path.read_bytes())
                    elif path.suffix.casefold() in (".zip", ".tar", ".tgz", ".gz"):
                        relative = path.relative_to(source).as_posix()
                        self.walk_bytes(relative, relative, path.read_bytes(), 0)
        else:
            data = source.read_bytes()
            if magic(data) in ("zip", "tar", "gzip"):
                self.walk_bytes(source.name, source.name, data, 0)
            else:
                self.add(source.name, "single-file", ".", data)

def pair_members(members):
    groups = defaultdict(lambda: {"SPL": [], "SHD": []})
    for member in members:
        key = (member["container"], member["parent"], member["normalized_stem"])
        groups[key][member["ext"]].append(member)
    pairs, unpaired, ambiguous = [], [], []
    for key, group in sorted(groups.items()):
        if group["SPL"] and group["SHD"]:
            if len(group["SPL"]) == 1 and len(group["SHD"]) == 1:
                spl, shd = group["SPL"][0], group["SHD"][0]
                job_hits = sorted({
                    hit["pattern"].split(":", 1)[1]
                    for hit in shd["hits"]
                    if hit["pattern"].startswith(("job:", "job-utf16:"))
                })
                payload_hits = [
                    hit for hit in spl["hits"]
                    if hit["pattern"].startswith("PS-261003-")
                    and (":raw" in hit["pattern"] or ":hex" in hit["pattern"])
                ]
                pairs.append({
                    "container": key[0], "parent": key[1], "normalized_stem": key[2],
                    "spl": spl, "shd": shd, "job_id_strings_in_shd": job_hits,
                    "spl_payload_hits": payload_hits,
                    "pairing_basis": "exact same container + parent + normalized filename stem; not proof of job identity",
                })
            else:
                ambiguous.append({"key": key, "spl": group["SPL"], "shd": group["SHD"]})
        else:
            unpaired.extend(group["SPL"] + group["SHD"])
    return pairs, unpaired, ambiguous

def self_test():
    inner = io.BytesIO()
    payload = bytes.fromhex("A9A9DC5731A5E2AE879C47215C2559D5")
    job = b"PS-261003-0417"
    with zipfile.ZipFile(inner, "w") as archive:
        archive.writestr("sub/0417.SPL", b"X" + payload + b"Y" + payload.hex().upper().encode())
        archive.writestr("sub/0417.SHD", job + job.decode().encode("utf-16le"))
    outer = io.BytesIO()
    with zipfile.ZipFile(outer, "w") as archive:
        archive.writestr("spool/0007.SPL", payload)
        archive.writestr("spool/0007.SHD", job)
        archive.writestr("other/0007.SPL", b"other")
        archive.writestr("other/0007.SHD", b"other")
        archive.writestr("spool/0008.SPL", b"unpaired")
        archive.writestr("spool/0009.SHD", b"unpaired")
        archive.writestr("nested.zip", inner.getvalue())
    patterns = [
        ("job:" + job.decode(), job),
        ("job-utf16:" + job.decode(), job.decode().encode("utf-16le")),
        ("target:raw", payload),
        ("target:hex", payload.hex().upper().encode()),
    ]
    intake = Intake(patterns)
    intake.walk_bytes("test.zip", "test.zip", outer.getvalue())
    pairs, unpaired, ambiguous = pair_members(intake.members)
    assert len(pairs) == 3 and len(unpaired) == 2 and not ambiguous
    assert any(any(hit["pattern"] == "target:raw" for hit in pair["spl"]["hits"]) for pair in pairs)
    assert any("PS-261003-0417" in pair["job_id_strings_in_shd"] for pair in pairs)
    return {"pairs": len(pairs), "unpaired": len(unpaired), "ambiguous": len(ambiguous), "passed": True}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="authorized native spool directory, archive, or single SPL/SHD file")
    parser.add_argument("--evidence-root", type=Path, default=Path("resources/evidence"),
                        help="extracted official evidence directory; acceptance.json must be in its parent")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"synthetic_test": self_test()}, indent=2))
        return
    if not args.source:
        parser.error("--source is required unless --self-test is used")
    payloads, mask, nonce = read_evidence(args.evidence_root)
    patterns, jobs = make_patterns(payloads, mask, nonce)
    intake = Intake(patterns)
    intake.walk_path(args.source)
    pairs, unpaired, ambiguous = pair_members(intake.members)
    print(json.dumps({
        "source": str(args.source),
        "source_job_ids": jobs,
        "members_scanned": len(intake.members),
        "spl_shd_pairs": pairs,
        "unpaired_members": unpaired,
        "ambiguous_groups": ambiguous,
        "errors": intake.errors,
        "total_spool_member_bytes_scanned": intake.spool_bytes,
        "total_archive_member_bytes_scanned": intake.archive_bytes,
        "limitations": [
            "pairing is filename/container metadata only; SHD offsets are not decoded",
            "job identity is reported only when literal ASCII/UTF-16LE job ID text is present in SHD",
            "payload hits are exact byte or hex-string occurrences; no transform or decryption is attempted",
        ],
    }, indent=2))

if __name__ == "__main__":
    main()
