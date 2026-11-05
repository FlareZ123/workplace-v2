"""Audit all completed K04 first-five prefix shards, without rehashing.

Input: directory of per-shard text outputs downloaded as GitHub Actions artifacts.
Rejects missing/duplicate shard, incomplete coverage, wrong positive controls,
and any unexpected original SHA256 commitment hit.
"""
import pathlib
import re
import sys

LOG_RE = re.compile(
    r"^SHARD_COMPLETE shard=(\d+) full_sha256_checks=(\d+) "
    r"original_hits=(\d+) planted_hits=(\d+) elapsed=([0-9.]+) smoke=(\d+)$",
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
        shard, checks, original, positive, _, smoke = matches[0]
        shard, checks, original, positive, smoke = map(int, (shard, checks, original, positive, smoke))
        if file.name != f"shard-{shard}.txt":
            raise RuntimeError(f"{file}: shard/file mismatch")
        if shard in data:
            raise RuntimeError(f"duplicate shard {shard}")
        if checks != 4294967296 or smoke:
            raise RuntimeError(f"shard {shard}: incomplete calculation ({checks})")
        if positive != int(shard == 95):
            raise RuntimeError(f"shard {shard}: wrong planted-positive count {positive}")
        data[shard] = original
    missing = sorted(set(range(256)) - set(data))
    if missing:
        raise RuntimeError(f"missing {len(missing)} shards: {missing[:20]}")
    total = sum(data.values())
    print(f"AUDIT_COMPLETE shards={len(data)} full_sha256_checks={256 * 4294967296} original_hits={total} planted_hits=1")
    if total:
        raise RuntimeError(f"ORIGINAL_K04_MATCH found in {[k for k,v in data.items() if v]}")


if __name__ == "__main__":
    main()
