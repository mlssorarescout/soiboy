from st_aggrid import GridOptionsBuilder, JsCode


# ============================================================
# CELL STYLING HELPERS
# ============================================================

def create_strength_cell_style_js(center, color_scheme, opacity):
    strong = color_scheme["strong"]
    weak = color_scheme["weak"]
    neutral = color_scheme["neutral"]

    return JsCode(f"""
    function(params) {{
        const v = params.data[params.colDef.field + "__strength"];

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
        const n = Math.max(-1, Math.min(1, dev)) * 0.8;

        function lerp(a,b,f) {{ return Math.round(a + (b-a)*f); }}

        let r,g,b;
        if (n >= 0) {{
            r = lerp({neutral[0]}, {strong[0]}, n);
            g = lerp({neutral[1]}, {strong[1]}, n);
            b = lerp({neutral[2]}, {strong[2]}, n);
        }} else {{
            const a = Math.abs(n);
            r = lerp({neutral[0]}, {weak[0]}, a);
            g = lerp({neutral[1]}, {weak[1]}, a);
            b = lerp({neutral[2]}, {weak[2]}, a);
        }}

        style.background = `rgb(${{r}},${{g}},${{b}})`;
        style.color = (r*299+g*587+b*114)/1000 > 128 ? "#212529" : "#fff";
        return style;
    }}
    """)


def create_dynamic_next5_cell_style_js(color_scheme, opacity):
    strong = color_scheme["strong"]
    weak = color_scheme["weak"]
    neutral = color_scheme["neutral"]

    return JsCode(f"""
    function(params) {{
        const v = params.data["Next_5_Diff_Display__strength"];

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

        const dev = (v - 0.5) / 0.5;
        const n = Math.max(-1, Math.min(1, dev));

        function lerp(a,b,f) {{ return Math.round(a + (b-a)*f); }}

        let r,g,b;
        if (n >= 0) {{
            r = lerp({neutral[0]}, {strong[0]}, n);
            g = lerp({neutral[1]}, {strong[1]}, n);
            b = lerp({neutral[2]}, {strong[2]}, n);
        }} else {{
            const a = Math.abs(n);
            r = lerp({neutral[0]}, {weak[0]}, a);
            g = lerp({neutral[1]}, {weak[1]}, a);
            b = lerp({neutral[2]}, {weak[2]}, a);
        }}

        style.background = `rgb(${{r}},${{g}},${{b}})`;
        style.color = (r*299+g*587+b*114)/1000 > 128 ? "#212529" : "#fff";
        return style;
    }}
    """)


# ============================================================
# VALUE FORMATTERS
# ============================================================

def create_mins_value_formatter_js():
    return JsCode("""
    function(params) {
        const value = params.value;

        if (value == null || isNaN(value)) {
            return '-';
        }

        return Math.round(value) + '%';
    }
    """)


def create_soi_value_getter_js():
    return JsCode("""
    function(params) {
        if (params.data.SOI_Score == null || isNaN(params.data.SOI_Score)) {
            return '-';
        }

        const value = params.data.SOI_Score;
        const percentage = Math.round(value * 100);

        const barWidth = Math.round(value * 20);
        const emptyWidth = 20 - barWidth;

        const filled = '▓'.repeat(barWidth);
        const empty = '░'.repeat(emptyWidth);

        return filled + empty + ' ' + percentage + '%';
    }
    """)


def create_soi_cell_style_js():
    return JsCode("""
    function(params) {
        if (params.value == null || params.value === '-') {
            return {
                display: 'flex',
                justifyContent: 'flex-start',
                alignItems: 'center',
                color: '#adb5bd',
                paddingLeft: '8px',
                fontFamily: 'monospace'
            };
        }

        const value = params.data.SOI_Score;

        let color;
        if (value >= 0.7) {
            color = '#22c55e';
        } else if (value >= 0.4) {
            color = '#eab308';
        } else {
            color = '#ef4444';
        }

        return {
            display: 'flex',
            justifyContent: 'flex-start',
            alignItems: 'center',
            fontFamily: 'monospace',
            fontSize: '0.85rem',
            fontWeight: '600',
            color: color,
            paddingLeft: '8px',
            backgroundColor: 'transparent'
        };
    }
    """)


# ============================================================
# GRID CONFIGURATION
# ============================================================

def configure_player_grid(grid_df, strength_columns, cell_style_js, strength_colors, strength_opacity):

    gb = GridOptionsBuilder.from_dataframe(grid_df)

    gb.configure_column(
        "displayName",
        pinned="left",
        width=180,
        headerName="Player",
        cellStyle={'fontWeight': '600', 'paddingLeft': '8px'}
    )

    gb.configure_column(
        "Club",
        pinned="left",
        width=150,
        headerName="Club",
        cellStyle={'paddingLeft': '8px'}
    )

    dynamic_next5_style = create_dynamic_next5_cell_style_js(strength_colors, strength_opacity)
    mins_formatter = create_mins_value_formatter_js()

    for col_info in strength_columns:
        col_name = col_info["name"]
        display_name = col_info["display"]

        if col_name == "SOI_Score":
            gb.configure_column(
                col_name,
                headerName=display_name,
                valueGetter=create_soi_value_getter_js(),
                cellStyle=create_soi_cell_style_js(),
                width=240,
                headerClass="ag-center-header",
                sortable=True
            )

        elif col_name == "Next_5_Diff_Display":
            gb.configure_column(
                col_name,
                headerName=display_name,
                tooltipField=f"{col_name}__tooltip",
                cellStyle=dynamic_next5_style,
                width=110,
                headerClass="ag-center-header"
            )
            gb.configure_column(f"{col_name}__strength", hide=True)
            gb.configure_column(f"{col_name}__tooltip", hide=True)

        elif col_name in ["L5_Mins_Display", "L15_Mins_Display"]:
            gb.configure_column(
                col_name,
                headerName=display_name,
                valueFormatter=mins_formatter,
                tooltipField=f"{col_name}__tooltip",
                cellStyle=cell_style_js,
                width=110,
                headerClass="ag-center-header"
            )
            gb.configure_column(f"{col_name}__strength", hide=True)
            gb.configure_column(f"{col_name}__tooltip", hide=True)

        else:
            gb.configure_column(
                col_name,
                headerName=display_name,
                tooltipField=f"{col_name}__tooltip",
                cellStyle=cell_style_js,
                width=110,
                headerClass="ag-center-header"
            )
            gb.configure_column(f"{col_name}__strength", hide=True)
            gb.configure_column(f"{col_name}__tooltip", hide=True)

    gb.configure_grid_options(
        tooltipShowDelay=0,
        animateRows=True,
        rowHeight=45,
        headerHeight=45,
        enableCellTextSelection=True
    )

    gb.configure_default_column(
        resizable=True,
        sortable=True,
        filter=False
    )

    return gb.build()


# ============================================================
# DATA PREP FOR GRID
# ============================================================

def prepare_player_grid_data(df):

    display_cols = ["displayName", "Club"]
    strength_columns = []

    metrics = [
        ("L5_Form_Display", "L5 Form", "Last 5 games average score / 70"),
        ("L15_Form_Display", "L15 Form", "Last 15 games average score / 70"),
        ("Next_5_Diff_Display", "Next 5 Fixtures", "Upcoming fixture difficulty"),
        ("L5_Mins_Display", "L5 Mins", "Last 5 games minutes / 450"),
        ("L15_Mins_Display", "L15 Mins", "Last 15 games minutes / 1350"),
        ("SOI_Score", "SOI", "Strength of Investment")
    ]

    for name, display, tooltip in metrics:
        if name in df.columns:
            display_cols.append(name)
            strength_columns.append({
                "name": name,
                "display": display,
                "tooltip": tooltip
            })

    grid_df = df[display_cols].copy()

    for col_info in strength_columns:
        col = col_info["name"]

        if col == "SOI_Score":
            continue

        strength_col = col.replace("_Display", "_Strength")

        if strength_col in df.columns:
            grid_df[f"{col}__strength"] = df[strength_col]
            grid_df[f"{col}__tooltip"] = col_info["tooltip"]

    if "SOI_Score" in grid_df.columns:
        grid_df = grid_df.sort_values("SOI_Score", ascending=False)

    return grid_df, strength_columns
