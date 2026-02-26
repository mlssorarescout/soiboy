import pandas as pd
import streamlit as st
from src.config import COMPETITION_NAMES, SORARE_COMPETITION_MAPPING

# Known correct reference point: Friday 2026-02-27 at 15:00 UTC = start of GW 58
# This anchors the Fri/Tue alternating grid regardless of what data is loaded.
_REFERENCE_BOUNDARY = pd.Timestamp("2026-02-27T15:00:00Z")
_REFERENCE_GW = 57
_PERIODS = [pd.Timedelta(days=4), pd.Timedelta(days=3)]  # Fri→Tue, Tue→Fri


@st.cache_data
def load_and_prepare_data(file_path):
    """
    Load and prepare the opponent difficulty data from CSV.

    Args:
        file_path: Path to the CSV file

    Returns:
        Prepared DataFrame with cleaned data types and display names

    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        Exception: For other data loading errors
    """
    df = pd.read_csv(file_path)

    # Convert date column to datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)

    # Convert numeric columns
    numeric_cols = ["Domestic League Ranking", "Score_mean", "Score_median"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Create display-friendly competition names
    df["Competition_Display"] = df["Comp_Slug"].map(COMPETITION_NAMES).fillna(
        df["name (upcomingGames.competition)"]
    )

    # Create Sorare Competition grouping (use Competition_Display instead of raw name)
    df["Sorare_Competition"] = (
        df["Competition_Display"].map(SORARE_COMPETITION_MAPPING).fillna("Other")
    )

    # Map location to H/A abbreviation
    df["HA"] = df["Location"].map({"Home": "H", "Away": "A"}).fillna("")

    return df


def _build_boundaries(min_date, max_date):
    """
    Build a list of (boundary_timestamp, gameweek_number) tuples covering
    [min_date, max_date], anchored to _REFERENCE_BOUNDARY / _REFERENCE_GW.

    Boundaries alternate every 4 days (Fri->Tue) then 3 days (Tue->Fri) at 15:00 UTC.
    """
    # --- build forward from reference ---
    forward_boundaries = [_REFERENCE_BOUNDARY]
    i = 0
    while forward_boundaries[-1] <= max_date + pd.Timedelta(days=7):
        forward_boundaries.append(forward_boundaries[-1] + _PERIODS[i % 2])
        i += 1

    # --- build backward from reference ---
    # Going backward the period order reverses: step back 3 days, then 4, then 3...
    backward_boundaries = []
    prev = _REFERENCE_BOUNDARY
    i = 1  # first step back uses _PERIODS[1 % 2] = 3 days
    while prev > min_date - pd.Timedelta(days=7):
        prev = prev - _PERIODS[i % 2]
        backward_boundaries.insert(0, prev)
        i += 1

    all_boundaries = backward_boundaries + forward_boundaries

    # Assign gameweek numbers relative to the reference
    ref_index = len(backward_boundaries)
    gameweeks = [
        _REFERENCE_GW + (idx - ref_index) for idx in range(len(all_boundaries))
    ]

    return list(zip(all_boundaries, gameweeks))


def calculate_gameweeks(df):
    """
    Calculate gameweek numbers based on match dates.

    Gameweek boundaries alternate between:
      - Friday  15:00 UTC  ->  Tuesday 15:00 UTC  (4 days)
      - Tuesday 15:00 UTC  ->  Friday  15:00 UTC  (3 days)

    The grid is anchored to a known reference point so it remains correct
    regardless of the date range of data loaded.

    Args:
        df: DataFrame with 'Date' column and 'Game Week' column from CSV

    Returns:
        DataFrame with 'Game Week' column calculated
    """
    if df.empty or df["Date"].isna().all():
        df["Game Week"] = pd.NA
        return df

    if "Game Week" not in df.columns:
        st.error("❌ 'Game Week' column not found in the CSV file.")
        st.stop()

    min_date = df["Date"].min()
    max_date = df["Date"].max()

    # Build the boundary grid
    boundary_gw_pairs = _build_boundaries(min_date, max_date)

    intervals = pd.DataFrame(boundary_gw_pairs, columns=["boundary", "gameweek"])
    intervals = intervals.sort_values("boundary").reset_index(drop=True)

    # Assign gameweeks using backward merge (each match gets the GW whose
    # boundary is the latest one that is <= the match date/time)
    df = df.sort_values("Date")
    df = pd.merge_asof(
        df,
        intervals,
        left_on="Date",
        right_on="boundary",
        direction="backward",
    )

    # Handle any dates that fell before the earliest boundary (forward fill)
    if df["gameweek"].isna().any():
        df_unassigned = df[df["gameweek"].isna()].copy()
        df_assigned = pd.merge_asof(
            df_unassigned.sort_values("Date"),
            intervals,
            left_on="Date",
            right_on="boundary",
            direction="forward",
        )
        df.loc[df["gameweek"].isna(), "gameweek"] = df_assigned["gameweek"].values

    df["Game Week"] = df["gameweek"].astype(int)
    df.drop(columns=["boundary", "gameweek"], inplace=True, errors="ignore")

    return df


def prepare_ranking_display(df):
    """
    Prepare ranking columns for display in the grid.

    Creates both a sortable integer column and a display-friendly string column
    where missing ranks show as "-".

    Args:
        df: DataFrame with 'Domestic League Ranking' column

    Returns:
        DataFrame with 'Rank_Sort' and 'Rank_Display' columns added
    """
    df["Rank_Sort"] = df["Domestic League Ranking"].fillna(9999).astype(int)
    df["Rank_Display"] = df["Domestic League Ranking"].apply(
        lambda x: "-" if pd.isna(x) else str(int(x))
    )
    return df
