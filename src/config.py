"""
Configuration settings for the Opponent Difficulty Dashboard.

This module contains all configurable parameters including file paths,
competition mappings, and visual styling settings.
"""

from pathlib import Path
import os

# Data file locations
# For production, use relative paths
DATA_PATH = Path(os.getenv("DATA_PATH", "data/Calculated Opponent Difficulty.csv"))
PLAYER_DATA_PATH = Path(os.getenv("PLAYER_DATA_PATH", "data/Player_Metrics.csv"))

# Competition display name mappings
# Maps internal slugs to user-friendly competition names
COMPETITION_NAMES = {
    "primera-division-cl": "Primera Division",
    "laliga-es": "LaLiga",
    "bundesliga-de": "Bundesliga",
    "austrian-bundesliga": "Austrian Bundesliga",
    "serie-a-it": "Serie A",
    "campeonato-brasileiro-serie-a": "Brasil Serie A",
    "russian-premier-league": "Russian Premier League",
    "premier-league-gb-eng": "EPL"
}

# Sorare Competition mapping
# Maps competition names to Sorare competition groups
SORARE_COMPETITION_MAPPING = {
    "Austrian Bundesliga": "Challenger",
    "First Division A": "Jupiler Pro League",
    "UEFA Champions League": "UEFA",
    "UEFA Europa League": "UEFA",
    "HNL": "Contender",
    "Superliga": "Challenger",
    "EPL": "EPL",
    "Championship": "Contender",
    "Ligue 1": "Ligue 1",
    "Ligue 2": "Contender",
    "Bundesliga": "Bundesliga",
    "2. Bundesliga": "Contender",
    "Serie A": "Challenger",
    "Serie B": "Contender",
    "Eredivisie": "Eredivisie",
    "Primeira Liga": "Challenger",
    "Premiership": "Challenger",
    "LaLiga": "LaLiga",
    "Segunda División": "Contender",
    "Süper Lig": "Challenger",
    "MLS": "MLS",
    "Concacaf Champions Cup": "Concacaf Champions Cup",
    "Liga Profesional Argentina": "Contender",
    "CONMEBOL Libertadores": "CONMEBOL Libertadores",
    "Liga MX": "Contender",
    "K League 1": "K League 1",
    "AFC Champions League Elite": "AFC Champions League Elite",
    "Liga 1": "Contender",
    "Primera Division": "Contender",
    "Brasil Serie A": "Contender",
    "Super League": "Contender",
    "Primera A": "Contender",
    "J1 100 Year Vision League": "J1 100 Year Vision League",
    "UEFA Conference League": "UEFA",
    "Russian Premier League": "Contender"
}

# Color scheme for difficulty visualization
# RGB tuples for easy, hard, and neutral difficulty ratings
DIFFICULTY_COLORS = {
    "easy": (34, 197, 94),    # Green - easier opponents
    "hard": (239, 68, 68),     # Red - harder opponents
    "neutral": (255, 255, 255) # White - neutral/average difficulty
}

# Difficulty calculation settings
DIFFICULTY_CENTER = 48    # The neutral difficulty value (center point)
COLOR_OPACITY = 2         # Multiplier for color intensity (higher = more vibrant)

# Player strength metric normalization settings
STRENGTH_METRICS = {
    "Last_5_Score_Avg": {
        "divisor": 70,
        "display_name": "L5 Form",
        "tooltip": "Last 5 games average score / 70"
    },
    "Last_15_Score_Avg": {
        "divisor": 70,
        "display_name": "L15 Form",
        "tooltip": "Last 15 games average score / 70"
    },
    "Mean_Opp_Score": {
        "divisor": 60,
        "display_name": "Next 5 Diff",
        "tooltip": "Mean opponent difficulty score / 60"
    },
    "Last_5_Mins": {
        "divisor": 450,
        "display_name": "L5 Minutes",
        "tooltip": "Last 5 games minutes played / 450"
    },
    "Last_15_Mins": {
        "divisor": 1350,
        "display_name": "L15 Minutes",
        "tooltip": "Last 15 games minutes played / 1350"
    }
}

# Color scheme for player strength visualization
# Inverse of difficulty (high values = green, low values = red)
STRENGTH_COLORS = {
    "strong": (34, 197, 94),    # Green - high strength
    "weak": (239, 68, 68),      # Red - low strength
    "neutral": (255, 255, 255)  # White - neutral strength
}

STRENGTH_CENTER = 0.5  # Neutral point for strength metrics (after normalization)
STRENGTH_OPACITY = 2   # Multiplier for color intensity

# Default SOI (Strength of Investment) weights
DEFAULT_SOI_WEIGHTS = {
    "l5_form": 0.2,
    "l15_form": 0.4,
    "next_5_diff": 0.2,
    "l5_mins": 0.1,
    "l15_mins": 0.1
}