def create_pivot_tables(df, metric):
    """
    Create pivot tables for values, labels, and opponents.
    
    Args:
        df: Filtered DataFrame with match data
        metric: The difficulty metric to use ('Score_mean' or 'Score_median')
        
    Returns:
        Tuple of (value_pivot, label_pivot, opponent_pivot) DataFrames
    """
    # Create cell labels with score and home/away indicator
    df["CellLabel"] = df.apply(
        lambda r: f"{round(r[metric],1)} ({r['HA']})" if r[metric] == r[metric] else "",
        axis=1
    )

    pivot_index = ["Rank_Sort", "Name"]

    # Create separate pivots for values, labels, and opponents
    value_pivot = df.pivot_table(
        values=metric, 
        index=pivot_index, 
        columns="Game Week",  # Changed from "Gameweek"
        aggfunc="first"
    )
    
    label_pivot = df.pivot_table(
        values="CellLabel", 
        index=pivot_index, 
        columns="Game Week",  # Changed from "Gameweek"
        aggfunc="first"
    ).fillna("")
    
    opponent_pivot = df.pivot_table(
        values="Opponent", 
        index=pivot_index, 
        columns="Game Week",  # Changed from "Gameweek"
        aggfunc="first"
    ).fillna("")

    # Calculate row averages
    row_avg = value_pivot.mean(axis=1)

    # Add average column to all pivots
    value_pivot["Avg"] = row_avg
    label_pivot["Avg"] = row_avg.round(1).astype(str)
    opponent_pivot["Avg"] = ""

    return value_pivot, label_pivot, opponent_pivot


def prepare_grid_dataframe(value_pivot, label_pivot, opponent_pivot, rank_df, gameweeks):
    """
    Prepare the final DataFrame for AG Grid display.
    
    Args:
        value_pivot: Pivot table with difficulty values
        label_pivot: Pivot table with formatted labels
        opponent_pivot: Pivot table with opponent names
        rank_df: DataFrame with ranking information
        gameweeks: List of selected gameweeks
        
    Returns:
        Tuple of (grid_df, gw_columns) where grid_df is ready for display
        and gw_columns is the list of gameweek column names
    """
    # Create gameweek column names
    gw_columns = [f"GW {gw}" for gw in gameweeks]
    mapping = dict(zip(gameweeks, gw_columns))

    # Rename columns in all pivots
    value_pivot.rename(columns=mapping, inplace=True)
    label_pivot.rename(columns=mapping, inplace=True)
    opponent_pivot.rename(columns=mapping, inplace=True)

    # Define column order
    ordered = gw_columns + ["Avg"]

    # Reorder columns
    value_pivot = value_pivot[ordered]
    label_pivot = label_pivot[ordered]
    opponent_pivot = opponent_pivot[ordered]

    # Start with label pivot as the base grid DataFrame
    grid_df = label_pivot.reset_index()

    # Merge with ranking display information
    grid_df = grid_df.merge(
        rank_df[["Rank_Sort", "Name", "Rank_Display"]].drop_duplicates(),
        on=["Rank_Sort", "Name"],
        how="left"
    ).rename(columns={"Rank_Display": "Rank"})

    # Add hidden columns for values and tooltips
    for col in ordered:
        grid_df[f"{col}__val"] = value_pivot.reset_index()[col]
        grid_df[f"{col}__tip"] = opponent_pivot.reset_index()[col]

    return grid_df, gw_columns
