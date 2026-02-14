import pandas as pd
import streamlit as st
from src.config import COMPETITION_NAMES


@st.cache_data
def load_and_prepare_data(file_path):
    df = pd.read_csv(file_path)

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)

    numeric_cols = ["Domestic League Ranking", "Score_mean", "Score_median"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Competition_Display"] = df["Comp_Slug"].map(COMPETITION_NAMES).fillna(
        df["name (upcomingGames.competition)"]
    )

    df["HA"] = df["Location"].map({"Home": "H", "Away": "A"}).fillna("")

    return df


def calculate_gameweeks(df):
    if df.empty or df["Date"].isna().all():
        df["Gameweek"] = pd.NA
        return df

    min_date = df["Date"].min()
    start_boundary = min_date.normalize() + pd.Timedelta(hours=15)

    days_since_friday = (start_boundary.weekday() - 4) % 7
    start_boundary -= pd.Timedelta(days=days_since_friday)

    if start_boundary > min_date:
        start_boundary -= pd.Timedelta(days=7)

    max_date = df["Date"].max()
    boundaries = [start_boundary]
    periods = [pd.Timedelta(days=4), pd.Timedelta(days=3)]

    while boundaries[-1] <= max_date + pd.Timedelta(days=7):
        boundaries.append(boundaries[-1] + periods[len(boundaries) % 2])

    intervals = pd.DataFrame({
        "boundary": boundaries[:-1],
        "gameweek": range(1, len(boundaries))
    })

    df = df.sort_values("Date")
    df = pd.merge_asof(
        df,
        intervals,
        left_on="Date",
        right_on="boundary",
        direction="backward"
    )

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

    df["Gameweek"] = df["gameweek"].astype(int)
    df.drop(columns=["boundary", "gameweek"], inplace=True, errors="ignore")

    return df


def prepare_ranking_display(df):
    df["Rank_Sort"] = df["Domestic League Ranking"].fillna(9999).astype(int)
    df["Rank_Display"] = df["Domestic League Ranking"].apply(
        lambda x: "-" if pd.isna(x) else str(int(x))
    )
    return df
