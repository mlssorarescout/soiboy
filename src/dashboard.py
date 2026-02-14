import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

from src.config import (
    DATA_PATH,
    DIFFICULTY_CENTER,
    DIFFICULTY_COLORS,
    COLOR_OPACITY
)

from src.data import load_and_prepare_data, calculate_gameweeks, prepare_ranking_display
from src.pivots import create_pivot_tables, prepare_grid_dataframe
from src.grid import create_cell_style_js, configure_grid


def main():

    st.markdown("# ? Opponent Difficulty Dashboard")
    st.markdown("### Analyze fixture difficulty across competitions and gameweeks")
    st.markdown("<hr>", unsafe_allow_html=True)

    df = load_and_prepare_data(DATA_PATH)
    df = calculate_gameweeks(df)
    df = prepare_ranking_display(df)

    st.sidebar.markdown("## ?? Filters")

    competition = st.sidebar.selectbox(
        "Competition",
        sorted(df["Competition_Display"].dropna().unique())
    )

    df_filtered = df[df["Competition_Display"] == competition]

    position = st.sidebar.selectbox(
        "Position",
        sorted(df_filtered["Position"].dropna().unique())
    )

    df_filtered = df_filtered[df_filtered["Position"] == position]

    metric = st.sidebar.radio(
        "Metric",
        ["Score_mean", "Score_median"],
        format_func=lambda x: x.replace("_", " ").title()
    )

    gameweeks = sorted(df_filtered["Gameweek"].unique())

    selected_gameweeks = st.sidebar.multiselect(
        "Gameweeks",
        gameweeks,
        default=gameweeks,
        format_func=lambda x: f"GW {x}"
    )

    df_filtered = df_filtered[df_filtered["Gameweek"].isin(selected_gameweeks)]

    value_pivot, label_pivot, opponent_pivot = create_pivot_tables(df_filtered, metric)

    grid_df, gw_columns = prepare_grid_dataframe(
        value_pivot,
        label_pivot,
        opponent_pivot,
        df_filtered,
        selected_gameweeks
    )

    cell_js = create_cell_style_js(
        DIFFICULTY_CENTER,
        DIFFICULTY_COLORS,
        COLOR_OPACITY
    )

    grid_options = configure_grid(grid_df, gw_columns, cell_js)

    AgGrid(
        grid_df,
        gridOptions=grid_options,
        height=720,
        allow_unsafe_jscode=True,
        theme="streamlit"
    )

    export_df = grid_df[["Rank", "Name"] + gw_columns + ["Avg"]]

    st.download_button(
        "Download CSV",
        export_df.to_csv(index=False).encode(),
        "opponent_difficulty.csv"
    )
