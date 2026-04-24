# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

**Flask app factory** (`app/__init__.py`) — reads `MTG_TEST_MODE` env var, resolves `DATA_DIR` to `data/` or `data/test/`, wipes and re-seeds DB if in test mode, registers the single Blueprint.

**Single Blueprint** (`app/routes.py`) — all routes live here. No sub-blueprints. Stats are computed on-the-fly by helper functions (`_compute_player_stats`, `_compute_commander_stats`, `_compute_color_stats`, `_compute_aggregated_color_stats`) called at dashboard render time; nothing is cached.

**4 SQLAlchemy models** (`app/models.py`):
- `Player` — static set of 6 players, seeded on first run
- `Commander` — name + MTG color identity string (e.g. `UBR`); ~40 seeded on first run, user-expandable
- `Game` — date + total_turns; cascade-deletes its entries
- `GameEntry` — the join between a player, a commander, and a game; holds finish placement, turn order, sol_ring_t1, eliminated_by_id (FK to Commander), victory_condition / loss_condition, notes

**Key invariant in GameEntry:** winners (`finish == 1`) have `victory_condition` set and NULL for `loss_condition` / `eliminated_by_id` / `turn_eliminated`; losers are the inverse. Routes enforce this split when saving.

**Excel sync** (`app/excel_sync.py`, `app/import_excel.py`):
- `_sync_excel()` is called explicitly after every write operation (create/edit/delete game) — it is not automatic via SQLAlchemy events
- Import auto-detects column positions by scanning headers for keywords (`pilot`, `deck`, `colour`, `turns`, etc.); unknown players/commanders are created on the fly with color `?`
- Both files write to `DATA_DIR`, which is isolated in test mode

## Environment variables

| Variable | Effect |
|---|---|
| `MTG_TEST_MODE` | `1`/`true`/`yes` → use `data/test/` DB, wipe on startup, enable `/test/reset` |
| `SECRET_KEY` | Flask session key; defaults to `change-me-in-production` |
| `TS_AUTHKEY` | Tailscale auth key (Docker only, read from `.env`) |

## Docker / Tailscale

Two services in `docker-compose.yml`:
- `tailscale` — runs the Tailscale daemon, registers hostname `mtg-tracker`, persists state in a named volume
- `app` — shares `tailscale`'s network namespace (`network_mode: service:tailscale`), mounts `./data` to persist DB and Excel outside the container

The app container never exposes a port to the host directly; all traffic goes through the Tailscale interface.

## UI conventions

- All UI strings are in Italian
- Color identity buttons in commander modals follow canonical MTG order: W → U → B → R → G; the hidden input is populated by JS in that order
- Flash categories map to CSS classes: `flash-success`, `flash-error`, `flash-warning`
- `config.TEST_MODE` is available in all Jinja2 templates (passed via Flask app config)
