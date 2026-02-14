from st_aggrid import GridOptionsBuilder, JsCode


def create_cell_style_js(center, color_scheme, opacity):

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
            fontWeight: "500"
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

    gb = GridOptionsBuilder.from_dataframe(grid_df)

    gb.configure_column("Rank", pinned="left", width=80)
    gb.configure_column("Rank_Sort", hide=True)
    gb.configure_column("Name", pinned="left", width=220)

    for col in gw_columns + ["Avg"]:
        gb.configure_column(
            col,
            tooltipField=f"{col}__tip",
            cellStyle=cell_style_js,
            width=110
        )
        gb.configure_column(f"{col}__val", hide=True)
        gb.configure_column(f"{col}__tip", hide=True)

    gb.configure_grid_options(
        tooltipShowDelay=0,
        animateRows=True,
        rowHeight=45
    )

    return gb.build()