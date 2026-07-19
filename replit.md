# Space Shooter

A pygame-based space shooter game, playable in the browser via pygbag (WebAssembly).

## Controls
- **Arrow keys** — move the ship
- **Space** — shoot
- **P** — pause
- **S** — open shop (buy upgrades between waves)
- **R** — restart
- **Esc** — quit (desktop only)

## Stack
- Python 3.12
- pygame 2.6.1
- pygbag 0.9.3 (converts pygame to WebAssembly for browser play)

## Project files
- `main.py` — the game (async-compatible version for pygbag)
- `space_shooter.py` — original imported source
- `run.sh` — serves the pre-built web output
- `build/web/` — pygbag build output (static files served to the browser)

## How to run
The workflow (`bash run.sh`) serves `build/web/` on port 5000 using Python's HTTP server.

### Rebuilding after code changes
If you change `main.py`, rebuild with:
```bash
find . -not -path './.git/*' | xargs touch 2>/dev/null
python -m pygbag --build main.py
```
This regenerates `build/web/`. Then restart the workflow.

## User preferences
- Keep the project's original structure and stack (Python/pygame).
