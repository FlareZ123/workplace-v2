"""Audit all completed K04 interior five-byte burst shards, without rehashing.

Input: directory of per-shard text outputs downloaded as GitHub Actions artifacts.
Rejects missing/duplicate shard, incomplete coverage, wrong positive controls,
and any unexpected original SHA256 commitment hit.
"""
import pathlib
import re
import sys

LOG_RE = re.compile(
    r"^INTERIOR_SHARD_COMPLETE shard=(\d+) windows=(\d+) checks=(\d+) "
    r"original_hits=(\d+) planted_hits=(\d+)$",
    re.MULTILINE,
)


def main() -> None:
    root = pathlib.Path(sys.argv[1])
    files = sorted(root.glob("shard-*.txt"))
    data = {}
    for file in files:
        body = file.read_text(encoding="utf-8")
        matches = LOG_RE.findall(body)
        if len(matches) != 1:
            raise RuntimeError(f"{file}: missing/duplicated complete marker")
        shard, windows, checks, original, positive = matches[0]
        shard, windows, checks, original, positive = map(int, (shard, windows, checks, original, positive))
        if file.name != f"shard-{shard}.txt":
            raise RuntimeError(f"{file}: shard/file mismatch")
        if shard in data:
            raise RuntimeError(f"duplicate shard {shard}")
        if checks != 42949672960 or windows != 10:
            raise RuntimeError(f"shard {shard}: incomplete calculation ({checks})")
        if positive != 10:
            raise RuntimeError(f"shard {shard}: wrong planted-positive count {positive}")
        data[shard] = original
    missing = sorted(set(range(256)) - set(data))
    if missing:
        raise RuntimeError(f"missing {len(missing)} shards: {missing[:20]}")
    total = sum(data.values())
    print(f"AUDIT_COMPLETE shards={len(data)} full_sha256_checks={256 * 42949672960} original_hits={total} planted_hits=2560")
    if total:
        raise RuntimeError(f"ORIGINAL_K04_MATCH found in {[k for k,v in data.items() if v]}")


if __name__ == "__main__":
    main()
