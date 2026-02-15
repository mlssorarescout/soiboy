import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

from src.config import (
    DATA_PATH,
    PLAYER_DATA_PATH,
    DIFFICULTY_CENTER,
    DIFFICULTY_COLORS,
    COLOR_OPACITY,
    STRENGTH_CENTER,
    STRENGTH_COLORS,
    STRENGTH_OPACITY
)

from src.data import load_and_prepare_data, calculate_gameweeks, prepare_ranking_display
from src.pivots import create_pivot_tables, prepare_grid_dataframe
from src.grid import create_cell_style_js, configure_grid
from src.player_data import load_player_data, normalize_strength_metrics, filter_players_by_gameweeks, calculate_soi
from src.player_grid import create_strength_cell_style_js, configure_player_grid, prepare_player_grid_data


def main():
    # Header section with better formatting
    st.markdown("# ⚽ Opponent Difficulty Dashboard")
    st.markdown("### Analyze fixture difficulty across competitions and gameweeks")
    st.markdown("<hr>", unsafe_allow_html=True)

    # Load and prepare fixture data
    try:
        df = load_and_prepare_data(DATA_PATH)
        df = calculate_gameweeks(df)
        df = prepare_ranking_display(df)
    except FileNotFoundError:
        st.error(f"❌ Data file not found at: {DATA_PATH}")
        st.info("💡 Please ensure the CSV file is in the correct location.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

    # Load player data
    try:
        player_df = load_player_data(PLAYER_DATA_PATH)
        player_df = normalize_strength_metrics(player_df)
    except FileNotFoundError:
        st.warning(f"⚠️ Player data file not found at: {PLAYER_DATA_PATH}")
        st.info("💡 Player strength analysis will be unavailable.")
        player_df = None
    except Exception as e:
        st.warning(f"⚠️ Error loading player data: {str(e)}")
        player_df = None

    # Sidebar filters with icons
    st.sidebar.markdown("## 🎯 Filters")

    # Sorare Competition filter (first level - single select)
    sorare_competitions = sorted(df["Sorare_Competition"].dropna().unique())
    
    # Set default to Contender if available, otherwise first option
    default_sorare = "Contender" if "Contender" in sorare_competitions else sorare_competitions[0]
    default_index = sorare_competitions.index(default_sorare)
    
    selected_sorare_comp = st.sidebar.selectbox(
        "🏆 Sorare Competition",
        sorare_competitions,
        index=default_index,
        help="Filter by Sorare competition group"
    )
    
    # Filter data by Sorare Competition
    df_sorare_filtered = df[df["Sorare_Competition"] == selected_sorare_comp]

    # Competition filter (multi-select, filtered by Sorare Competition)
    available_competitions = sorted(df_sorare_filtered["Competition_Display"].dropna().unique())
    selected_competitions = st.sidebar.multiselect(
        "⚽ Competition",
        available_competitions,
        default=available_competitions,
        help="Select competitions to analyze"
    )
    
    if not selected_competitions:
        st.warning("⚠️ Please select at least one competition.")
        st.stop()

    df_filtered = df_sorare_filtered[df_sorare_filtered["Competition_Display"].isin(selected_competitions)]

    # Position filter
    positions = sorted(df_filtered["Position"].dropna().unique())
    position = st.sidebar.selectbox(
        "👤 Position",
        positions,
        help="Filter by player position"
    )

    df_filtered = df_filtered[df_filtered["Position"] == position]

    # Metric selection
    metric = st.sidebar.radio(
        "📊 Metric",
        ["Score_mean", "Score_median"],
        format_func=lambda x: x.replace("_", " ").title(),
        help="Choose between mean or median difficulty scores"
    )

    # Gameweek selection
    gameweeks = sorted(df_filtered["Game Week"].unique())

    st.sidebar.markdown("---")
    
    selected_gameweeks = st.sidebar.multiselect(
        "📅 Gameweeks",
        gameweeks,
        default=gameweeks,
        format_func=lambda x: f"GW {x}",
        help="Select which gameweeks to display"
    )

    if not selected_gameweeks:
        st.warning("⚠️ Please select at least one gameweek to display.")
        st.stop()
    
    # SOI Weight Configuration (only show if player data is available)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚖️ SOI Weights")
    
    soi_weights = {
        "l5_form": st.sidebar.slider(
            "L5 Form Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.05,
            help="Weight for Last 5 games form"
        ),
        "l15_form": st.sidebar.slider(
            "L15 Form Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.4,
            step=0.05,
            help="Weight for Last 15 games form"
        ),
        "next_5_diff": st.sidebar.slider(
            "Next 5 Diff Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.05,
            help="Weight for upcoming opponent difficulty"
        ),
        "l5_mins": st.sidebar.slider(
            "L5 Minutes Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.05,
            help="Weight for Last 5 games minutes"
        ),
        "l15_mins": st.sidebar.slider(
            "L15 Minutes Weight",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.05,
            help="Weight for Last 15 games minutes"
        )
    }
    
    # Show total weight
    total_weight = sum(soi_weights.values())
    if abs(total_weight - 1.0) > 0.01:
        st.sidebar.warning(f"⚠️ Weights sum to {total_weight:.2f} (should be 1.0)")
    else:
        st.sidebar.success(f"✅ Weights sum to {total_weight:.2f}")

    df_filtered = df_filtered[df_filtered["Game Week"].isin(selected_gameweeks)]

    # Create pivot tables
    value_pivot, label_pivot, opponent_pivot = create_pivot_tables(df_filtered, metric)

    # Prepare grid dataframe
    grid_df, gw_columns = prepare_grid_dataframe(
        value_pivot,
        label_pivot,
        opponent_pivot,
        df_filtered,
        selected_gameweeks
    )

    # Create cell styling
    cell_js = create_cell_style_js(
        DIFFICULTY_CENTER,
        DIFFICULTY_COLORS,
        COLOR_OPACITY
    )

    # Configure grid options
    grid_options = configure_grid(grid_df, gw_columns, cell_js)

#    # Display metrics summary
#    col1, col2, col3 = st.columns(3)
#    with col1:
#        st.metric("Teams", len(grid_df))
#    with col2:
#        st.metric("Gameweeks", len(selected_gameweeks))
#    with col3:
#        avg_difficulty = grid_df["Avg__val"].mean()
#        st.metric("Avg Difficulty", f"{avg_difficulty:.1f}")

#    st.markdown("---")

    # Display the fixture grid
    st.markdown("### 📊 Team Fixture Difficulty")
    
    grid_height = 600  # Default height that works well on mobile

    grid_response = AgGrid(
        grid_df,
        gridOptions=grid_options,
        height=grid_height,
        allow_unsafe_jscode=True,
        theme="streamlit",
        update_mode="MODEL_CHANGED",
        fit_columns_on_grid_load=False,
        enable_enterprise_modules=False
    )
    
    # Get selected rows
    selected_rows = grid_response['selected_rows']

    # Export section for fixtures
    st.markdown("---")
    
    st.markdown("### 📥 Export Fixture Data")
    st.markdown("Download the fixture difficulty view as a CSV file.")
    
    export_df = grid_df[["Rank", "Name"] + gw_columns + ["Avg"]]
    
    st.download_button(
        "📊 Download Fixture CSV",
        export_df.to_csv(index=False).encode(),
        "opponent_difficulty.csv",
        "text/csv",
        help="Download the filtered fixture data as CSV"
    )
    
    # ============================================================
    # PLAYER STRENGTH DASHBOARD (SECOND DASHBOARD)
    # ============================================================
    
    if player_df is not None:
        st.markdown("---")
        
        st.markdown("## 👥 Sorare Opportunity Index")
        st.markdown("### Players from teams playing in selected gameweeks")
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Filter players by selected gameweeks and filters
        players_filtered = filter_players_by_gameweeks(
            player_df,
            df,
            selected_gameweeks,
            selected_competitions,
            position
        )
        
        # Further filter by selected teams if any rows are selected in the fixture grid
        if selected_rows is not None and len(selected_rows) > 0:
            selected_teams = selected_rows['Name'].tolist()
            st.info(f"🎯 Showing players from {len(selected_teams)} selected team(s)")
            players_filtered = players_filtered[players_filtered['Club'].isin(selected_teams)]
        
        # Calculate SOI with user-defined weights
        players_filtered = calculate_soi(players_filtered, soi_weights)
        
        if players_filtered.empty:
            st.info("ℹ️ No players found for the selected filters and gameweeks.")
        else:
            # Display player metrics summary
#            col1, col2, col3 = st.columns(3)
#            with col1:
#                st.metric("Players", len(players_filtered))
#            with col2:
#                avg_form = players_filtered["L5_Form_Display"].mean()
#                st.metric("Avg L5 Form", f"{avg_form:.2f}")
#            with col3:
#                avg_soi = players_filtered["SOI_Score"].mean()
#                st.metric("Avg SOI", f"{avg_soi:.2f}")
#            
#            st.markdown("---")
            
            # Prepare player grid
            player_grid_df, strength_cols = prepare_player_grid_data(players_filtered)
            
            # Create strength cell styling
            strength_cell_js = create_strength_cell_style_js(
                STRENGTH_CENTER,
                STRENGTH_COLORS,
                STRENGTH_OPACITY
            )
            
            # Configure player grid
            player_grid_options = configure_player_grid(
                player_grid_df,
                strength_cols,
                strength_cell_js,
                STRENGTH_COLORS,
                STRENGTH_OPACITY
            )
            
            # Display player grid
            AgGrid(
                player_grid_df,
                gridOptions=player_grid_options,
                height=500,
                allow_unsafe_jscode=True,
                theme="streamlit",
                update_mode="NO_UPDATE",
                fit_columns_on_grid_load=False
            )
            
            # Export section for players
            st.markdown("---")
            
            st.markdown("### 📥 Export Player Data")
            st.markdown("Download the player strength analysis as a CSV file.")
            
            player_export_df = players_filtered[[
                "displayName", "Club", "Position",
                "L5_Form_Display", "L15_Form_Display",
                "Next_5_Diff_Display",
                "L5_Mins_Display", "L15_Mins_Display",
                "SOI_Score"
            ]].copy()
            
            player_export_df.columns = [
                "Player", "Club", "Position",
                "L5 Form", "L15 Form",
                "Next 5 Diff",
                "L5 Minutes", "L15 Minutes",
                "SOI"
            ]
            
            st.download_button(
                "📊 Download Player CSV",
                player_export_df.to_csv(index=False).encode(),
                "player_strength.csv",
                "text/csv",
                help="Download the player strength data as CSV"
            )
    
    # Footer with color legend - stacked on mobile
    st.markdown("---")
    st.markdown("### 🎨 Color Legend")
    
    legend_col1, legend_col2, legend_col3 = st.columns(3)
    
    with legend_col1:
        st.markdown(
            '<div style="background-color: rgb(34, 197, 94); padding: 10px; '
            'border-radius: 8px; text-align: center; color: white; font-weight: 600; '
            'margin-bottom: 0.5rem;">'
            'Strong/Easy</div>',
            unsafe_allow_html=True
        )
    
    with legend_col2:
        st.markdown(
            '<div style="background-color: rgb(255, 255, 255); padding: 10px; '
            'border-radius: 8px; text-align: center; border: 1px solid #cbd5e1; '
            'font-weight: 600; margin-bottom: 0.5rem;">Neutral</div>',
            unsafe_allow_html=True
        )
    
    with legend_col3:
        st.markdown(
            '<div style="background-color: rgb(239, 68, 68); padding: 10px; '
            'border-radius: 8px; text-align: center; color: white; font-weight: 600; '
            'margin-bottom: 0.5rem;">'
            'Weak/Hard</div>',
            unsafe_allow_html=True
        )