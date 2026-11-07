"""SFT for the shared p951 source-root contract."""
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "agents" / "agent49"))
import k04_p951_symbolic_basis as mt  # noqa: E402


def main() -> None:
    repo_rows, repo_selected = mt.packets(REPO_ROOT)
    resources_rows, resources_selected = mt.packets(REPO_ROOT / "resources")
    assert repo_selected == resources_selected == 129
    assert repo_rows == resources_rows
    assert len(repo_rows) == 133
    assert sum(bool(row) for row in repo_rows) == 132
    print(
        "PASS: repository-root and resources-root calls resolve the same "
        f"133-row source (selected index {repo_selected}, 132 intact payloads)"
    )


if __name__ == "__main__":
    main()
