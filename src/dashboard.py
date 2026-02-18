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
from src.player_data import load_player_data, normalize_strength_metrics, filter_players_by_gameweeks, calculate_soi, calculate_dynamic_fixture_difficulty
from src.player_grid import create_strength_cell_style_js, configure_player_grid, prepare_player_grid_data
from src.matchup_cohesion import (
    find_best_matchup_cohesions,
    prepare_cohesion_display_df,
    create_matchup_detail_grid
)


def main():
    # Header section with better formatting
    st.markdown("# ⚽ Opponent Difficulty Dashboard")
    st.markdown("### Analyze fixture difficulty across competitions and gameweeks")
    
    # Get last updated timestamp from data file
    import os
    from datetime import datetime
    try:
        data_mtime = os.path.getmtime(DATA_PATH)
        last_updated = datetime.fromtimestamp(data_mtime).strftime("%B %d, %Y at %I:%M %p")
        st.markdown(f"*Last Updated: {last_updated}*")
    except:
        pass
    
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
        # Don't normalize yet - will do it after filtering
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
        
        # Calculate dynamic fixture difficulty based on team fixture data and selected gameweeks
        players_filtered = calculate_dynamic_fixture_difficulty(
            players_filtered,
            df,
            selected_gameweeks,
            selected_competitions,
            metric
        )
        
        # Normalize strength metrics based on filtered player pool (percentile within filters)
        players_filtered = normalize_strength_metrics(players_filtered)
        
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
    
    # ============================================================
    # MATCHUP COHESION DASHBOARD (THIRD DASHBOARD)
    # ============================================================
    
    st.markdown("---")
    
    st.markdown("## 🔄 Matchup Cohesion Analysis")
    st.markdown("### Find complementary team matchups")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Standalone Position Filter for Cohesion (independent from sidebar)
    # Use df instead of df_filtered to get all positions, not just sidebar-filtered ones
    all_positions_cohesion = sorted(df[df["Sorare_Competition"] == selected_sorare_comp]["Position"].dropna().unique())
    
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        cohesion_positions = st.multiselect(
            "📍 Position(s) to Analyze",
            all_positions_cohesion,
            default=all_positions_cohesion,
            help="Select one or more positions for matchup analysis (independent from sidebar filter)",
            key="cohesion_positions"
        )
    
    with col_filter2:
        min_both_play = st.slider(
            "🎯 Min % Both Teams Play",
            min_value=0,
            max_value=100,
            value=0,
            step=10,
            help="Filter to only show teams that play together in at least this % of gameweeks",
            key="cohesion_min_both_play"
        )
    
    if not cohesion_positions:
        st.warning("⚠️ Please select at least one position to analyze.")
    else:
        # Filter data for cohesion analysis using the cohesion-specific position filter
        # Start with data already filtered by Sorare Competition and Competitions
        df_cohesion = df_sorare_filtered[
            (df_sorare_filtered["Competition_Display"].isin(selected_competitions)) &
            (df_sorare_filtered["Position"].isin(cohesion_positions)) &
            (df_sorare_filtered["Game Week"].isin(selected_gameweeks))
        ]
        
        # Get all teams from the cohesion-filtered data
        available_teams = sorted(df_cohesion["Name"].unique())
        
        if len(available_teams) < 2:
            st.info("ℹ️ Need at least 2 teams to analyze matchup cohesion.")
        else:
            # Team selection
            col1, col2 = st.columns([3, 1])
            
            with col1:
                primary_team = st.selectbox(
                    "🎯 Select Primary Team",
                    available_teams,
                    help="Choose the team to find matchup partners for",
                    key="cohesion_primary_team"
                )
            
            with col2:
                top_n = st.number_input(
                    "Top N Partners",
                    min_value=5,
                    max_value=50,
                    value=15,
                    step=5,
                    help="Number of best matchup partners to show"
                )
            
            # Info box explaining the scoring
            with st.expander("ℹ️ How Cohesion Score is Calculated", expanded=False):
                position_text = ", ".join(cohesion_positions) if len(cohesion_positions) > 1 else cohesion_positions[0]
                st.markdown(f"""
                **Analyzing Position(s): {position_text}**
                
                **Cohesion Score Formula:**
                ```
                Score = (Both Play % × 20%) + (Both Home % × 40%) + (Fixture Difficulty Percentile × 40%)
                ```
                
                **Column Definitions:**
                - **Rank**: Teams ranked by cohesion score (higher is better)
                - **Team Match**: The partner team being evaluated
                - **Position**: Position(s) being analyzed
                - **Both Play %**: Percentage of selected gameweeks where both teams have a match
                - **Both Home %**: Percentage of PRIMARY team's home games where partner is also home
                - **Fixture Difficulty Percentile**: Percentile rank of combined difficulty across ALL teams in filters (higher = easier fixtures)
                - **Cohesion Score**: Overall matchup quality (0-100, higher is better)
                
                **Weights Explanation:**
                - Both Home % gets the most weight (40%) because having coverage for your home games is crucial
                - Fixture Difficulty Percentile also weighted heavily (40%) - compares against all teams in your filters
                - Both Play % weighted lower (20%) - overlap is less important than quality
                
                **Both Home % Explanation:**
                If your selected team has 2 home games in the upcoming gameweeks, and a partner team 
                also has home games in both those same gameweeks, they would show 100% Both Home %.
                This helps you find teams that give you options when your primary team plays at home.
                
                **Fixture Difficulty Percentile Explanation:**
                This percentile is calculated across ALL teams in your sidebar filters (Sorare Competition, 
                Competitions, and Gameweeks), not just the teams shown in the cohesion table. A 75th percentile 
                means the team pair has easier fixtures than 75% of all possible team combinations.
                
                **Filters:**
                - **Min % Both Teams Play**: Only shows teams that play together in at least this % of gameweeks
                - **Positions**: Completely independent from sidebar position filter - analyze any positions
                """)
            
            # Calculate matchup cohesions
            with st.spinner("Calculating matchup cohesion..."):
                cohesion_df = find_best_matchup_cohesions(
                    df_cohesion,
                    df_cohesion,  # Pass full cohesion dataframe for percentile calculation
                    primary_team,
                    selected_gameweeks,
                    metric,
                    cohesion_positions,
                    top_n=top_n,
                    min_both_play_pct=min_both_play
                )
            
            if cohesion_df.empty:
                st.info(f"ℹ️ No teams found matching the criteria (min {min_both_play}% both play). Try lowering the minimum threshold.")
            else:
                # Display summary metrics in cards
                st.markdown("### 📊 Summary Metrics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    best_score = cohesion_df["cohesion_score"].max()
                    st.metric(
                        "Best Cohesion Score", 
                        f"{best_score:.1f}",
                        help="Highest cohesion score found"
                    )
                
                with col2:
                    avg_both_home = cohesion_df["both_home_pct"].mean()
                    st.metric(
                        "Avg Both Home %", 
                        f"{avg_both_home:.0f}%",
                        help="Average % of primary team's home games where partner is also home"
                    )
                
                with col3:
                    avg_both_play = cohesion_df["both_play_pct"].mean()
                    st.metric(
                        "Avg Both Play %", 
                        f"{avg_both_play:.0f}%",
                        help="Average percentage of gameweeks where both teams play"
                    )
                
                with col4:
                    avg_percentile = cohesion_df["difficulty_percentile"].mean()
                    st.metric(
                        "Avg Difficulty Percentile", 
                        f"{avg_percentile:.0f}%",
                        help="Average fixture difficulty percentile (higher is easier)"
                    )
                
                st.markdown("---")
                
                # Prepare display dataframe
                display_df = prepare_cohesion_display_df(cohesion_df)
                
                # Create styled dataframe with progress bars
                position_text = ", ".join(cohesion_positions) if len(cohesion_positions) > 1 else cohesion_positions[0]
                st.markdown("### 🎯 Matchup Cohesion Rankings")
                st.markdown(f"*Showing top {len(display_df)} partners for **{primary_team}** at **{position_text}***")
                
                if min_both_play > 0:
                    st.markdown(f"*Filtered to teams that play together in ≥{min_both_play}% of gameweeks*")
                
                # Display the dataframe with column configuration for better visualization
                cohesion_response = st.dataframe(
                    display_df,
                    column_config={
                        "Rank": st.column_config.NumberColumn(
                            "Rank",
                            help="Ranking by cohesion score",
                            format="%d",
                            width="small"
                        ),
                        "Team Match": st.column_config.TextColumn(
                            "Team Match",
                            help="Partner team name",
                            width="medium"
                        ),
                        "Position": st.column_config.TextColumn(
                            "Position",
                            help="Position(s) being analyzed",
                            width="medium"
                        ),
                        "Both Play %": st.column_config.ProgressColumn(
                            "Both Play %",
                            help="% of gameweeks where both teams play",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                            width="medium"
                        ),
                        "Both Home %": st.column_config.ProgressColumn(
                            "Both Home %",
                            help="% of primary team's home games where partner is also home",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                            width="medium"
                        ),
                        "Fixture Difficulty Percentile": st.column_config.ProgressColumn(
                            "Fixture Difficulty Percentile",
                            help="Percentile ranking of fixture difficulty (higher = easier)",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                            width="medium"
                        ),
                        "Cohesion Score": st.column_config.ProgressColumn(
                            "Cohesion Score",
                            help="Overall cohesion score (higher is better)",
                            format="%.1f",
                            min_value=0,
                            max_value=100,
                            width="medium"
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    height=500,
                    on_select="rerun",
                    selection_mode="multi-row"
                )
                
                # SOI Filter based on selected teams
                if player_df is not None and cohesion_response.selection.rows:
                    selected_indices = cohesion_response.selection.rows
                    selected_teams = display_df.iloc[selected_indices]["Team Match"].tolist()
                    
                    # Add primary team to the list
                    all_selected_teams = [primary_team] + selected_teams
                    
                    st.markdown("---")
                    st.markdown("## 👥 Sorare Opportunity Index - Filtered by Selected Teams")
                    st.markdown(f"### Players from: {', '.join(all_selected_teams)}")
                    
                    # Filter players by selected teams and cohesion positions  
                    players_filtered = filter_players_by_gameweeks(
                        player_df,
                        df,
                        selected_gameweeks,
                        selected_competitions,
                        cohesion_positions[0] if len(cohesion_positions) == 1 else position  # Use cohesion position if single, else sidebar
                    )
                    
                    # Filter by selected teams
                    players_filtered = players_filtered[players_filtered['Club'].isin(all_selected_teams)]
                    
                    # Calculate dynamic fixture difficulty based on team fixture data and selected gameweeks
                    players_filtered = calculate_dynamic_fixture_difficulty(
                        players_filtered,
                        df,
                        selected_gameweeks,
                        selected_competitions,
                        metric
                    )
                    
                    # Normalize strength metrics based on filtered player pool (percentile within filters)
                    players_filtered = normalize_strength_metrics(players_filtered)
                    
                    # Calculate SOI with user-defined weights
                    players_filtered = calculate_soi(players_filtered, soi_weights)
                    
                    if players_filtered.empty:
                        st.info("ℹ️ No players found for the selected teams and filters.")
                    else:
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