import re
from pathlib import Path

import pytest


def _run_main(argv):
    from src import main as mod
    return mod.main(argv)


def _parse_metrics(out: str):
    """Parse metric lines printed by CLI into a dict of strings.
    Expected lines include keys like 'Steps:', 'Nodes expanded:', 'Runtime (s):'.
    """
    result = {}
    for line in out.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            result[k.strip()] = v.strip()
    return result


@pytest.mark.parametrize("with_stats", [False, True])
def test_cli_runs_and_prints_metrics(capsys, with_stats):
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "demo.csv"

    argv = [
        "--map",
        str(demo_map),
        "--algo",
        "astar",
        "--no-fog",
    ]
    if with_stats:
        argv.append("--with-stats")

    rc = _run_main(argv)
    assert rc == 0

    captured = capsys.readouterr().out
    metrics = _parse_metrics(captured)

    # Always printed
    assert "Start" in metrics and "Goal" in metrics
    assert "Steps" in metrics and "Cost" in metrics
    assert "Nodes expanded" in metrics and "Runtime (s)" in metrics

    # Validate numeric shape
    steps = int(metrics["Steps"])
    cost = int(metrics["Cost"])
    nodes = int(metrics["Nodes expanded"])
    runtime = float(metrics["Runtime (s)"])

    assert steps >= 0 and cost >= 0
    if with_stats:
        # with-stats should collect some expansions and runtime >= 0
        assert nodes >= 0
        assert runtime >= 0.0
    else:
        # without stats it's fine to be zero; just check types
        assert isinstance(nodes, int)
        assert isinstance(runtime, float)
