param(
  [string]$Repo = "LC271828/ai-mini-project-fog-maze"
)

# Optional: create commonly used labels (ignore errors if they already exist)
$labels = @(
  @{ name="core";           color="5319e7"; desc="Core implementation" },
  @{ name="algorithms";     color="1d76db"; desc="Search algorithms" },
  @{ name="agent";          color="0e8a16"; desc="Agent logic" },
  @{ name="cli";            color="0052cc"; desc="Command-line interface" },
  @{ name="visualization";  color="fbca04"; desc="Pygame visualization" },
  @{ name="tests";          color="e11d21"; desc="Unit tests" },
  @{ name="docs";           color="d4c5f9"; desc="Documentation" },
  @{ name="design";         color="b60205"; desc="Design/API alignment" },
  @{ name="infra";          color="c2e0c6"; desc="Infra/Repo config" },
  @{ name="data";           color="bfdadc"; desc="Maps/data" },
  @{ name="process";        color="fef2c0"; desc="Process/Contributing" }
)
foreach ($l in $labels) {
  try { gh label create $l.name --color $l.color --description $l.desc --repo $Repo | Out-Null } catch {}
}

function New-Issue {
  param(
    [Parameter(Mandatory=$true)][string]$Title,
    [Parameter(Mandatory=$true)][string]$Body,
    [string]$Labels = "",
    [string]$Assignees = ""
  )
  $cmdArgs = @("issue", "create", "--repo", $Repo, "--title", $Title, "--body", $Body)
  if ($Labels -ne "") { $cmdArgs += @("--label", $Labels) }
  if ($Assignees -ne "") { $cmdArgs += @("--assignee", $Assignees) }
  gh @cmdArgs
}

# 1) Implement Grid CSV loader + fog-of-war
$body = @'
Implement Grid in src/grid.py:
- from_csv(path), in_bounds, passable, neighbors4, tile_at, is_visible
- Fog: reveal_from(pos) radius=1 (U/D/L/R), walls reveal and block beyond; no re-fogging
- get_visible_neighbors(pos), visible_tiles()
CSV rules: rectangular; symbols {0,1,S,G}; exactly one S and one G; raise ValueError.

Acceptance criteria:
- Loading maps/demo.csv yields correct grid/start/goal; visible mask starts all False
- reveal_from(start) reveals start and adjacent cells per spec; visibility persists (no re-fog)
- No auto-added boundary walls; coordinates match CSV

Tasks:
- [ ] Implement data structure and API
- [ ] Input validation with helpful error messages
- [ ] Minimal doctests or comments with asserts
'@
New-Issue -Title "Implement Grid CSV loader + fog-of-war" -Body $body -Labels "enhancement,core" -Assignees "asthar,leo"

# 2) Implement search algorithms (BFS/DFS/UCS/A*) in src/search.py
$body = @'
Implement pure functions in src/search.py:
- bfs(grid, start, goal) -> (path, nodes_expanded)
- dfs(grid, start, goal) -> (path, nodes_expanded)
- ucs(grid, start, goal) -> (path, nodes_expanded)
- astar(grid, start, goal, h=manhattan) -> (path, nodes_expanded)
- ALGORITHMS = {"bfs": bfs, "dfs": dfs, "ucs": ucs, "astar": astar}

Acceptance criteria:
- Works on a simple open grid and maps/demo.csv
- A* path length equals BFS/UCS on unit-cost grid

Tasks:
- [ ] Implement algorithms (no pygame/no I/O)
- [ ] Shared reconstruct helper
- [ ] Docstrings clarify nodes_expanded definition
'@
New-Issue -Title "Implement search algorithms (BFS/DFS/UCS/A*)" -Body $body -Labels "enhancement,algorithms,core" -Assignees "gibran,leo"

# 3) Implement OnlineAgent with re-planning
$body = @'
Implement OnlineAgent in src/agent.py:
- Perceive (reveal), Plan (search.ALGORITHMS[algo]), Act (move one step)
- Re-plan as visibility expands; reach goal on demo map
- Metrics dataclass: steps, nodes_expanded, replans, runtime
- Exploration when no known path: simple frontier-based strategy

Acceptance criteria:
- Agent reaches G on maps/demo.csv
- run() returns Metrics with the fields above

Tasks:
- [ ] Define Metrics dataclass
- [ ] Implement step() and run()
- [ ] Add simple frontier exploration
'@
New-Issue -Title "Implement OnlineAgent with re-planning" -Body $body -Labels "enhancement,agent,core" -Assignees "ahsan,leo"

# 4) CLI wiring (src/main.py)
$body = @'
Implement CLI in src/main.py:
- Flags: --map, --algo [bfs|dfs|ucs|astar], --gui, --config
- Headless prints metrics; --gui invokes visualizer if available

Acceptance criteria:
- Running --map maps/demo.csv --algo astar prints cost, nodes expanded, runtime

Tasks:
- [ ] Argument parsing
- [ ] Wire Grid + Agent + (optional) Visualize
- [ ] Friendly errors and exit codes
'@
New-Issue -Title "CLI wiring (src/main.py)" -Body $body -Labels "enhancement,cli" -Assignees "leo"

# 5) Visualization (optional Pygame)
$body = @'
Implement src/visualize.py:
- Render grid, fog mask, agent, current path
- Step agent per frame; allow quit

Acceptance criteria:
- Works with --gui; fog correctly shows unknown vs visible vs walls

Tasks:
- [ ] Rendering loop and colors
- [ ] Integrate with OnlineAgent step()
'@
New-Issue -Title "Visualization (Pygame)" -Body $body -Labels "enhancement,visualization" -Assignees "thomz"

# 6) Unit tests: search algorithms
$body = @'
Add tests in tests/test_search.py:
- BFS/DFS find path on simple grid
- UCS equals BFS length on unit-cost maps
- A* finds optimal path with Manhattan heuristic

Acceptance criteria:
- Tests pass locally and in CI (when added)

Tasks:
- [ ] Tiny fixture grids
- [ ] Tests per algorithm
'@
New-Issue -Title "Unit tests: search algorithms" -Body $body -Labels "tests" -Assignees "gibran"

# 7) Unit tests: fog and agent
$body = @'
Add tests in tests/test_fog.py:
- reveal_from radius=1; walls reveal and block beyond; no re-fogging
- Agent explores and reaches goal on maps/demo.csv

Acceptance criteria:
- Tests pass with implemented Grid and OnlineAgent

Tasks:
- [ ] Fog visibility tests
- [ ] Agent reachability test
'@
New-Issue -Title "Unit tests: fog and agent" -Body $body -Labels "tests" -Assignees "asthar,ahsan"

# 8) Align search API across code and docs
$body = @'
Ensure a single search signature across code and docs:
- Keep grid-first signature (matches quickstart and TEAM_API.md) or update consistently
- Update README.md, TEAM_API.md, quickstart accordingly

Acceptance criteria:
- All docs and examples use the same signatures

Tasks:
- [ ] Confirm final signature
- [ ] Update docs and examples
'@
New-Issue -Title "Align search API across code and docs" -Body $body -Labels "design,docs" -Assignees "leo,bayu,gibran"

# 9) Documentation sync and slides
$body = @'
Keep docs in sync with implementation:
- Update README.md, docs/PEAS.md, docs/requirements.md, TEAM_API.md
- Add a simple "How to run" and metrics definitions

Acceptance criteria:
- Docs reflect actual behavior and CLI options

Tasks:
- [ ] Update docs post-merge of Grid/Search/Agent
- [ ] Add 1–2 images/diagrams if helpful
'@
New-Issue -Title "Documentation sync and slides" -Body $body -Labels "docs" -Assignees "bayu"

# 10) CODEOWNERS setup
$body = @'
Add .github/CODEOWNERS with module ownership:
- Core modules owned by respective leads + integrator
- experiments/* owned per person

Acceptance criteria:
- PRs auto-request appropriate reviewers

Tasks:
- [ ] Fill with real usernames
- [ ] Commit to dev and verify on a test PR
'@
New-Issue -Title "CODEOWNERS setup" -Body $body -Labels "infra" -Assignees "leo"

# 11) Experiments hygiene and promotion process
$body = @'
Improve CONTRIBUTING.md and experiments/README.md:
- No imports from experiments/ into src/ or tests/
- Promotion process: how to graduate code from experiments to src via PR

Acceptance criteria:
- Clear, short checklist in docs

Tasks:
- [ ] Add promotion checklist
- [ ] Cross-link from README
'@
New-Issue -Title "Experiments hygiene and promotion process" -Body $body -Labels "process,docs" -Assignees "leo,bayu"

# 12) Map curation and additional demos
$body = @'
Add more CSV maps with varied patterns:
- Narrow corridors, cul-de-sacs, simple open map

Acceptance criteria:
- New maps validate with Grid.from_csv

Tasks:
- [ ] Create maps/demo2.csv and maps/demo3.csv
- [ ] Update maps/README.md with notes
'@
New-Issue -Title "Map curation and additional demos" -Body $body -Labels "data,enhancement" -Assignees "asthar"
