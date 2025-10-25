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
# IMPORTANT: Pygame is optional. We import it lazily inside functions so that
# importing this module does not require pygame to be installed.

from typing import Optional, List, Tuple, Any
from pathlib import Path
from src.grid import Grid
from src.agent import OnlineAgent
from src.search import ALGORITHMS_NEIGHBORS as SEARCH_ALGOS


def _require_pygame():
	"""Import pygame lazily and return the module.

	Raises a clear, user-friendly error if pygame is not installed, including
	guidance on how to install it using the project scripts.
	"""
	try:
		import pygame as _pg  # type: ignore
		return _pg
	except Exception as e:  # pragma: no cover - exercised in manual runs
		raise RuntimeError(
			"Pygame is required for the GUI visualizer but is not installed.\n"
			"Install it with:\n  powershell -ExecutionPolicy Bypass -File .\\scripts\\setup.ps1 -WithGUI\n"
			"Or\n  python -m pip install pygame\n"
			"Then re-run the visualizer."
		) from e


def draw_frame(screen: Any, grid: Grid, agent: OnlineAgent, cell_size: int = 24, show_grid: bool = True):
		"""Draw a single frame onto an existing pygame screen.

		Contract
		- Does not flip the display; caller should call pygame.display.flip() after drawing.
		- Uses Grid visibility; Agent is only used for current position and plan.
		- No side effects to Grid/Agent beyond reading fields.

		TODO(Thomz): implement with pygame; placeholder is a no-op to keep CI green.
		"""
		# Import pygame lazily
		pygame = _require_pygame()

		# Colors
		FOG = (50, 150, 50)
		WALL = (150, 40, 40)
		FLOOR = (230, 230, 230)
		START = (34, 139, 34)
		GOAL = (255, 200, 34)
		AGENT = (30, 144, 255)
		PLAN_RGB = (255, 200, 0)
		GRID_LINE = (200, 200, 200)

		rows = getattr(grid, "height", None)
		cols = getattr(grid, "width", None)
		if rows is None or cols is None:
			# try fallback to grid dimensions
			rows = len(getattr(grid, "grid", []))
			cols = len(getattr(grid, "grid", [])[0]) if rows else 0

		# Draw cells
		for r in range(rows):
			for c in range(cols):
				x = c * cell_size
				y = r * cell_size
				rect = pygame.Rect(x, y, cell_size, cell_size)

				# Fog handling: if not visible, draw fog color
				visible = False
				try:
					visible = bool(grid.is_visible(r, c))
				except Exception:
					visible = False

				if not visible:
					pygame.draw.rect(screen, FOG, rect)
				else:
					sym = grid.tile_at(r, c)
					if sym == '1' or sym == '#':
						color = WALL
					elif sym == '0' or sym == '.':
						color = FLOOR
					elif sym == 'S':
						color = START
					elif sym == 'G':
						color = GOAL
					else:
						color = FLOOR
					pygame.draw.rect(screen, color, rect)

				if show_grid:
					pygame.draw.rect(screen, GRID_LINE, rect, 1)

		# Plan overlay (semi-transparent)
		plan: List[Tuple[int, int]] = getattr(agent, "current_plan", None) or []
		if plan:
			surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
			surf.fill((*PLAN_RGB, 120))
			# skip index 0 because that's usually the current position
			for (r, c) in plan[1:]:
				x = c * cell_size
				y = r * cell_size
				screen.blit(surf, (x, y))

		# Agent overlay
		pos = getattr(agent, "current", None)
		if pos:
			r, c = pos
			center = (c * cell_size + cell_size // 2, r * cell_size + cell_size // 2)
			radius = max(2, int(cell_size * 0.4))
			pygame.draw.circle(screen, AGENT, center, radius)

		# Start/Goal markers (draw again on top to ensure visibility)
		try:
			start = getattr(grid, "start", None)
		except Exception:
			start = None
		try:
			goal = getattr(grid, "goal", None)
		except Exception:
			goal = None

		if start:
			r, c = start
			rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
			pygame.draw.rect(screen, START, rect, 2)
		if goal:
			r, c = goal
			rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
			pygame.draw.rect(screen, GOAL, rect, 2)

		return


def visualize(agent: OnlineAgent, grid: Grid, cell_size: int = 24, fps: int = 10):
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
		# Import pygame lazily
		pygame = _require_pygame()

		# Initialize pygame only if it isn't already initialized. When called from
		# the menu (which already calls pygame.init()) we want to preserve the
		# initialized state so returning to the menu works smoothly.
		_created_pygame = False
		if not pygame.get_init():
			pygame.init()
			_created_pygame = True
		clock = pygame.time.Clock()

		rows = getattr(grid, "height", None)
		cols = getattr(grid, "width", None)
		if rows is None or cols is None:
			rows = len(getattr(grid, "grid", []))
			cols = len(getattr(grid, "grid", [])[0]) if rows else 0

		# Fixed window dimensions
		WINDOW_WIDTH = 1280
		WINDOW_HEIGHT = 720
		STATS_HEIGHT = 60  # pixels for stats area
		STEPS_WIDTH = 120  # pixels for step counter panel
		
		# Calculate available space for maze
		maze_max_width = WINDOW_WIDTH - STEPS_WIDTH
		maze_max_height = WINDOW_HEIGHT - STATS_HEIGHT
		
		# Calculate scale to fit maze in available space
		width = cols * cell_size
		height = rows * cell_size
		scale = min(maze_max_width / width, maze_max_height / height)
		scaled_cell = max(4, int(cell_size * scale))
		
		# Calculate maze dimensions after scaling
		maze_width = cols * scaled_cell
		maze_height = rows * scaled_cell
		
		# Calculate position to center maze (offset by steps panel width)
		maze_x = STEPS_WIDTH + (maze_max_width - maze_width) // 2
		maze_y = STATS_HEIGHT + (maze_max_height - maze_height) // 2
		
		screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption("Fog Maze")

		# Font for HUD
		try:
			font = pygame.font.SysFont(None, 20)
		except Exception:
			font = None

		paused = False
		running = True
		finished = False
		
		# History tracking
		history = []  # List of (position, plan) tuples
		current_step = 0  # Index into history for replay
		
		# Store initial state
		initial_pos = getattr(agent, "current", None)
		initial_plan = getattr(agent, "current_plan", None)
		if initial_pos is not None:
			history.append((initial_pos, initial_plan))
		finished = False

		# main loop
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
					break
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						running = False
						break
					if event.key == pygame.K_SPACE:
						paused = not paused
						if event.key == pygame.K_n:
							# single step while paused (no-op if already finished)
							if paused and not finished:
								try:
									cont = agent.step()
								except Exception:
									cont = True
								if cont is False:
									finished = True
									paused = True
					if event.key in (pygame.K_PLUS, pygame.K_EQUALS):
						fps = min(120, fps + 5)
					if event.key == pygame.K_MINUS:
						fps = max(1, fps - 5)

			# Handle arrow keys for history navigation
			keys = pygame.key.get_pressed()
			if keys[pygame.K_LEFT]:
				if current_step > 0:
					current_step -= 1
					pos, plan = history[current_step]
					agent.current = pos
					agent.current_plan = plan
			elif keys[pygame.K_RIGHT]:
				if current_step < len(history) - 1:
					current_step += 1
					pos, plan = history[current_step]
					agent.current = pos
					agent.current_plan = plan

			# when not paused, advance one step per frame
			if not paused and not finished:
				try:
					cont = agent.step()
					# Store new state in history
					pos = getattr(agent, "current", None)
					plan = getattr(agent, "current_plan", None)
					if pos is not None and (not history or pos != history[-1][0]):
						history.append((pos, plan))
						current_step = len(history) - 1
				except Exception:
					cont = True
				if cont is False:
					finished = True
					paused = True

			# draw
			screen.fill((30, 30, 30))
			
			# Stats panel at top
			pygame.draw.rect(screen, (40, 40, 40), (0, 0, WINDOW_WIDTH, STATS_HEIGHT))
			pygame.draw.line(screen, (60, 60, 60), (0, STATS_HEIGHT), (WINDOW_WIDTH, STATS_HEIGHT))
			
			# Steps panel on left
			pygame.draw.rect(screen, (40, 40, 40), (0, STATS_HEIGHT, STEPS_WIDTH, WINDOW_HEIGHT - STATS_HEIGHT))
			pygame.draw.line(screen, (60, 60, 60), (STEPS_WIDTH, STATS_HEIGHT), (STEPS_WIDTH, WINDOW_HEIGHT))
			
			# Draw maze below stats panel and to the right of steps panel
			maze_surface = pygame.Surface((maze_width, maze_height))
			maze_surface.fill((30, 30, 30))
			draw_frame(maze_surface, grid, agent, cell_size=scaled_cell, show_grid=True)
			screen.blit(maze_surface, (maze_x, maze_y))
			
			# Stats/HUD in dedicated top panel
			if font is not None:
				# Top stats in three columns
				# Left column
				left_lines = [
					f"Position: {getattr(agent, 'current', None)}",
					f"Plan length: {len(getattr(agent, 'current_plan', []) or [])}"
				]
				
				# Center column
				center_lines = [
					f"Start: {getattr(grid, 'start', None)}",
					f"Goal: {getattr(grid, 'goal', None)}"
				]
				
				# Right column
				right_lines = [
					f"FPS: {fps}",
					"Space: pause/play" if not finished else "Finished — ESC to exit"
				]
				
				# Draw left column
				x = maze_x
				for i, line in enumerate(left_lines):
					surf = font.render(line, True, (200, 200, 200))
					screen.blit(surf, (x, 5 + i * 18))
				
				# Draw center column
				x = maze_x + (maze_width // 2)
				for i, line in enumerate(center_lines):
					surf = font.render(line, True, (200, 200, 200))
					text_width = surf.get_width()
					screen.blit(surf, (x - text_width // 2, 5 + i * 18))
				
				# Draw right column
				x = maze_x + maze_width
				for i, line in enumerate(right_lines):
					surf = font.render(line, True, (200, 200, 200))
					text_width = surf.get_width()
					screen.blit(surf, (x - text_width - 10, 5 + i * 18))
				
				# Steps panel content
				step_lines = []
				for i in range(max(0, len(history))):
					step_num = i + 1
					is_current = i == current_step
					prefix = "→ " if is_current else "  "
					step_text = f"{prefix}Step {step_num}"
					surf = font.render(step_text, True, (255, 255, 255) if is_current else (200, 200, 200))
					screen.blit(surf, (10, STATS_HEIGHT + 10 + i * 20))
				
				# Navigation hint at bottom of steps panel
				hint_text = "← → to navigate"
				surf = font.render(hint_text, True, (150, 150, 150))
				screen.blit(surf, (10, WINDOW_HEIGHT - 30))

			pygame.display.flip()
			clock.tick(fps)

		# finalize metrics (try to be non-destructive)
		try:
			final_metrics = agent.run(0)
		except Exception:
			final_metrics = None

		# Only quit pygame if this function initialized it. When called from the
		# menu we must not quit pygame so the menu can continue running.
		if _created_pygame:
			pygame.quit()
		return final_metrics


def run_menu():
	"""Run a simple pygame main menu to pick a map and a search algorithm.

	Selecting Enter will load the chosen map and algorithm and launch
	the visualizer. After the visualizer exits you return to the menu.
	Controls: Up/Down to move, Tab to switch focus (maps/algos), Enter to run,
	Esc to quit.
	"""
	# Import pygame lazily
	pygame = _require_pygame()

	# menu constants
	WINDOW_WIDTH = 1280
	WINDOW_HEIGHT = 720
	BG = (30, 30, 30)
	PANEL_BG = (40, 40, 40)
	HIGHLIGHT = (255, 220, 120)
	TEXT_COLOR = (200, 200, 200)
	font = None
	try:
		pygame.init()
		font = pygame.font.SysFont(None, 22)
		screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption("Fog Maze - Menu")
		clock = pygame.time.Clock()
	except Exception:
		# If pygame initialization fails, abort gracefully.
		return

	# gather maps
	map_dir = Path("maps")
	map_files = sorted([p for p in map_dir.glob("*.csv")])
	map_names = [p.name for p in map_files]
	if not map_names:
		map_names = ["(no maps found)"]

	# gather algorithms
	algos = sorted(list(SEARCH_ALGOS.keys()))
	if not algos:
		algos = ["(no algos)"]

	map_idx = 0
	algo_idx = 0
	focus = 0  # 0 = maps, 1 = algos
	running = True

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				break
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
					break
				if event.key == pygame.K_TAB:
					focus = 1 - focus
				if event.key == pygame.K_UP:
					if focus == 0 and map_idx > 0:
						map_idx -= 1
					elif focus == 1 and algo_idx > 0:
						algo_idx -= 1
				if event.key == pygame.K_DOWN:
					if focus == 0 and map_idx < len(map_names) - 1:
						map_idx += 1
					elif focus == 1 and algo_idx < len(algos) - 1:
						algo_idx += 1
				if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
					# launch visualizer with current selection
					if not map_files:
						continue
					selected_map = map_files[map_idx]
					selected_algo = algos[algo_idx]
					# build grid and agent
					try:
						grid = Grid.from_csv(selected_map)
					except Exception as e:
						# show error briefly then continue
						print(f"Failed to load map {selected_map}: {e}")
						continue
					search_fn = SEARCH_ALGOS.get(selected_algo)
					agent = OnlineAgent(grid, full_map=False, search_algo=search_fn)
					# run visualize (blocking) and then return to menu when it exits
					visualize(agent, grid, cell_size=24, fps=8)

		# draw menu
		screen.fill(BG)
		# title
		title_s = font.render("Fog Maze — Select map and algorithm", True, HIGHLIGHT)
		screen.blit(title_s, (20, 12))

		# draw maps list panel
		maps_x = 40
		maps_y = 60
		pygame.draw.rect(screen, PANEL_BG, pygame.Rect(maps_x - 10, maps_y - 10, 360, WINDOW_HEIGHT - maps_y - 40))
		mx = maps_x
		y = maps_y
		for i, name in enumerate(map_names):
			if i == map_idx:
				col = HIGHLIGHT if focus == 0 else (220, 220, 160)
			else:
				col = TEXT_COLOR
			s = font.render(name, True, col)
			screen.blit(s, (mx, y))
			y += 26

		# draw algos list panel
		algos_x = 420
		algos_y = 60
		pygame.draw.rect(screen, PANEL_BG, pygame.Rect(algos_x - 10, algos_y - 10, 200, WINDOW_HEIGHT - algos_y - 40))
		x = algos_x
		y = algos_y
		for i, name in enumerate(algos):
			if i == algo_idx:
				col = HIGHLIGHT if focus == 1 else (220, 220, 160)
			else:
				col = TEXT_COLOR
			s = font.render(name, True, col)
			screen.blit(s, (x, y))
			y += 26

		# instructions
		instr = font.render("Up/Down: select  Tab: switch column  Enter: run  Esc: quit", True, (150, 150, 150))
		screen.blit(instr, (20, WINDOW_HEIGHT - 30))

		pygame.display.flip()
		clock.tick(30)

	pygame.quit()
	return
