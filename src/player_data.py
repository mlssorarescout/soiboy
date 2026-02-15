import pandas as pd
import streamlit as st
from src.config import STRENGTH_METRICS, DIFFICULTY_CENTER


@st.cache_data
def load_player_data(file_path):
    """
    Load and prepare player metrics data from CSV.
    
    Args:
        file_path: Path to the player metrics CSV file
        
    Returns:
        Prepared DataFrame with player metrics
    """
    df = pd.read_csv(file_path)
    
    # Convert numeric columns
    numeric_cols = [
        "averageScore", "Mean_Opp_Score", "Median_Opp_Score", "Count",
        "Last_5_Score_Running_Avg", "Last_15_Score_Running_Avg",
        "Last_5_Mins_Played_Running_Sum", "Last_15_Mins_Played_Running_Sum"
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    return df


def normalize_strength_metrics(df):
    """
    Normalize strength metrics to 0-1 scale with color coding.
    Handles NaN and infinite values gracefully.
    
    Args:
        df: DataFrame with raw player metrics
        
    Returns:
        DataFrame with normalized strength columns added
    """
    df = df.copy()
    
    # Last 5 Score Average / 70 (cap at 1)
    if "Last_5_Score_Running_Avg" in df.columns:
        df["L5_Form_Strength"] = (df["Last_5_Score_Running_Avg"] / 70).clip(upper=1.0)
        df["L5_Form_Strength"] = df["L5_Form_Strength"].replace([float('inf'), float('-inf')], float('nan'))
        df["L5_Form_Display"] = df["L5_Form_Strength"].round(2)
    
    # Last 15 Score Average / 70 (cap at 1)
    if "Last_15_Score_Running_Avg" in df.columns:
        df["L15_Form_Strength"] = (df["Last_15_Score_Running_Avg"] / 70).clip(upper=1.0)
        df["L15_Form_Strength"] = df["L15_Form_Strength"].replace([float('inf'), float('-inf')], float('nan'))
        df["L15_Form_Display"] = df["L15_Form_Strength"].round(2)
    
    # Mean Opponent Score / 60 (cap at 1) - INVERTED for Next 5 Difficulty
    if "Mean_Opp_Score" in df.columns:
        # Divide by 60 and cap at 1
        normalized = (df["Mean_Opp_Score"] / 60).clip(upper=1.0)
        # Invert: lower opponent score = easier = higher strength (1 - normalized)
        df["Next_5_Diff_Strength"] = (1 - normalized).clip(0, 1)
        df["Next_5_Diff_Strength"] = df["Next_5_Diff_Strength"].replace([float('inf'), float('-inf')], float('nan'))
        # Display as the inverted strength value (0-1), will be colored dynamically
        df["Next_5_Diff_Display"] = df["Next_5_Diff_Strength"].round(2)
    
    # Last 5 Minutes / 450 (cap at 1) - display as percentage
    if "Last_5_Mins_Played_Running_Sum" in df.columns:
        df["L5_Mins_Strength"] = (df["Last_5_Mins_Played_Running_Sum"] / 450).clip(upper=1.0)
        df["L5_Mins_Strength"] = df["L5_Mins_Strength"].replace([float('inf'), float('-inf')], float('nan'))
        # Display as percentage (0-100)
        df["L5_Mins_Display"] = (df["L5_Mins_Strength"] * 100).round(0)
    
    # Last 15 Minutes / 1350 (cap at 1) - display as percentage
    if "Last_15_Mins_Played_Running_Sum" in df.columns:
        df["L15_Mins_Strength"] = (df["Last_15_Mins_Played_Running_Sum"] / 1350).clip(upper=1.0)
        df["L15_Mins_Strength"] = df["L15_Mins_Strength"].replace([float('inf'), float('-inf')], float('nan'))
        # Display as percentage (0-100)
        df["L15_Mins_Display"] = (df["L15_Mins_Strength"] * 100).round(0)
    
    return df


def calculate_soi(df, weights):
    """
    Calculate Strength of Investment (SOI) score based on weighted metrics.
    
    Args:
        df: DataFrame with normalized strength metrics
        weights: Dictionary with weight values for each metric
        
    Returns:
        DataFrame with SOI_Score column added
    """
    df = df.copy()
    
    # Initialize SOI score
    df["SOI_Score"] = 0.0
    
    # Add weighted contributions (fill NaN with 0 for calculation)
    if "L5_Form_Strength" in df.columns:
        df["SOI_Score"] += df["L5_Form_Strength"].fillna(0) * weights["l5_form"]
    
    if "L15_Form_Strength" in df.columns:
        df["SOI_Score"] += df["L15_Form_Strength"].fillna(0) * weights["l15_form"]
    
    if "Next_5_Diff_Strength" in df.columns:
        df["SOI_Score"] += df["Next_5_Diff_Strength"].fillna(0) * weights["next_5_diff"]
    
    if "L5_Mins_Strength" in df.columns:
        df["SOI_Score"] += df["L5_Mins_Strength"].fillna(0) * weights["l5_mins"]
    
    if "L15_Mins_Strength" in df.columns:
        df["SOI_Score"] += df["L15_Mins_Strength"].fillna(0) * weights["l15_mins"]
    
    # Clip to 0-1 range
    df["SOI_Score"] = df["SOI_Score"].clip(0, 1)
    
    return df


def filter_players_by_gameweeks(player_df, fixture_df, selected_gameweeks, selected_competitions, position):
    """
    Filter players to only show those from teams playing in selected gameweeks.
    
    Args:
        player_df: DataFrame with player data
        fixture_df: DataFrame with fixture data (from first dashboard)
        selected_gameweeks: List of selected gameweek numbers
        selected_competitions: List of selected competition names
        position: Selected position
        
    Returns:
        Filtered DataFrame with only relevant players
    """
    # Get unique teams playing in selected gameweeks and competitions
    fixtures_filtered = fixture_df[
        (fixture_df["Game Week"].isin(selected_gameweeks)) &
        (fixture_df["Competition_Display"].isin(selected_competitions))
    ]
    
    playing_teams = set(fixtures_filtered["Name"].unique())
    
    # Filter players by position and team
    players_filtered = player_df[
        (player_df["Position"] == position) &
        (player_df["Club"].isin(playing_teams))
    ].copy()
    
    return players_filtered
