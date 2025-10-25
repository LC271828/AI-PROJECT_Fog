"""Visualization (API guide for Thomz)

Goal (TEAM_API-compliant)
- Provide a minimal pygame visualizer that can render the Grid with fog-of-war,
	the OnlineAgent, and the current plan.
- It should not change Grid or Agent state except for calling ``agent.step()``.
- Keep the visualizer optional (headless-first). Import pygame lazily.

Inputs (from TEAM_API)
- Grid
	- fields: width, height, grid (2D symbols), start, goal
	- fog: visible (2D bool mask); reveal handled by Grid.reveal_from() called by Agent
	- helpers: tile_at(r,c), is_visible(r,c), neighbors4(r,c)
- OnlineAgent
	- fields: current (position), current_plan (list[Coord], optional)
	- methods: step() -> bool (False when done), run(max_steps) -> Metrics
	- Metrics includes steps, replans, nodes_expanded (when using with-stats), cost, runtime

Shape contract (simple)
- One cell maps to a fixed pixel size (e.g., 24px). Window size = (grid.width * cell, grid.height * cell).
- Draw order per tile: base floor/wall, start/goal markers, plan overlay, agent overlay.
- Fog: if not visible -> draw dark cell ('fog color'); visible walls use a different color.

Controls (suggested)
- ESC / window close: exit
- Space: pause/resume stepping
- N: single-step when paused
- +/-: change speed (FPS)

Implementation roadmap (TODOs)
1) Init
	 - TODO(Thomz): import pygame inside functions (lazy) so CI without pygame is fine.
	 - TODO(Thomz): compute window size from grid dimensions and cell_size.
	 - TODO(Thomz): create display surface; set caption.
2) Colors & sizing
	 - TODO(Thomz): define colors for fog, free, wall, start, goal, agent, plan.
	 - TODO(Thomz): optional grid lines.
3) Draw helpers
	 - TODO(Thomz): draw_tile(screen, r, c, grid, cell_size) -> None.
	 - TODO(Thomz): overlay_plan(screen, plan, cell_size) -> None (draw '*' or tinted rects).
	 - TODO(Thomz): overlay_agent(screen, pos, cell_size) -> None (draw '@' or small circle).
4) Loop
	 - TODO(Thomz): handle events (QUIT, ESC, Space, N, +/-).
	 - TODO(Thomz): when not paused, call agent.step(); if False, stop.
	 - TODO(Thomz): redraw every frame; cap with clock.tick(fps).
	 - TODO(Thomz): HUD (optional): text for steps, replans, nodes_expanded, cost.
5) Stats (optional)
	 - If the search passed into the agent is a with-stats wrapper (see src.search),
		 Metrics will include nodes_expanded/runtime; show them on HUD if present.

Usage examples (from repo root, optional)
"""

# Thomz: text-only renderer exists at examples/visualize_text.py; use that for quick tests.
# The stubs below sketch a pygame API without enforcing pygame at import-time.


def draw_frame(screen, grid, agent, cell_size=24, show_grid=True):
		"""Draw a single frame onto an existing pygame screen.

		Contract
		- Does not flip the display; caller should call pygame.display.flip() after drawing.
		- Uses Grid visibility; Agent is only used for current position and plan.
		- No side effects to Grid/Agent beyond reading fields.

		TODO(Thomz): implement with pygame; placeholder is a no-op to keep CI green.
		"""
		# NOTE: Keep imports local to avoid ImportError in environments without pygame
		try:
			import importlib
			pygame = importlib.import_module("pygame")  # type: ignore[assignment]
		except Exception:
			return  # silently no-op if pygame missing

		# TODO(Thomz): fill background
		# TODO(Thomz): loop over r,c -> draw visible/free/wall/fog
		# TODO(Thomz): draw start/goal markers
		# TODO(Thomz): overlay current plan (agent.current_plan)
		# TODO(Thomz): overlay agent position (agent.current)
		# TODO(Thomz): optional grid lines for clarity
		return


def visualize(agent, grid, cell_size=24, fps=10):
		"""Minimal pygame visualization loop.

		Parameters
		- agent: OnlineAgent (TEAM_API)
		- grid: Grid (TEAM_API)
		- cell_size: pixels per tile
		- fps: target frames per second

		Returns
		- Metrics from agent.run-like usage, or None if terminated early. For simplicity
			this function will step the agent one move per frame when running.

		TODO(Thomz): implement with pygame; placeholder returns None to keep optional.
		"""
		try:
			import importlib
			pygame = importlib.import_module("pygame")  # type: ignore[assignment]
		except Exception:
				# pygame not installed; leave gracefully
				return None

		# TODO(Thomz): pygame.init(); clock = pygame.time.Clock()
		# TODO(Thomz): screen = pygame.display.set_mode((grid.width*cell_size, grid.height*cell_size))
		# TODO(Thomz): pygame.display.set_caption("Fog Maze")
		# TODO(Thomz): paused = False
		# TODO(Thomz): main loop: handle events, step when not paused, draw_frame, flip, clock.tick(fps)
		# TODO(Thomz): on finish, return agent.metrics
		# TODO(Thomz): pygame.quit()
		return None
