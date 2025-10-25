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
from src.search import ALGORITHMS_NEIGHBORS_WITH_STATS as SEARCH_ALGOS_WITH_STATS

# Maximum FPS cap for GUI. Increase if you want faster stepping on large maps.
MAX_FPS = 1000


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
		PATH_RGB = (255, 165, 0)  # orange for visited path
		GRID_LINE = (200, 200, 200)

		rows = getattr(grid, "height", None)
		cols = getattr(grid, "width", None)
		if rows is None or cols is None:
			# try fallback to grid dimensions
			rows = len(getattr(grid, "grid", []))
			cols = len(getattr(grid, "grid", [])[0]) if rows else 0

		# Whether fog is disabled (agent has full map)
		no_fog = bool(getattr(agent, "full_map", False))

		# Draw cells
		for r in range(rows):
			for c in range(cols):
				x = c * cell_size
				y = r * cell_size
				rect = pygame.Rect(x, y, cell_size, cell_size)

				# Fog handling: in no-fog mode treat all tiles as visible
				visible = True if no_fog else False
				if not no_fog:
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

		# Path-taken overlay (semi-transparent, drawn before plan)
		m = getattr(agent, "metrics", None)
		path_taken: List[Tuple[int, int]] = getattr(m, "path_taken", None) or []
		if path_taken:
			surf_path = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
			surf_path.fill((*PATH_RGB, 90))
			for (r, c) in path_taken:
				# avoid overdrawing the current agent cell; agent marker will show there
				if getattr(agent, "current", None) == (r, c):
					continue
				x = c * cell_size
				y = r * cell_size
				screen.blit(surf_path, (x, y))

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
		STATS_HEIGHT = 120  # pixels for stats area (expanded to fit more HUD lines)
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
					elif event.key == pygame.K_n:
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
						fps = min(MAX_FPS, fps + 5)
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
				# Derive helpful labels
				# Map name (set by menu) and algorithm
				map_name = getattr(grid, "map_name", None) or getattr(grid, "name", None) or "(unknown map)"
				# Try to use an explicit search_name if provided; else try to infer from SEARCH_ALGOS or function __name__
				algo_name = getattr(agent, "search_name", None)
				if not algo_name:
					try:
						algo_fn = getattr(agent, "search", None)
						algo_name = next((k for k, v in SEARCH_ALGOS.items() if v is algo_fn), None)
						if not algo_name and hasattr(algo_fn, "__name__"):
							algo_name = getattr(algo_fn, "__name__")
					except Exception:
						algo_name = None
				algo_name = algo_name or "(unknown algo)"

				# Live metrics (robust to missing fields)
				m = getattr(agent, "metrics", None)
				steps = getattr(m, "steps", 0) if m is not None else 0
				replans = getattr(m, "replans", 0) if m is not None else 0
				nodes = getattr(m, "nodes_expanded", 0) if m is not None else 0
				# Display a live cumulative cost based on path length to avoid depending on the last search plan cost
				path_len = len(getattr(m, "path_taken", []) or []) if m is not None else 0
				cost = max(0, path_len - 1)
				runtime = getattr(m, "runtime", 0.0) if m is not None else 0.0

				# Top stats in three columns (multiple lines supported by taller STATS_HEIGHT)
				# Left column: map/algo/fog
				left_lines = [
					f"Map: {map_name}",
					f"Algo: {algo_name}",
					f"Fog: {'Off' if getattr(agent, 'full_map', False) else 'On'}",
				]

				# Center column: start/goal/size
				center_lines = [
					f"Start: {getattr(grid, 'start', None)}",
					f"Goal: {getattr(grid, 'goal', None)}",
					f"Size: {cols}x{rows}",
				]

				# Right column: live stats + status
				status_str = (
					"Finished — ESC to exit" if finished else ("Paused" if paused else "Running")
				)
				right_lines = [
					f"Steps: {steps}   Replans: {replans}",
					f"Nodes: {nodes}   Cost: {cost}",
					f"Runtime: {runtime:.3f}s   FPS: {fps}",
					status_str,
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
				
				# Steps panel content — compact counter
				if history:
					current_display = current_step + 1
					total_display = len(history)
					if current_step < total_display - 1:
						counter_text = f"Step: {current_display}/{total_display}"
					else:
						# At latest step; show just the current counter to avoid redundant N/N
						counter_text = f"Step: {current_display}"
				else:
					counter_text = "Step: 0"
				surf = font.render(counter_text, True, (255, 255, 255))
				screen.blit(surf, (10, STATS_HEIGHT + 10))

				# Navigation hint at bottom of steps panel (history navigation still works)
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
	fps_init = 8  # allow adjusting initial FPS from the menu with +/- or 'F' to edit
	fog_enabled = True  # default like CLI (fog on); toggle with 'V'
	with_stats = False  # toggle metrics-enabled search wrappers with 'T'
	# Simple inline editor state for FPS numeric entry
	editing_fps = False
	fps_buffer = ""
	running = True

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				break
			if event.type == pygame.KEYDOWN:
				# Handle inline FPS editing mode first
				if editing_fps:
					if event.key == pygame.K_ESCAPE:
						# cancel editing
						editing_fps = False
						fps_buffer = ""
						continue
					if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
						# apply if buffer has a number; else keep previous
						if fps_buffer.strip():
							try:
								val = int(fps_buffer)
								fps_init = max(1, min(MAX_FPS, val))
							except Exception:
								pass
						fps_buffer = ""
						editing_fps = False
						continue
					if event.key == pygame.K_BACKSPACE:
						fps_buffer = fps_buffer[:-1]
						continue
					# accept digits from top row and keypad
					if event.unicode and event.unicode.isdigit():
						# limit length to avoid overflow
						if len(fps_buffer) < 4:
							fps_buffer += event.unicode
						continue

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
				if event.key == pygame.K_f:
					# enter FPS editing mode
					editing_fps = True
					fps_buffer = ""
				if event.key == pygame.K_v:
					# toggle fog on/off
					fog_enabled = not fog_enabled
				if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
					fps_init = min(MAX_FPS, fps_init + 1)
				if event.key == pygame.K_MINUS:
					fps_init = max(1, fps_init - 1)
				if event.key == pygame.K_t:
					# toggle stats-enabled search variants
					with_stats = not with_stats
				if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
					# launch visualizer with current selection
					if not map_files:
						continue
					selected_map = map_files[map_idx]
					selected_algo = algos[algo_idx]
					# build grid and agent
					try:
						grid = Grid.from_csv(selected_map)
						# annotate grid with a friendly name for HUD
						setattr(grid, "map_name", selected_map.name)
					except Exception as e:
						# show error briefly then continue
						print(f"Failed to load map {selected_map}: {e}")
						continue
					search_fn = (SEARCH_ALGOS_WITH_STATS if with_stats else SEARCH_ALGOS).get(selected_algo)
					# full_map is inverse of fog_enabled
					agent = OnlineAgent(grid, full_map=(not fog_enabled), search_algo=search_fn)
					# annotate agent with algorithm name for HUD
					setattr(agent, "search_name", selected_algo + ("+stats" if with_stats else ""))
					# run visualize (blocking) and then return to menu when it exits
					visualize(agent, grid, cell_size=24, fps=fps_init)

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

		# instructions + FPS hint
		instr_fog = font.render(f"Fog: {'On' if fog_enabled else 'Off'}  (V to toggle)", True, (150, 150, 150))
		screen.blit(instr_fog, (20, WINDOW_HEIGHT - 70))
		instr1 = font.render("Up/Down: select  Tab: switch column  Enter: run  Esc: quit", True, (150, 150, 150))
		screen.blit(instr1, (20, WINDOW_HEIGHT - 50))
		instr2 = font.render(f"FPS: {fps_init}  (+/- to change, F to type)   Metrics: {'On' if with_stats else 'Off'} (T)", True, (150, 150, 150))
		screen.blit(instr2, (20, WINDOW_HEIGHT - 30))

		# Draw inline FPS editor overlay if active
		if editing_fps:
			overlay = pygame.Surface((WINDOW_WIDTH, 60))
			overlay.set_alpha(220)
			overlay.fill((20, 20, 20))
			screen.blit(overlay, (0, WINDOW_HEIGHT - 60))
			prompt = f"Enter FPS (1..{MAX_FPS}), Enter to apply, Esc to cancel: {fps_buffer or ''}"
			ps = font.render(prompt, True, (255, 220, 120))
			screen.blit(ps, (20, WINDOW_HEIGHT - 45))

		pygame.display.flip()
		clock.tick(30)

	pygame.quit()
	return
