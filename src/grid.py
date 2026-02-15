from st_aggrid import GridOptionsBuilder, JsCode


def create_cell_style_js(center, color_scheme, opacity):
    """
    Create JavaScript code for dynamic cell styling based on difficulty values.
    
    Args:
        center: The neutral difficulty value
        color_scheme: Dictionary with 'easy', 'hard', and 'neutral' RGB tuples
        opacity: Multiplier for color intensity
        
    Returns:
        JsCode object for cell styling
    """
    easy = color_scheme["easy"]
    hard = color_scheme["hard"]
    neutral = color_scheme["neutral"]

    return JsCode(f"""
    function(params) {{
        const v = params.data[params.colDef.field + "__val"];

        let style = {{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontWeight: "500",
            fontSize: "clamp(0.7rem, 2vw, 0.95rem)"
        }};

        if (v == null || isNaN(v)) {{
            style.background = "#fafafa";
            style.color = "#adb5bd";
            return style;
        }}

        const dev = (v - {center}) / {center};
        const n = Math.max(-1, Math.min(1, dev)) * {opacity};

        function lerp(a,b,f) {{ return Math.round(a + (b-a)*f); }}

        let r,g,b;
        if (n >= 0) {{
            r = lerp({neutral[0]}, {easy[0]}, n);
            g = lerp({neutral[1]}, {easy[1]}, n);
            b = lerp({neutral[2]}, {easy[2]}, n);
        }} else {{
            const a = Math.abs(n);
            r = lerp({neutral[0]}, {hard[0]}, a);
            g = lerp({neutral[1]}, {hard[1]}, a);
            b = lerp({neutral[2]}, {hard[2]}, a);
        }}

        style.background = `rgb(${{r}},${{g}},${{b}})`;
        style.color = (r*299+g*587+b*114)/1000 > 128 ? "#212529" : "#fff";
        return style;
    }}
    """)


def configure_grid(grid_df, gw_columns, cell_style_js):
    """
    Configure AG Grid options for the opponent difficulty table.
    
    Args:
        grid_df: DataFrame to display
        gw_columns: List of gameweek column names
        cell_style_js: JsCode for cell styling
        
    Returns:
        Dictionary of grid options
    """
    gb = GridOptionsBuilder.from_dataframe(grid_df)

    # Configure pinned columns with mobile-friendly widths
    gb.configure_column(
        "Rank", 
        pinned="left", 
        width=60,
        minWidth=50,
        maxWidth=80,
        headerName="Rank",
        cellStyle={'textAlign': 'center', 'fontWeight': '600'}
    )
    
    gb.configure_column("Rank_Sort", hide=True)
    
    gb.configure_column(
        "Name", 
        pinned="left", 
        width=180,
        minWidth=120,
        maxWidth=250,
        headerName="Team",
        cellStyle={'fontWeight': '600', 'paddingLeft': '8px'}
    )

    # Configure gameweek columns with mobile-friendly widths
    for col in gw_columns + ["Avg"]:
        header_name = "Avg" if col == "Avg" else col
        
        gb.configure_column(
            col,
            headerName=header_name,
            tooltipField=f"{col}__tip",
            cellStyle=cell_style_js,
            width=90,
            minWidth=70,
            maxWidth=120,
            headerClass="ag-center-header"
        )
        gb.configure_column(f"{col}__val", hide=True)
        gb.configure_column(f"{col}__tip", hide=True)

    # Grid-level options optimized for mobile
    gb.configure_grid_options(
        tooltipShowDelay=0,
        animateRows=True,
        rowHeight=40,
        headerHeight=45,
        suppressMenuHide=True,
        enableCellTextSelection=True,
        ensureDomOrder=True,
        suppressHorizontalScroll=False,
        alwaysShowHorizontalScroll=False,
        # Add selection options
        rowSelection='multiple',
        suppressRowClickSelection=False,
        enableRangeSelection=True
    )

    # Configure default column properties
    gb.configure_default_column(
        resizable=True,
        sortable=True,
        filter=False
    )

    return gb.build()