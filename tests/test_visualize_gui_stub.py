"""GUI draw tests using a pygame stub so we don't need the real pygame.

We validate that:
- draw_frame runs without errors when pygame is unavailable (via stub)
- In no-fog mode (agent.full_map=True), the function overlays the plan and the
  visited path (metrics.path_taken) using screen.blit for each expected cell
  (excluding the agent's current cell and plan[0]).

These are smoke-level tests focusing on side effects (number of blits) rather
than pixel colors.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import importlib


class _Surface:
    def __init__(self, size, flags=None):
        self.size = size
        self.flags = flags
        self.blits: list[tuple[int, int]] = []
        self.fills: list[tuple] = []
        self.alpha = None

    def fill(self, color):
        self.fills.append(color)

    def set_alpha(self, a):
        self.alpha = a

    def blit(self, other, pos):
        self.blits.append(tuple(pos))


class _Draw:
    def __init__(self):
        self.rect_calls = []
        self.circle_calls = []
        self.line_calls = []

    def rect(self, screen, color, rect, width=0):
        self.rect_calls.append((color, rect, width))

    def circle(self, screen, color, center, radius):
        self.circle_calls.append((color, center, radius))

    def line(self, screen, color, start, end):
        self.line_calls.append((color, start, end))


class PygameStub:
    SRCALPHA = object()

    def __init__(self):
        self.draw = _Draw()

    def Rect(self, x, y, w, h):
        # A simple tuple is fine for our tests
        return (x, y, w, h)

    def Surface(self, size, flags=None):
        return _Surface(size, flags)


def test_draw_frame_no_fog_overlays_plan_and_path(monkeypatch):
    # Import grid and visualize after setting up monkeypatch for pygame
    from src.grid import Grid
    import src.visualize as V

    # Monkeypatch _require_pygame in visualize to return our stub
    stub = PygameStub()
    monkeypatch.setattr(V, "_require_pygame", lambda: stub, raising=True)

    # Build a tiny map and agent stub
    repo_root = Path(__file__).resolve().parents[1]
    demo_map = repo_root / "maps" / "open_room.csv"
    g = Grid.from_csv(demo_map)

    # Agent stub: no fog, simple plan and path
    current = (0, 0)
    plan = [(0, 0), (0, 1), (0, 2)]
    path_taken = [(0, 0), (1, 0), (2, 0)]
    metrics = SimpleNamespace(path_taken=path_taken)
    agent = SimpleNamespace(full_map=True, current=current, current_plan=plan, metrics=metrics)

    # Screen surface
    screen = stub.Surface((g.width * 4, g.height * 4))

    # Call
    V.draw_frame(screen, g, agent, cell_size=4, show_grid=True)

    # Expect a blit for each plan cell except index 0, and for each path cell except the current cell
    expected_plan_blits = max(0, len(plan) - 1)
    expected_path_blits = len(path_taken) - (1 if current in path_taken else 0)

    # We drew two overlay passes: path first, then plan; total blits should be their sum
    assert len(screen.blits) >= expected_plan_blits + expected_path_blits

    # Sanity: agent circle drawn once
    assert len(stub.draw.circle_calls) == 1
