import pandas as pd
import numpy as np
import streamlit as st
from itertools import combinations


def calculate_team_avg_difficulty(df, team, gameweeks, metric):
    """
    Calculate average difficulty for a team across specified gameweeks.
    
    Args:
        df: Filtered dataframe with opponent difficulty data
        team: Team name
        gameweeks: List of gameweeks to analyze
        metric: Score_mean or Score_median
        
    Returns:
        Average difficulty score, or None if no data
    """
    team_data = df[(df["Name"] == team) & (df["Game Week"].isin(gameweeks))]
    if team_data.empty:
        return None
    return team_data[metric].mean()


def calculate_cohesion_score(df, team1, team2, gameweeks, metric, positions):
    """
    Calculate how well two teams' fixtures complement each other.
    
    Focuses on:
    - Percentage of gameweeks both teams play
    - Percentage of primary team's home games where partner is also home
    - Average difficulty score
    
    Args:
        df: Filtered dataframe with opponent difficulty data
        team1: First team name (primary team)
        team2: Second team name (partner team)
        gameweeks: List of gameweeks to analyze
        metric: Score_mean or Score_median
        positions: List of positions to analyze (can be multiple)
        
    Returns:
        Dictionary with cohesion metrics
    """
    # Filter by positions (multiple positions allowed)
    team1_data = df[(df["Name"] == team1) & 
                    (df["Game Week"].isin(gameweeks)) & 
                    (df["Position"].isin(positions))]
    team2_data = df[(df["Name"] == team2) & 
                    (df["Game Week"].isin(gameweeks)) & 
                    (df["Position"].isin(positions))]
    
    if team1_data.empty or team2_data.empty:
        return None
    
    # Get gameweeks each team plays
    team1_gws = set(team1_data["Game Week"].unique())
    team2_gws = set(team2_data["Game Week"].unique())
    
    # Calculate overlap
    overlap_gws = team1_gws & team2_gws
    
    # Column 4: % of selected gameweeks where both teams play
    both_play_pct = (len(overlap_gws) / len(gameweeks) * 100) if gameweeks else 0
    
    # Column 5: % of PRIMARY TEAM'S home games where partner is also home
    # Get gameweeks where team1 (primary) is home
    team1_home_gws = set(team1_data[team1_data["HA"] == "H"]["Game Week"].unique())
    
    # Count how many of team1's home games team2 is also home
    both_home_count = 0
    for gw in team1_home_gws:
        team2_gw_data = team2_data[team2_data["Game Week"] == gw]
        
        # Check if team2 has a home match in this gameweek
        if not team2_gw_data.empty and (team2_gw_data["HA"] == "H").any():
            both_home_count += 1
    
    # Calculate percentage based on primary team's home games
    both_home_pct = (both_home_count / len(team1_home_gws) * 100) if team1_home_gws else 0
    
    # Column 6: Average difficulty (combined average of both teams)
    team1_avg = team1_data[metric].mean()
    team2_avg = team2_data[metric].mean()
    combined_avg = (team1_avg + team2_avg) / 2
    
    # Calculate cohesion score with updated difficulty formula
    difficulty_score = combined_avg / 70 if combined_avg > 1 else 1
    
    cohesion_score = (
        both_play_pct * 0.20 +
        both_home_pct * 0.40 +
        difficulty_score * 0.40
    )
    
    # Get position string for display
    position_str = ", ".join(sorted(positions)) if len(positions) > 1 else positions[0]
    
    return {
        "team1": team1,
        "team2": team2,
        "position": position_str,
        "both_play_pct": both_play_pct,
        "both_home_pct": both_home_pct,
        "combined_avg_difficulty": combined_avg,
        "cohesion_score": cohesion_score,
        "overlap_count": len(overlap_gws),
        "both_home_count": both_home_count,
        "team1_home_count": len(team1_home_gws)
    }


def find_best_matchup_cohesions(df, primary_team, gameweeks, metric, positions, top_n=10, min_both_play_pct=0):
    """
    Find teams that best complement the primary team's fixture schedule.
    
    Args:
        df: Filtered dataframe with opponent difficulty data
        primary_team: The team to find complements for
        gameweeks: List of gameweeks to analyze
        metric: Score_mean or Score_median
        positions: List of positions to analyze
        top_n: Number of top matchups to return
        min_both_play_pct: Minimum percentage of gameweeks both teams must play (0-100)
        
    Returns:
        DataFrame with best matchup cohesion scores
    """
    all_teams = df[df["Position"].isin(positions)]["Name"].unique()
    other_teams = [t for t in all_teams if t != primary_team]
    
    cohesion_results = []
    
    for other_team in other_teams:
        result = calculate_cohesion_score(
            df, primary_team, other_team, gameweeks, metric, positions
        )
        if result and result["both_play_pct"] >= min_both_play_pct:
            cohesion_results.append(result)
    
    # Convert to dataframe and sort by cohesion score
    results_df = pd.DataFrame(cohesion_results)
    if results_df.empty:
        return results_df
    
    results_df = results_df.sort_values("cohesion_score", ascending=False).head(top_n)
    results_df = results_df.reset_index(drop=True)
    results_df["rank"] = range(1, len(results_df) + 1)
    
    return results_df


def create_matchup_detail_grid(df, primary_team, partner_team, gameweeks, metric, positions):
    """
    Create a detailed week-by-week comparison of two teams' fixtures.
    
    Args:
        df: Filtered dataframe with opponent difficulty data
        primary_team: First team
        partner_team: Second team
        gameweeks: List of gameweeks to analyze
        metric: Score_mean or Score_median
        positions: List of positions to analyze
        
    Returns:
        DataFrame with gameweek-by-gameweek comparison
    """
    detail_rows = []
    
    for gw in sorted(gameweeks):
        team1_data = df[(df["Name"] == primary_team) & 
                        (df["Game Week"] == gw) & 
                        (df["Position"].isin(positions))]
        team2_data = df[(df["Name"] == partner_team) & 
                        (df["Game Week"] == gw) & 
                        (df["Position"].isin(positions))]
        
        row = {"gameweek": gw}
        
        if not team1_data.empty:
            # Take first match if multiple positions
            row["team1_opponent"] = team1_data["Opponent"].iloc[0]
            row["team1_location"] = team1_data["HA"].iloc[0]
            row["team1_difficulty"] = team1_data[metric].mean()  # Average across positions
        else:
            row["team1_opponent"] = "-"
            row["team1_location"] = "-"
            row["team1_difficulty"] = None
            
        if not team2_data.empty:
            row["team2_opponent"] = team2_data["Opponent"].iloc[0]
            row["team2_location"] = team2_data["HA"].iloc[0]
            row["team2_difficulty"] = team2_data[metric].mean()  # Average across positions
        else:
            row["team2_opponent"] = "-"
            row["team2_location"] = "-"
            row["team2_difficulty"] = None
        
        # Determine if both home
        row["both_home"] = (row["team1_location"] == "H" and row["team2_location"] == "H")
        
        # Calculate the best choice for this gameweek
        if row["team1_difficulty"] is not None and row["team2_difficulty"] is not None:
            if row["team1_difficulty"] < row["team2_difficulty"]:
                row["best_choice"] = primary_team
                row["best_difficulty"] = row["team1_difficulty"]
            else:
                row["best_choice"] = partner_team
                row["best_difficulty"] = row["team2_difficulty"]
        elif row["team1_difficulty"] is not None:
            row["best_choice"] = primary_team
            row["best_difficulty"] = row["team1_difficulty"]
        elif row["team2_difficulty"] is not None:
            row["best_choice"] = partner_team
            row["best_difficulty"] = row["team2_difficulty"]
        else:
            row["best_choice"] = "-"
            row["best_difficulty"] = None
            
        detail_rows.append(row)
    
    return pd.DataFrame(detail_rows)


def prepare_cohesion_display_df(cohesion_df):
    """
    Prepare the cohesion results for display in the grid.
    
    Args:
        cohesion_df: DataFrame with cohesion scores
        
    Returns:
        DataFrame formatted for display with exactly 6 columns
    """
    if cohesion_df.empty:
        return pd.DataFrame()
    
    display_df = cohesion_df.copy()
    
    # Select and rename columns per specification
    display_df = display_df[[
        "rank",
        "team2",
        "position",
        "both_play_pct",
        "both_home_pct",
        "combined_avg_difficulty",
        "cohesion_score"
    ]]
    
    display_df.columns = [
        "Rank",
        "Team Match",
        "Position",
        "Both Play %",
        "Both Home %",
        "Avg Difficulty",
        "Cohesion Score"
    ]
    
    # Round numeric columns
    display_df["Both Play %"] = display_df["Both Play %"].round(1)
    display_df["Both Home %"] = display_df["Both Home %"].round(1)
    display_df["Avg Difficulty"] = display_df["Avg Difficulty"].round(1)
    display_df["Cohesion Score"] = display_df["Cohesion Score"].round(1)
    
    return display_df
