"""Reproduce missing N13 ordered-subsequence plus two N20 literal-cue lengths.

The original Agent11 SFT has already covered retention lengths 4..12.
This wrapper covers 0..3, 13..21, and 22 using the same exact editor;
it never modifies the shared original Agent11 SFT or historical evidence.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "agents" / "agent11" / "k08_n13_two_cue_condensation_sft.cpp"
source = ORIGINAL.read_text(encoding="utf-8")
base = {
    "middle": (
        "if(count<13||count>21)continue;",
        'std::vector<const char*> plant_words={"at","the","end","of","the","night","the","mugs","stood","beside","the","window","and"};',
        "if(lo<=8191 && hi>8191 && plant_hits==0)",
        "complete_assignments=1051892512",
    ),
    "ends": (
        "if(count>3&&count<22)continue;",
        'std::vector<const char*> plant_words={"at","the","end"};',
        "if(lo<=7 && hi>7 && plant_hits==0)",
        "complete_assignments=137032",
    ),
}
reference = {
    'if(count<4||count>12)continue;': 0,
    'std::vector<const char*> plant_words={"at","the","end","of"};': 1,
    'if(lo<=15 && hi>15 && plant_hits==0)': 2,
}
for mode, (length_gate, plant, plant_gate, expected) in base.items():
    modified = source
    for old, offset in reference.items():
        assert modified.count(old) == 1, old
        modified = modified.replace(old, (length_gate, plant, plant_gate)[offset])
    with TemporaryDirectory(prefix=f"h17-n13-{mode}-") as temp:
        binary = Path(temp) / "n13-source-cues"
        subprocess.run(
            ["c++", "-x", "c++", "-std=c++17", "-O3",
             "-Wno-deprecated-declarations", "-", "-lcrypto", "-o", str(binary)],
            input=modified, text=True, check=True,
        )
        run = subprocess.run(
            [str(binary), str(ROOT / "resources"), "0", str(1 << 22)],
            text=True, capture_output=True,
        )
        print(f"MODE={mode}")
        print(run.stdout, end="")
        print(run.stderr, end="")
        assert run.returncode in (0, 1), run.returncode
        assert expected in run.stdout
        assert "synthetic_positive=" in run.stdout
