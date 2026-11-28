#!/usr/bin/env python3
"""Private, resuming K04 P16/P20 firstpacket state receipts.

Run *only* on authorized local original source outside public CI. This script
records every SAT model from a complete parent, including those which have no
K04 SHA commitment hit. A later cheap reducer may change without repeating
a costly firstpacket SMT inversion. No model, candidate or original source
byte is printed or written into GitHub; receipt files are chmod 0600 under
a preexisting, mode-0700, out-of-repo directory.

UNKNOWN children remain unsealed. Never infer exhaustive absence from a
first state, a timed-out model-blocking query, or a downstream holdout failure.
"""
from __future__ import annotations
import argparse, hashlib, json, os, secrets, stat, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agents.agent37.k04_p16_p20_adaptive_source_local import (
    P12, P16, adaptive_child, read_original, stream, assess_state, escrow_hits,
)

SOURCE_PIN = "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
CIRCUIT = Path(__file__).with_name("k04_p16_p20_adaptive_source_local.py")
MASK64 = (1 << 64) - 1


def private_dir(path: Path) -> Path:
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        raise RuntimeError("Historical source forbidden in CI")
    path = path.expanduser()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise RuntimeError("Symlink in private ledger path")
    p = path.resolve(strict=True)
    if not p.is_dir() or p == ROOT or ROOT in p.parents:
        raise RuntimeError("Private ledger must be an existing out-of-repo directory")
    if stat.S_IMODE(p.stat().st_mode) & 0o077:
        raise PermissionError("Private directory must be mode 0700")
    return p


def metadata(first: tuple[int, int], endian: str, order: str) -> dict:
    actual = first if order == "ab" else tuple(reversed(first))
    first_raw = b"".join(x.to_bytes(8, endian) for x in actual)
    return {
        "schema": "h17-k04-source-first-P16P20-receipt/v1",
        "source_sha256": SOURCE_PIN,
        "first_sha256": hashlib.sha256(first_raw).hexdigest(),
        "serializer": endian + "/" + order,
        "circuit_sha256": hashlib.sha256(CIRCUIT.read_bytes()).hexdigest(),
        "P12": list(P12), "P16": list(P16),
    }


def namespace(meta: dict) -> str:
    return hashlib.sha256(json.dumps(meta, sort_keys=True).encode()).hexdigest()


def receipt_path(root: Path, meta: dict, parent: int) -> Path:
    assert 0 <= parent < 4096
    return root / f"{namespace(meta)}_p{parent:04d}.json"


def validate_record(record: dict, parent: int, first: tuple[int, int]):
    children = record["children"]
    if len(children) != 16 or sorted(x["child"] for x in children) != list(range(16)):
        raise ValueError("Parent receipt must contain exactly 16 P16 children")
    for c in children:
        if c["terminal"] not in ("unknown", "unsat"):
            raise ValueError("Invalid exact model-blocking terminal")
        sub = c["child"]
        for pair in c["states"]:
            if len(pair) != 2 or not all(type(v) == int and 0 <= v <= MASK64 for v in pair):
                raise ValueError("Malformed full 128-bit model")
            a, b = pair
            if stream(a, b, 2) != list(first):
                raise ValueError("Cached model fails whole intact source packet")
            a_parent = sum(((a >> p) & 1) << j for j, p in enumerate(P12))
            a_child = sum(((a >> p) & 1) << j for j, p in enumerate(P16[12:]))
            if (a_parent, a_child) != (parent, sub):
                raise ValueError("Model stored under the wrong exact cube")
    sealed = all(c["terminal"] == "unsat" for c in children)
    if bool(record["sealed"]) != sealed:
        raise ValueError("Receipt seal contradicts child terminal statuses")


def read_receipt(root, meta, parent, first):
    path = receipt_path(root, meta, parent)
    if not path.exists():
        return None
    if path.is_symlink() or stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise PermissionError("Insecure state receipt")
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(fd, "r", encoding="ascii") as f:
        record = json.load(f)
    if record["meta"] != meta or record["parent"] != parent:
        raise ValueError("Receipt source/circuit/view mismatch")
    validate_record(record, parent, first)
    return record


def write_receipt(root, meta, parent, record, first):
    record = {**record, "meta": meta, "parent": parent}
    validate_record(record, parent, first)
    target = receipt_path(root, meta, parent)
    if target.exists():
        previous = read_receipt(root, meta, parent, first)
        if previous["sealed"]:
            raise RuntimeError("Never overwrite a sealed source-state receipt")
        # Replacing an UNKNOWN receipt is intentional; preserve all prior
        # discovered models to avoid discarding useful partial search states.
        prev_children = {c["child"]: c for c in previous["children"]}
        for row in record["children"]:
            old = prev_children[row["child"]]
            row["states"] = sorted({tuple(p) for p in
                                    (row["states"] + old["states"])})
            row["terminal"] = "unsat" if row["terminal"] == "unsat" or
                                   old["terminal"] == "unsat" else "unknown"
        record["sealed"] = all(x["terminal"] == "unsat" for x in record["children"])
        validate_record(record, parent, first)
    temp = root / (".tmp-" + secrets.token_hex(16))
    fd = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY |
                 getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="ascii") as f:
            json.dump(record, f, sort_keys=True)
            f.write("\\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, target)
        directory_fd = os.open(root, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temp.unlink(missing_ok=True)


def solve_parent(first, parent, ms, retry_ms, cap):
    children = []
    for child in range(16):
        states, terminal, details = adaptive_child(first, parent, child,
                                                   ms, retry_ms, cap)
        children.append({
            "child": child, "terminal": terminal,
            "states": [list(x) for x in sorted(set(states))],
            "adaptive": details,
        })
    return {"sealed": all(x["terminal"] == "unsat" for x in children),
            "children": children}


def synthetic():
    # No original source or commitment is opened.
    x = (0xB02543CFB686BB4A, 0xF9DA21F56A996103)
    y = (0xCE695E4122B2739A, 0xFF6DF861F134F29D)
    first = tuple(stream(*x, 2))
    assert tuple(stream(*y, 2)) == first
    parent = sum(((x[0] >> p) & 1) << i for i, p in enumerate(P12))
    record = solve_parent(first, parent, 350, 700, 32)
    assert record["sealed"]
    with tempfile.TemporaryDirectory() as d:
        os.chmod(d, 0o700)
        root = private_dir(Path(d))
        meta = metadata(first, "little", "ab")
        write_receipt(root, meta, parent, record, first)
        copy = read_receipt(root, meta, parent, first)
        states = {tuple(pair) for row in copy["children"] for pair in row["states"]}
        assert states == {x, y}
        assert stat.S_IMODE(receipt_path(root, meta, parent).stat().st_mode) == 0o600
    print(json.dumps({
        "synthetic_only": True, "same_parent_collision_states": 2,
        "both_captured": True, "16_exact_children_sealed": True,
        "private_receipt_0600": True, "original_source_read": False,
    }, sort_keys=True))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--synthetic", action="store_true")
    p.add_argument("--private-dir", type=Path)
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--endian", choices=("little", "big"), default="little")
    p.add_argument("--order", choices=("ab", "ba"), default="ab")
    p.add_argument("--timeout-ms", type=int, default=350)
    p.add_argument("--retry-timeout-ms", type=int, default=700)
    p.add_argument("--max-models", type=int, default=32)
    p.add_argument("--local-hit-escrow", type=Path)
    a = p.parse_args()
    if a.synthetic:
        return synthetic()
    if a.private_dir is None or a.local_hit_escrow is None:
        p.error("Private receipt directory and original-hit escrow are required")
    if not (0 <= a.start < 4096 and 1 <= a.count <= 4096-a.start
            and 100 <= a.timeout_ms <= a.retry_timeout_ms <= 30000
            and 1 <= a.max_models <= 1024):
        p.error("Invalid exact search bounds")
    root = private_dir(a.private_dir)
    escrow = a.local_hit_escrow.resolve()
    if escrow.parent != root:
        p.error("Verified component escrow must be within private receipt directory")
    first, later, mask, target = read_original(a.endian, a.order)
    meta = metadata(first, a.endian, a.order)
    totals = {"parents": 0, "sealed": 0, "open": 0, "states": 0,
              "full_sha_checks": 0, "original_commit_hits": 0,
              "loaded_sealed_from_cache": 0}
    for parent in range(a.start, a.start + a.count):
        saved = read_receipt(root, meta, parent, first)
        if saved and saved["sealed"]:
            record = saved
            totals["loaded_sealed_from_cache"] += 1
        else:
            record = solve_parent(first, parent, a.timeout_ms,
                                  a.retry_timeout_ms, a.max_models)
            write_receipt(root, meta, parent, record, first)
        totals["parents"] += 1
        totals["sealed" if record["sealed"] else "open"] += 1
        models = sorted({tuple(pair) for c in record["children"]
                         for pair in c["states"]})
        totals["states"] += len(models)
        for state in models:
            counts, hits = assess_state(state, mask, target, a.endian,
                                        a.order, 8, 8, later)
            totals["full_sha_checks"] += counts["candidates"]
            totals["original_commit_hits"] += counts["commit_hits"]
            if hits:
                escrow_hits(escrow, hits)
        print(json.dumps({
            "source_private_only": True, "parents_completed": totals["parents"],
            "view": a.endian + "/" + a.order, "aggregates": totals,
            "raw_source_or_model_exposed": False,
        }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
