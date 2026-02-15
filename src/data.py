import pandas as pd
import streamlit as st
from src.config import COMPETITION_NAMES, SORARE_COMPETITION_MAPPING


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
    df["Sorare_Competition"] = df["Competition_Display"].map(SORARE_COMPETITION_MAPPING).fillna("Other")

    # Map location to H/A abbreviation
    df["HA"] = df["Location"].map({"Home": "H", "Away": "A"}).fillna("")

    return df


def calculate_gameweeks(df):
    """
    Calculate gameweek numbers based on match dates.
    
    Uses the 'Game Week' column from CSV to determine the starting gameweek,
    then applies Friday-to-Thursday week definition with 4-day and 3-day periods
    alternating to align with typical match schedules.
    
    Args:
        df: DataFrame with 'Date' column and 'Game Week' column from CSV
        
    Returns:
        DataFrame with 'Game Week' column calculated
    """
    if df.empty or df["Date"].isna().all():
        df["Game Week"] = pd.NA
        return df

    # Check if Game Week column exists and find the minimum value
    if "Game Week" not in df.columns:
        st.error("❌ 'Game Week' column not found in the CSV file.")
        st.stop()
    
    # Convert Game Week to numeric and find minimum (ignoring NaN values)
    game_week_values = pd.to_numeric(df["Game Week"], errors="coerce")
    valid_gameweeks = game_week_values.dropna()
    
    if valid_gameweeks.empty:
        st.error("❌ No valid Game Week values found in the CSV file.")
        st.stop()
    
    min_game_week = valid_gameweeks.min()
    
    # Calculate the starting gameweek (min - 604)
    starting_gameweek = int(min_game_week - 604)

    # Find the first Friday at 3 PM before the earliest match
    min_date = df["Date"].min()
    start_boundary = min_date.normalize() + pd.Timedelta(hours=15)

    days_since_friday = (start_boundary.weekday() - 4) % 7
    start_boundary -= pd.Timedelta(days=days_since_friday)

    if start_boundary > min_date:
        start_boundary -= pd.Timedelta(days=7)

    # Generate gameweek boundaries with alternating 4/3 day periods
    max_date = df["Date"].max()
    boundaries = [start_boundary]
    periods = [pd.Timedelta(days=4), pd.Timedelta(days=3)]

    while boundaries[-1] <= max_date + pd.Timedelta(days=7):
        boundaries.append(boundaries[-1] + periods[len(boundaries) % 2])

    # Create intervals dataframe starting from the calculated starting gameweek
    intervals = pd.DataFrame({
        "boundary": boundaries[:-1],
        "gameweek": range(starting_gameweek, starting_gameweek + len(boundaries) - 1)
    })

    # Assign gameweeks using backward merge
    df = df.sort_values("Date")
    df = pd.merge_asof(
        df,
        intervals,
        left_on="Date",
        right_on="boundary",
        direction="backward"
    )

    # Handle any unassigned dates with forward merge
    if df["gameweek"].isna().any():
        df_unassigned = df[df["gameweek"].isna()]
        df_assigned = pd.merge_asof(
            df_unassigned.sort_values("Date"),
            intervals,
            left_on="Date",
            right_on="boundary",
            direction="forward"
        )
        df.loc[df["gameweek"].isna(), "gameweek"] = df_assigned["gameweek"].values

    # Convert to integer and rename to "Game Week", cleanup
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
