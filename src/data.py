import pandas as pd
import streamlit as st
from src.config import COMPETITION_NAMES


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

    # Map location to H/A abbreviation
    df["HA"] = df["Location"].map({"Home": "H", "Away": "A"}).fillna("")

    return df


def calculate_gameweeks(df):
    """
    Process gameweek numbers from the CSV file.
    
    Uses the existing 'Gameweek' column from the CSV, normalizing it by
    finding the minimum gameweek value and adjusting all values relative to it,
    so gameweeks start from 1.
    
    Args:
        df: DataFrame with 'Gameweek' column from CSV
        
    Returns:
        DataFrame with normalized 'Gameweek' column (starting from 1)
    """
    if df.empty:
        df["Gameweek"] = pd.NA
        return df
    
    # Check if Gameweek column exists in the CSV
    if "Gameweek" not in df.columns:
        st.error("❌ 'Gameweek' column not found in the CSV file.")
        st.stop()
    
    # Convert Gameweek to numeric, handling any non-numeric values
    df["Gameweek"] = pd.to_numeric(df["Gameweek"], errors="coerce")
    
    # Remove rows with invalid gameweek values
    if df["Gameweek"].isna().any():
        invalid_count = df["Gameweek"].isna().sum()
        st.warning(f"⚠️ Removed {invalid_count} rows with invalid Gameweek values.")
        df = df[df["Gameweek"].notna()].copy()
    
    if df.empty:
        st.error("❌ No valid gameweek data found in the file.")
        st.stop()
    
    # Find the minimum gameweek value in the file
    min_gameweek = df["Gameweek"].min()
    
    # Normalize gameweeks to start from 1
    # This subtracts the minimum and adds 1, so if min is 605, gameweeks become 1, 2, 3...
    df["Gameweek"] = (df["Gameweek"] - min_gameweek + 1).astype(int)
    
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
