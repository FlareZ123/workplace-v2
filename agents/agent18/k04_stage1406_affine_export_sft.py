"""Export ten genuinely new K04 stage1406 33-bit affine cosets, with source checks.

Reuses Agent48's original-source neighbor-stage gate; the output is consumed by
Agent18's minimally adapted Agent1 C/OpenSSL full SHA256 checker.
Invocation: python agents/agent18/k04_stage1406_affine_export_sft.py resources OUTPUT
"""
from pathlib import Path
import hashlib
import os
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "agent48"))
from k04_k02_neighbor_stage_cosets_sft import run


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: export_sft.py ORIGINAL_RESOURCES OUTPUT")
    models = run(Path(sys.argv[1]))
    new = [m for m in models if m["stage"] == 1406]
    older = [m for m in models if m["stage"] in (1178, 1405)]
    assert len(new) == 10 and len(older) == 32
    assert len({m["base"][-16:] for m in new + older}) == 42
    delta = new[0]["deltas"]
    assert len(delta) == 33
    assert all(len(m["base"]) == 32 and m["deltas"] == delta for m in new)
    assert all(len(d) == 32 and int(d[16:], 16) == 0 for d in delta)
    data = ("\n".join([m["base"] for m in new] + delta) + "\n").encode("ascii")
    destination = Path(sys.argv[2])
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock_path = destination.with_name(destination.name + ".lock")
    lock_path.touch(exist_ok=False)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=destination.parent, prefix=destination.name + ".",
            suffix=".part", delete=False,
        ) as temp:
            temp_path = Path(temp.name)
            temp.write(data)
            temp.flush()
            os.fsync(temp.fileno())
        os.replace(temp_path, destination)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
        lock_path.unlink()
    assert destination.read_bytes() == data
    print(
        "STAGE1406_DATA_VERIFIED modes=10 basis=33 "
        "new_candidates=85899345920 sha256=" + hashlib.sha256(data).hexdigest()
    )


if __name__ == "__main__":
    main()
