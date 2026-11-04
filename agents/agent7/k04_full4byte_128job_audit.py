"""Audit the 128-shard original K04 four-byte search after its completion.

Uses GitHub's documented read-only workflow-job and job-log REST endpoints.
No access to or mutation of the original H-17 evidence or acceptance.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from filelock import FileLock

REPOSITORY = "FlareZ123/workplace-v2"
RUN_ID = 41838591961
N_SHARDS = 128
N_EXPECTED_SUPPORTS = 1713
FULL_CHECKS_PER_SUPPORT = 1 << 32
OUTPUT = Path(__file__).with_name("k04_full4byte_reconciled_41838591961.json")
API = "https://api.github.com/repos/" + REPOSITORY
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer " + os.environ["GITHUB_TOKEN"],
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "H17-fourbyte-audit",
}
JOB_NAME = re.compile(r"full-fourbyte \((\d+)\)")
PER_SUPPORT = re.compile(
    r"QUARTET_DONE q=(\d+) indexes=(\d+),(\d+),(\d+),(\d+) "
    r"complete_checks=(\d+) original_hits=(\d+) plant_hits=(\d+)"
)
SHARD_END = re.compile(
    r"SHARD_COMPLETE shard=(\d+) quartets=(\d+) full_sha256_checks=(\d+) "
    r"original_hits=(\d+) plants=(\d+)"
)
MATCH = re.compile(r"ORIGINAL_K04_MATCH\s+[^\n]*")


def request_bytes(route: str) -> bytes:
    req = Request(API + route, headers=HEADERS)
    with urlopen(req, timeout=90) as response:
        return response.read()


def get_jobs() -> list[dict]:
    jobs = []
    for page in range(1, 4):
        payload = json.loads(
            request_bytes(f"/actions/runs/{RUN_ID}/jobs?per_page=100&page={page}")
        )
        jobs.extend(payload["jobs"])
        if len(jobs) >= payload["total_count"]:
            break
    if len(jobs) != N_SHARDS:
        raise RuntimeError(f"Expected {N_SHARDS} jobs, retrieved {len(jobs)}")
    by_shard: dict[int, dict] = {}
    for job in jobs:
        m = JOB_NAME.fullmatch(job["name"])
        if not m:
            raise RuntimeError(f"Unrecognized job name: {job['name']}")
        shard = int(m.group(1))
        if shard in by_shard or not 0 <= shard < N_SHARDS:
            raise RuntimeError(f"Repeated or invalid shard: {shard}")
        by_shard[shard] = job
    if len(by_shard) != N_SHARDS:
        raise RuntimeError("Missing shard")
    return [by_shard[i] for i in range(N_SHARDS)]


def expected_supports() -> list[tuple[int, int, int, int]]:
    positions = []
    for a in range(16):
        for b in range(a + 1, 16):
            for c in range(b + 1, 16):
                for d in range(c + 1, 16):
                    if a == 0 and b == 1:
                        continue
                    if d == a + 3:
                        continue
                    if a % 4 == b % 4 == c % 4 == d % 4:
                        continue
                    positions.append((a, b, c, d))
    if len(positions) != N_EXPECTED_SUPPORTS:
        raise RuntimeError(f"Expected 1713 supports; got {len(positions)}")
    return positions


def main() -> int:
    jobs = get_jobs()
    expected = expected_supports()
    status_counts: dict[str, int] = {}
    for job in jobs:
        status = job["conclusion"] or job["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    print("128_JOB_STATUS", json.dumps(status_counts), flush=True)
    if "--status-only" in sys.argv:
        print("GITHUB_ACTIONS_API_AND_128_SHARD_INDEX_PASS", flush=True)
        return 0

    if any(job["status"] != "completed" for job in jobs):
        raise RuntimeError("Full 128-job run not yet completed; defer audit")

    records = []
    errors = []
    hits = []
    observed_supports: set[int] = set()
    complete_checks = 0
    for shard, job in enumerate(jobs):
        raw = request_bytes(f"/actions/jobs/{job['id']}/logs").decode("utf-8", "replace")
        rows = PER_SUPPORT.findall(raw)
        endings = SHARD_END.findall(raw)
        matches = MATCH.findall(raw)
        hits.extend([{"shard": shard, "job_id": job["id"], "record": text}
                     for text in matches])
        expected_indices = set(range(shard, N_EXPECTED_SUPPORTS, N_SHARDS))
        actual_indices = set()
        for values in rows:
            q, a, b, c, d, count, orig, planted = map(int, values)
            if q in observed_supports:
                errors.append(f"Duplicate global support q={q}")
            if q >= N_EXPECTED_SUPPORTS or (a, b, c, d) != expected[q]:
                errors.append(f"Unexpected fourbyte support q={q}")
            if count != FULL_CHECKS_PER_SUPPORT or planted != 1:
                errors.append(f"Support q={q} wrong complete/planted counts")
            if orig:
                errors.append(f"Original K04 hit in support q={q}")
            observed_supports.add(q)
            actual_indices.add(q)
            complete_checks += count

        if actual_indices != expected_indices:
            errors.append(f"Shard {shard} missing/unexpected q={sorted(expected_indices ^ actual_indices)}")
        if len(endings) != 1:
            errors.append(f"Shard {shard} has {len(endings)} complete markers")
        else:
            completed_shard, supports, checks, original, planted = map(int, endings[0])
            if (completed_shard != shard or supports != len(expected_indices)
                    or checks != supports * FULL_CHECKS_PER_SUPPORT
                    or original or planted != supports):
                errors.append(f"Shard {shard} ending counters inconsistent: {endings[0]}")

        if job["conclusion"] != "success":
            errors.append(f"Shard {shard} job {job['id']} conclusion={job['conclusion']}")
        records.append({"shard": shard, "job_id": job["id"],
                        "job_conclusion": job["conclusion"],
                        "supports": len(rows),
                        "full_checks": len(rows) * FULL_CHECKS_PER_SUPPORT,
                        "original_hits_logged": len(matches)})
        if (shard + 1) % 16 == 0:
            print("AUDIT_PROGRESS", shard + 1, "supports", len(observed_supports),
                  "full_checks", complete_checks, "errors", len(errors), flush=True)

    if len(observed_supports) != N_EXPECTED_SUPPORTS:
        errors.append(f"Only {len(observed_supports)} distinct supports")
    if complete_checks != N_EXPECTED_SUPPORTS * FULL_CHECKS_PER_SUPPORT:
        errors.append(f"Incorrect total checks {complete_checks}")
    report = {
        "repo": REPOSITORY, "run_id": RUN_ID,
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "expected_supports": N_EXPECTED_SUPPORTS,
        "observed_supports": len(observed_supports),
        "expected_checks": N_EXPECTED_SUPPORTS * FULL_CHECKS_PER_SUPPORT,
        "observed_checks": complete_checks,
        "status_counts": status_counts, "errors": errors,
        "original_k04_matches": hits, "shards": records,
        "full_frontier_pass": not errors and not hits,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(OUTPUT) + ".lock"):
        tmp = OUTPUT.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, OUTPUT)
    print("FINAL_128_SHARD_AUDIT", json.dumps(
        {k: report[k] for k in (
            "expected_supports", "observed_supports", "expected_checks",
            "observed_checks", "status_counts", "errors",
            "original_k04_matches", "full_frontier_pass"
        )}), flush=True)
    return 0 if report["full_frontier_pass"] else 3


if __name__ == "__main__":
    sys.exit(main())
