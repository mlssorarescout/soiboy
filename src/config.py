from pathlib import Path

DATA_PATH = Path(r"A:\Documents\SOI\Output\Calculated Opponent Difficulty.csv")

COMPETITION_NAMES = {
    "primera-division-cl": "Primera Division",
    "laliga-es": "LaLiga",
    "bundesliga-de": "Bundesliga",
    "austrian-bundesliga": "Austrian Bundesliga",
    "serie-a-it": "Serie A",
    "campeonato-brasileiro-serie-a": "Brasil Serie A",
}

DIFFICULTY_COLORS = {
    "easy": (34, 197, 94),
    "hard": (239, 68, 68),
    "neutral": (255, 255, 255)
}

DIFFICULTY_CENTER = 48
COLOR_OPACITY = 2