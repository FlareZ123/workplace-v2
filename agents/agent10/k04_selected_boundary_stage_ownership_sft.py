"""H-17 selected-boundary stage ownership for the conditional p951 printer DEST rule."""
from pathlib import Path
import hashlib
import re
from importlib.util import module_from_spec, spec_from_file_location

ROOT = Path(__file__).resolve().parents[2]
model_path = ROOT / "agents/agent49/k04_p951_symbolic_basis.py"
spec = spec_from_file_location("k04_p951_symbolic_basis", model_path)
model = module_from_spec(spec)
spec.loader.exec_module(model)
starts = model.STARTS
raw = (ROOT / "resources/evidence/print/spool-reconstruction.log").read_bytes()
assert hashlib.sha256(raw).hexdigest() == "7d71d8bef7f01596e705ac14e24c5c4352042512b3088125afca40f3841b6083"
rows = [dict(re.findall(r"\b([A-Z]+)=([^ ]+)", s))
        for s in raw.decode().splitlines() if "PAYLOAD=" in s]
assert len(rows) == len(starts) == 133
labels = {0: "store", 1: "desk", 2: "bench", 3: "reject"}
codes = []
for i in range(128, 132):
    q = starts[i]
    next_q = starts[i + 1]
    assert next_q == q + 4, (i, q, next_q)
    copied_word = int.from_bytes(bytes.fromhex(rows[i + 1]["PAYLOAD"][:8]), "little")
    copied_code = copied_word >> 30
    codes.append(copied_code)
    print(
        f"predecessor={i} DEST={rows[i]['DEST']} hidden_dest_stage={q+4} "
        f"next_packet={i+1} first_word={copied_word:08X} "
        f"next_word_top2={copied_code}({labels[copied_code]})"
    )
assert codes == [1, 3, 2, 3]
assert rows[128]["DEST"] == "bench"
print("STAGE_OVERLAP=ALL_FOUR conditional_K04_original_bits=0")
