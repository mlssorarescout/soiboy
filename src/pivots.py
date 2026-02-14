def create_pivot_tables(df, metric):

    df["CellLabel"] = df.apply(
        lambda r: f"{round(r[metric],1)} ({r['HA']})" if r[metric] == r[metric] else "",
        axis=1
    )

    pivot_index = ["Rank_Sort", "Name"]

    value_pivot = df.pivot_table(values=metric, index=pivot_index, columns="Gameweek", aggfunc="first")
    label_pivot = df.pivot_table(values="CellLabel", index=pivot_index, columns="Gameweek", aggfunc="first").fillna("")
    opponent_pivot = df.pivot_table(values="Opponent", index=pivot_index, columns="Gameweek", aggfunc="first").fillna("")

    row_avg = value_pivot.mean(axis=1)

    value_pivot["Avg"] = row_avg
    label_pivot["Avg"] = row_avg.round(1).astype(str)
    opponent_pivot["Avg"] = ""

    return value_pivot, label_pivot, opponent_pivot


def prepare_grid_dataframe(value_pivot, label_pivot, opponent_pivot, rank_df, gameweeks):

    gw_columns = [f"GW {gw}" for gw in gameweeks]
    mapping = dict(zip(gameweeks, gw_columns))

    value_pivot.rename(columns=mapping, inplace=True)
    label_pivot.rename(columns=mapping, inplace=True)
    opponent_pivot.rename(columns=mapping, inplace=True)

    ordered = gw_columns + ["Avg"]

    value_pivot = value_pivot[ordered]
    label_pivot = label_pivot[ordered]
    opponent_pivot = opponent_pivot[ordered]

    grid_df = label_pivot.reset_index()

    grid_df = grid_df.merge(
        rank_df[["Rank_Sort", "Name", "Rank_Display"]].drop_duplicates(),
        on=["Rank_Sort", "Name"],
        how="left"
    ).rename(columns={"Rank_Display": "Rank"})

    for col in ordered:
        grid_df[f"{col}__val"] = value_pivot.reset_index()[col]
        grid_df[f"{col}__tip"] = opponent_pivot.reset_index()[col]

    return grid_df, gw_columns
