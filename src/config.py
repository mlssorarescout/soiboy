"""
Configuration settings for the Opponent Difficulty Dashboard.

This module contains all configurable parameters including file paths,
competition mappings, and visual styling settings.
"""

from pathlib import Path
import os

# Data file location - update this path to match your CSV file location
# For production, use relative path: Path("data/Calculated Opponent Difficulty.csv")
DATA_PATH = Path(os.getenv("DATA_PATH", "data/Calculated Opponent Difficulty.csv"))

# Competition display name mappings
# Maps internal slugs to user-friendly competition names
COMPETITION_NAMES = {
    "primera-division-cl": "Primera Division",
    "laliga-es": "LaLiga",
    "bundesliga-de": "Bundesliga",
    "austrian-bundesliga": "Austrian Bundesliga",
    "serie-a-it": "Serie A",
    "campeonato-brasileiro-serie-a": "Brasil Serie A",
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