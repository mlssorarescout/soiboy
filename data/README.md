# Data Directory

Place your `Calculated Opponent Difficulty.csv` file in this directory.

The CSV file should contain the following columns:
- Date
- Competition_Display or Comp_Slug
- Position
- Score_mean
- Score_median
- Domestic League Ranking
- Opponent
- Location
- name (upcomingGames.competition)

## File Location

The default configuration expects the file at:
```
data/Calculated Opponent Difficulty.csv
```

If your file is located elsewhere, update the `DATA_PATH` variable in `src/config.py`.
