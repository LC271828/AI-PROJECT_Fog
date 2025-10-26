"""
Guardrail script: fail if any file in src/ or tests/ imports from experiments/.

Policy:
- Do NOT import from experiments in src/ or tests/.

Behavior:
- Scans Python files under ./src and ./tests.
- Flags lines like:
    - from experiments import ...
    - from experiments.something import ...
    - import experiments
    - import experiments.something
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    re.compile(r"^\s*from\s+experiments(\.|\s|$)"),
    re.compile(r"^\s*import\s+experiments(\.|\s|$)"),
]


def scan_dir(dir_path: Path) -> list[tuple[Path, int, str]]:
    violations: list[tuple[Path, int, str]] = []
    if not dir_path.exists():
        return violations
    for py in dir_path.rglob("*.py"):
        try:
            text = py.read_text(encoding="utf-8")
        except Exception:
            # Fallback binary read to avoid encoding crashes
            try:
                text = py.read_bytes().decode("utf-8", errors="ignore")
            except Exception:
                continue
        for i, line in enumerate(text.splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            for pat in PATTERNS:
                if pat.search(line):
                    violations.append((py.relative_to(ROOT), i, line.rstrip()))
                    break
    return violations


def main() -> int:
    targets = [ROOT / "src", ROOT / "tests"]
    all_violations: list[tuple[Path, int, str]] = []
    for t in targets:
        all_violations.extend(scan_dir(t))

    if all_violations:
        print("Policy violation: imports from 'experiments' found in src/ or tests/\n")
        for path, lineno, line in all_violations:
            print(f"- {path}:{lineno}: {line}")
        print("\nPlease remove imports from 'experiments' in production code or tests.")
        return 2

    print("Guardrail passed: no 'experiments' imports detected in src/ or tests/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
