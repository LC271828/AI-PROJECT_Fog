"""
A lightweight pytest plugin that prints a rich terminal summary using the
'rich' library. Enabled via '--rich' and loaded by default from pytest.ini
with '-p tests.pytest_rich_report --rich'.

If 'rich' is unavailable, the plugin becomes a no-op and defers to pytest's
standard output.
"""

from typing import List, Tuple

import pytest

# Store (nodeid, duration, outcome) for call-phase reports
_DURATIONS: List[Tuple[str, float, str]] = []


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("rich-report")
    group.addoption(
        "--rich",
        action="store_true",
        default=False,
        help="Enable a rich (pretty) terminal summary using the 'rich' library.",
    )


def pytest_configure(config: pytest.Config) -> None:
    # No heavy setup required; option gate checked in terminal_summary
    pass


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        # Collect durations for top-N slow tests table
        _DURATIONS.append((rep.nodeid, getattr(rep, "duration", 0.0), rep.outcome))


def pytest_terminal_summary(terminalreporter, exitstatus):
    config = terminalreporter.config
    if not config.getoption("--rich"):
        return  # respect opt-in

    try:
        from rich.console import Console  # type: ignore
        from rich.table import Table  # type: ignore
        from rich.panel import Panel  # type: ignore
        from rich import box  # type: ignore
    except Exception:  # pragma: no cover
        return  # 'rich' not installed; degrade gracefully

    console = Console(force_terminal=True)

    # Build counts by outcome
    stats = terminalreporter.stats
    outcomes = [
        ("passed", "green"),
        ("failed", "red"),
        ("error", "bold red"),
        ("skipped", "yellow"),
        ("xfailed", "cyan"),
        ("xpassed", "cyan"),
        ("warnings", "magenta"),
    ]
    total_collected = getattr(terminalreporter, "_numcollected", 0)

    table = Table(title="Test summary", box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Outcome", justify="left")
    table.add_column("Count", justify="right")

    for key, style in outcomes:
        count = len(stats.get(key, []))
        if count:
            table.add_row(f"[{style}]{key}[/]", f"{count}")

    # Show total even if zero
    table.add_row("total", f"{total_collected}")

    console.print(Panel.fit(table, title="Pytest", border_style="blue"))

    # Top-N slow tests
    if _DURATIONS:
        N = 5
        slow = sorted(_DURATIONS, key=lambda t: t[1], reverse=True)[:N]
        dt = Table(title=f"Top {N} slow tests", box=box.MINIMAL)
        dt.add_column("Duration (s)", justify="right")
        dt.add_column("Outcome", justify="left")
        dt.add_column("Test", justify="left")
        for nodeid, dur, outcome in slow:
            dt.add_row(f"{dur:.3f}", outcome.upper(), nodeid)
        console.print(dt)
