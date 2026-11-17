"""Reproduce the unscreened 13..21-word N13 retention interval using Agent11's exact two-cue editor.

The original 4..12-word interval and all-22-word endpoint were previously scanned.
This wrapper changes only the selected length band and its planted source control.
It does not modify the shared Agent11 script or any original historical resource.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "agents" / "agent11" / "k08_n13_two_cue_condensation_sft.cpp"
source = ORIGINAL.read_text(encoding="utf-8")

replacements = {
    'if(count<4||count>12)continue;':
        'if(count<13||count>21)continue;',
    'std::vector<const char*> plant_words={"at","the","end","of"};':
        'std::vector<const char*> plant_words={"at","the","end","of","the","night","the","mugs","stood","beside","the","window","and"};',
    'if(lo<=15 && hi>15 && plant_hits==0)':
        'if(lo<=8191 && hi>8191 && plant_hits==0)',
}
for old, new in replacements.items():
    assert source.count(old) == 1, old
    source = source.replace(old, new)

with TemporaryDirectory(prefix="h17-n13-middle-") as temp:
    binary = Path(temp) / "n13-middle"
    subprocess.run(
        ["c++", "-x", "c++", "-std=c++17", "-O3",
         "-Wno-deprecated-declarations", "-", "-lcrypto", "-o", str(binary)],
        input=source, text=True, check=True,
    )
    run = subprocess.run(
        [str(binary), str(ROOT / "resources"), "0", str(1 << 22)],
        text=True, capture_output=True,
    )
    print(run.stdout, end="")
    print(run.stderr, end="")
    assert run.returncode in (0, 1), run.returncode
    assert "complete_assignments=1051892512" in run.stdout
    assert "synthetic_positive=" in run.stdout
