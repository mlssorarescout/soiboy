# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

No build system, test framework, or linter is configured.

## Architecture

This is a Streamlit dashboard for Sorare fantasy football fixture analysis. It has three main sections: **Fixture Difficulty** (team heatmaps), **Sorare Opportunity Index / SOI** (player scoring), and **Matchup Cohesion** (team pairing analysis).

### Module Responsibilities

- **`app.py`** — Entry point: page config, style injection, runs dashboard
- **`src/dashboard.py`** — Central controller: all sidebar filters and the three dashboard sections
- **`src/data.py`** — Loads `data/Calculated Opponent Difficulty.csv`; `calculate_gameweeks()` maps match dates to GW numbers anchored to Feb 27 2026 (GW 57) with alternating Fri/Tue week boundaries
- **`src/player_data.py`** — Loads `data/Player_Metrics.csv`; normalizes metrics to percentile rank (0–1) within the filtered pool; `calculate_soi()` applies user-defined weights
- **`src/matchup_cohesion.py`** — Scores team pairs on Both Play %, Both Home %, and combined fixture difficulty (weights 20/40/40)
- **`src/pivots.py`** — Produces value, label, and opponent pivot tables keyed by team × gameweek
- **`src/grid.py`** — Generates AG Grid config and the JS `cellStyle` function for color-gradient cells (green→white→red, neutral at `DIFFICULTY_CENTER=48`)
- **`src/player_grid.py`** — Same as `grid.py` but for the player/SOI grid
- **`src/styles.py`** — Injects all custom CSS; mobile-first with `clamp()` sizing and Streamlit component overrides
- **`src/config.py`** — All constants: data paths, competition mappings (league → Sorare group), color scheme, default SOI weights

### Data Flow

```
CSV files → data.py / player_data.py → filtering (sidebar) → pivots.py → grid.py → AG Grid display
```

### Key Conventions

- Difficulty scores are colored via JavaScript `JsCode` inside AG Grid — edits to color logic belong in `grid.py` / `player_grid.py`
- Competition filtering is two-level: Sorare competition group first, then individual league — mapping lives in `config.py` (`SORARE_COMPETITION_MAPPING`)
- Gameweek boundaries alternate Friday/Tuesday, anchored to a hardcoded reference point in `data.py`
- Player metric normalization uses `rank(pct=True)` applied within the currently filtered pool, so SOI scores are relative to what's on screen
