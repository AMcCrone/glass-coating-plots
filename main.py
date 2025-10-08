import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Company theme colors
COLORS = {
    'TT_Orange': 'rgb(211,69,29)',
    'TT_Olive': 'rgb(139,144,100)',
    'TT_LightBlue': 'rgb(136,219,223)',
    'TT_MidBlue': 'rgb(0,163,173)',
    'TT_DarkBlue': 'rgb(0,48,60)',
    'TT_Grey': 'rgb(99,102,105)',
    'TT_LightLightBlue': 'rgb(207,241,242)',
    'TT_LightGrey': 'rgb(223,224,225)'
}

METRIC_COLORS = [
    COLORS['TT_MidBlue'],
    COLORS['TT_Orange'],
    COLORS['TT_Olive'],
    COLORS['TT_LightBlue'],
    COLORS['TT_Grey'],
    'rgb(156,117,95)',
    'rgb(186,176,172)'
]

st.set_page_config(page_title="Glass Coating Analysis", page_icon="🔬", layout="wide")
st.title("Glass Coating Analysis Tool")
st.markdown("**Analyze and visualize glass coating performance metrics**")

# --- Authoritative dataframe in session state ---
if 'df' not in st.session_state:
    columns = [
        "Supplier", "Glass Type", "Glass Name", "Coating Name",
        "VLT (%)", "External Reflectance (%)", "Internal Reflectance (%)",
        "G-Value", "U-Value (W/m²K)", "Color Rendering Index", "Embodied Carbon (kgCO2e/m²)"
    ]
    sample_data = [
        ["AGC EU", "Low Iron", "Planibel ClearVision", "ipasol neutral 70/37",
         59.0, 11.0, 11.0, 0.34, 1.3, 95.0, 45.0],
        ["Guardian ME", "Ultra Clear", "Guardian UltraClear", "SN 70 T",
         63.0, 12.0, 12.0, 0.38, 1.3, 97.0, 42.0],
    ]
    st.session_state.df = pd.DataFrame(sample_data, columns=columns)

EDITOR_KEY = "editor_df"  # widget key — DO NOT assign to st.session_state[EDITOR_KEY] anywhere

def sync_editor_to_df():
    """
    Callback triggered by the widget when it changes.
    It reads the widget's state (allowed) and copies into authoritative df.
    """
    widget_val = st.session_state.get(EDITOR_KEY)
    if isinstance(widget_val, pd.DataFrame):
        st.session_state.df = widget_val.copy()

# ------------------ Data Entry UI ------------------
st.header("Data Entry")
st.markdown("Edit the table below. Edits are synced to session state automatically (via on_change).")

column_config = {
    "Glass Type": st.column_config.SelectboxColumn(
        "Glass Type",
        options=["Normal", "Mid-Iron", "Low Iron", "Ultra Clear"],
        required=False
    ),
    "VLT (%)": st.column_config.NumberColumn("VLT (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
    "External Reflectance (%)": st.column_config.NumberColumn("External Reflectance (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
    "Internal Reflectance (%)": st.column_config.NumberColumn("Internal Reflectance (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
    "G-Value": st.column_config.NumberColumn("G-Value", min_value=0.0, max_value=1.0, step=0.01, format="%.2f"),
    "U-Value (W/m²K)": st.column_config.NumberColumn("U-Value (W/m²K)", min_value=0.0, max_value=10.0, step=0.1, format="%.1f"),
    "Color Rendering Index": st.column_config.NumberColumn("Color Rendering Index", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
    "Embodied Carbon (kgCO2e/m²)": st.column_config.NumberColumn("Embodied Carbon (kgCO2e/m²)", min_value=0.0, step=0.1, format="%.1f"),
}

# IMPORTANT: give the authoritative df positionally to data_editor.
# Do NOT pre-set st.session_state[EDITOR_KEY] anywhere — the widget will create it.
# Provide on_change to auto-copy widget state -> st.session_state.df (via sync_editor_to_df).
try:
    edited_df = st.data_editor(
        st.session_state.df,    # positional
        num_rows="dynamic",
        width="stretch",
        column_config=column_config,
        hide_index=True,
        key=EDITOR_KEY,
        on_change=sync_editor_to_df
    )
except TypeError:
    # older/newer streamlit versions might not support on_change; try without it
    edited_df = st.data_editor(
        st.session_state.df,
        num_rows="dynamic",
        width="stretch",
        column_config=column_config,
        hide_index=True,
        key=EDITOR_KEY
    )

# If the widget returns the edited df directly, use that to update canonical df.
# This is allowed (we are updating 'df', not the widget key).
if isinstance(edited_df, pd.DataFrame):
    st.session_state.df = edited_df.copy()
else:
    # Otherwise, attempt to read the widget's session-state (allowed) and keep authoritative df consistent.
    widget_val = st.session_state.get(EDITOR_KEY)
    if isinstance(widget_val, pd.DataFrame):
        st.session_state.df = widget_val.copy()

# Optional manual save button (works by reading widget value or returned edited_df)
col1, _ = st.columns([1, 3])
with col1:
    if st.button("💾 Save edits to session (manual)"):
        # Prefer the returned edited_df; otherwise fall back to widget session state
        if isinstance(edited_df, pd.DataFrame):
            st.session_state.df = edited_df.copy()
            st.success("Saved edits to session from returned editor value.")
        else:
            w = st.session_state.get(EDITOR_KEY)
            if isinstance(w, pd.DataFrame):
                st.session_state.df = w.copy()
                st.success("Saved edits to session from widget state.")
            else:
                st.error("No valid edits found to save.")

# Use authoritative df for visualization
current_df = st.session_state.df.copy()

# ------------------ Visualization ------------------
st.header("Visualization")

if len(current_df) > 0:
    numeric_cols = [col for col in current_df.columns if col not in
                    ["Supplier", "Glass Type", "Glass Name", "Coating Name"]]

    tab1, tab2 = st.tabs(["Scatter Plot", "Bar Chart Comparison"])

        # TAB 1: SCATTER PLOT (replace your existing with this block)
    with tab1:
        st.subheader("Scatter Plot Settings")
        col1, col2, col3, col4 = st.columns(4)

        # Axis selectors
        with col1:
            default_x = "G-Value" if "G-Value" in numeric_cols else (numeric_cols[0] if numeric_cols else None)
            x_axis = st.selectbox("X-Axis", numeric_cols, index=numeric_cols.index(default_x) if default_x in numeric_cols else 0, key="scatter_x")
        with col2:
            default_y = "VLT (%)" if "VLT (%)" in numeric_cols else (numeric_cols[0] if numeric_cols else None)
            y_axis = st.selectbox("Y-Axis", numeric_cols, index=numeric_cols.index(default_y) if default_y in numeric_cols else 0, key="scatter_y")
        with col3:
            show_supplier = st.checkbox("Show Supplier Labels", value=True)
        with col4:
            show_coating = st.checkbox("Show Coating Labels", value=True)

        # Visual controls (marker color fixed to TT_Orange)
        col5, col6 = st.columns(2)
        with col5:
            point_size = st.slider("Base Point Size", 5, 20, 10)
        with col6:
            # fixed color per your request
            point_color_name = 'TT_Orange'
            point_color = COLORS[point_color_name]

        # Target lines & highlighting controls
        st.markdown("**Target lines & highlight zone**")
        tcol1, tcol2, tcol3 = st.columns([1, 1, 1])
        with tcol1:
            show_targets = st.checkbox("Show target lines / highlight zone", value=False)
        with tcol2:
            g_target = None
            if "G-Value" in numeric_cols:
                # default sensible value shown even if checkbox off
                g_target = st.number_input("G-Value target", min_value=0.0, max_value=1.0, step=0.01, value=0.35, key="g_target_input")
        with tcol3:
            vlt_target = None
            if "VLT (%)" in numeric_cols:
                vlt_target = st.number_input("VLT (%) target", min_value=0.0, max_value=100.0, step=0.1, value=60.0, key="vlt_target_input")

        # Prepare plotting DataFrame
        plot_df = current_df.dropna(subset=[x_axis, y_axis]).reset_index(drop=True)
        if len(plot_df) > 0:
            # compute extents and margins to extend highlight area beyond axes
            x_min, x_max = float(plot_df[x_axis].min()), float(plot_df[x_axis].max())
            y_min, y_max = float(plot_df[y_axis].min()), float(plot_df[y_axis].max())
            # avoid zero-range margins
            x_range = (x_max - x_min) if (x_max > x_min) else max(abs(x_min), 1.0)
            y_range = (y_max - y_min) if (y_max > y_min) else max(abs(y_min), 1.0)
            margin_x = x_range * 0.10
            margin_y = y_range * 0.10

            fig_scatter = go.Figure()

            # Draw target dashed lines in light grey if requested
            if show_targets:
                if g_target is not None:
                    fig_scatter.add_shape(
                        type="line",
                        x0=g_target, x1=g_target,
                        y0=y_min - margin_y, y1=y_max + margin_y,
                        line=dict(color=COLORS['TT_LightGrey'], width=2, dash='dash'),
                        xref='x', yref='y'
                    )
                    fig_scatter.add_annotation(
                        x=g_target, y=y_max + margin_y * 0.7,
                        text=f"G target: {g_target}",
                        showarrow=False, yshift=4, font=dict(size=10, color=COLORS['TT_DarkBlue'])
                    )
                if vlt_target is not None:
                    fig_scatter.add_shape(
                        type="line",
                        x0=x_min - margin_x, x1=x_max + margin_x,
                        y0=vlt_target, y1=vlt_target,
                        line=dict(color=COLORS['TT_LightGrey'], width=2, dash='dash'),
                        xref='x', yref='y'
                    )
                    fig_scatter.add_annotation(
                        x=x_max + margin_x * 0.5, y=vlt_target,
                        text=f"VLT target: {vlt_target}",
                        showarrow=False, xshift=6, font=dict(size=10, color=COLORS['TT_DarkBlue'])
                    )

                # If both targets provided, draw highlight rectangle for: G <= g_target AND VLT >= vlt_target
                if (g_target is not None) and (vlt_target is not None):
                    rect_x0 = x_min - margin_x
                    rect_x1 = g_target + margin_x
                    rect_y0 = vlt_target - margin_y
                    rect_y1 = y_max + margin_y
                    # ensure proper ordering
                    rx0, rx1 = min(rect_x0, rect_x1), max(rect_x0, rect_x1)
                    ry0, ry1 = min(rect_y0, rect_y1), max(rect_y0, rect_y1)
                    fig_scatter.add_shape(
                        type="rect",
                        x0=rx0, x1=rx1,
                        y0=ry0, y1=ry1,
                        fillcolor=COLORS['TT_LightBlue'],
                        opacity=0.12,
                        line=dict(width=0),
                        xref='x', yref='y'
                    )

            # label positions cycle to reduce overlap
            label_positions = [
                "top center", "bottom center", "middle left", "middle right",
                "top left", "top right", "bottom left", "bottom right"
            ]

            # Plot each point as separate trace so we can control per-point label position
            for idx, row in plot_df.iterrows():
                inside_zone = False
                if show_targets and (g_target is not None) and (vlt_target is not None):
                    try:
                        # zone condition: G (x) <= g_target AND VLT (y) >= vlt_target
                        inside_zone = (float(row[x_axis]) <= float(g_target)) and (float(row[y_axis]) >= float(vlt_target))
                    except Exception:
                        inside_zone = False

                # pick color and size
                if inside_zone:
                    marker_col = COLORS['TT_LightBlue']
                    marker_sz = int(max(4, point_size * 1.5))
                else:
                    marker_col = point_color
                    marker_sz = point_size

                # two-line annotation using HTML <br>
                supplier_txt = str(row.get('Supplier', ''))
                coating_txt = str(row.get('Coating Name', ''))
                annotation_text = f"{supplier_txt}<br>{coating_txt}" if (show_supplier or show_coating) else ""

                # if user disabled one of the two, still ensure lines: show supplier line if enabled else blank first line
                if (show_supplier is False) and (show_coating):
                    annotation_text = f"{''}<br>{coating_txt}"
                if (show_coating is False) and (show_supplier):
                    annotation_text = f"{supplier_txt}<br>{''}"

                textmode = 'markers+text' if (show_supplier or show_coating) else 'markers'
                textpos = label_positions[idx % len(label_positions)] if (show_supplier or show_coating) else ""

                hover_text = f"<b>{supplier_txt}</b><br>Coating: {coating_txt}<br>Glass: {row.get('Glass Name','')}<br>Type: {row.get('Glass Type','')}<br>{x_axis}: {row[x_axis]}<br>{y_axis}: {row[y_axis]}"

                fig_scatter.add_trace(go.Scatter(
                    x=[row[x_axis]],
                    y=[row[y_axis]],
                    mode=textmode,
                    marker=dict(
                        size=marker_sz,
                        color=marker_col,
                        line=dict(width=1.2, color=COLORS['TT_DarkBlue'])
                    ),
                    text=annotation_text,
                    textposition=textpos,
                    textfont=dict(size=9, color=COLORS['TT_DarkBlue']),
                    hovertemplate=hover_text + "<extra></extra>",
                    showlegend=False,
                    name=""
                ))

            # layout polish
            fig_scatter.update_layout(
                title=dict(text=f"{y_axis} vs {x_axis}", font=dict(size=18, color=COLORS['TT_DarkBlue'])),
                xaxis_title=x_axis,
                yaxis_title=y_axis,
                hovermode='closest',
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", color=COLORS['TT_DarkBlue']),
                height=600,
                margin=dict(t=80, b=80, l=80, r=80)
            )
            fig_scatter.update_xaxes(showgrid=True, gridwidth=1, gridcolor=COLORS['TT_LightGrey'], linecolor=COLORS['TT_Grey'], linewidth=2)
            fig_scatter.update_yaxes(showgrid=True, gridwidth=1, gridcolor=COLORS['TT_LightGrey'], linecolor=COLORS['TT_Grey'], linewidth=2)

            # Display and export
            config = {
                'displayModeBar': True,
                'displaylogo': False,
                'toImageButtonOptions': {
                    'format': 'svg',
                    'filename': 'scatter_plot',
                    'height': 600,
                    'width': 1000,
                    'scale': 1
                }
            }
            st.plotly_chart(fig_scatter, config=config)
            html_str = fig_scatter.to_html(include_plotlyjs='cdn')
            st.download_button(label="📥 Download Interactive Plot (HTML)", data=html_str, file_name="scatter_plot.html", mime="text/html")
        else:
            st.warning("⚠️ No valid data points to plot. Please ensure numeric values are entered.")

    with tab2:
        st.subheader("Bar Chart Comparison Settings")
        col1, col2 = st.columns([2, 1])
        with col1:
            metrics_to_compare = st.multiselect("Select Metrics to Compare", options=numeric_cols, default=[numeric_cols[0]] if numeric_cols else [])
        with col2:
            sort_by = st.selectbox("Sort By", options=["Supplier"] + metrics_to_compare if metrics_to_compare else ["Supplier"], index=0)

        if metrics_to_compare:
            bar_df = current_df.dropna(subset=metrics_to_compare)
            if len(bar_df) > 0:
                fig_bar = go.Figure()
                bar_df = bar_df.copy()
                bar_df['Label'] = bar_df['Supplier'] + '<br>' + bar_df['Coating Name']

                if sort_by != "Supplier":
                    bar_df = bar_df.sort_values(by=sort_by, ascending=False)

                for i, metric in enumerate(metrics_to_compare):
                    color = METRIC_COLORS[i % len(METRIC_COLORS)]
                    fig_bar.add_trace(go.Bar(
                        name=metric,
                        x=bar_df['Label'],
                        y=bar_df[metric],
                        marker_color=color,
                        text=bar_df[metric].round(2),
                        textposition='outside',
                        hovertemplate=f"<b>%{{x}}</b><br>{metric}: %{{y}}<extra></extra>"
                    ))

                fig_bar.update_layout(
                    title=dict(text="Performance Metrics Comparison", font=dict(size=18, color=COLORS['TT_DarkBlue'])),
                    xaxis_title="Product",
                    yaxis_title="Value",
                    barmode='group',
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial, sans-serif", color=COLORS['TT_DarkBlue']),
                    height=600,
                    margin=dict(t=80, b=120, l=80, r=80),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )

                fig_bar.update_xaxes(showgrid=False, linecolor=COLORS['TT_Grey'], linewidth=2)
                fig_bar.update_yaxes(showgrid=True, gridwidth=1, gridcolor=COLORS['TT_LightGrey'], linecolor=COLORS['TT_Grey'], linewidth=2)

                config = {'displayModeBar': True, 'displaylogo': False, 'toImageButtonOptions': {'format': 'svg', 'filename': 'bar_chart_comparison', 'height': 600, 'width': 1000, 'scale': 1}}
                st.plotly_chart(fig_bar, config=config)
                html_str = fig_bar.to_html(include_plotlyjs='cdn')
                st.download_button(label="📥 Download Interactive Plot (HTML)", data=html_str, file_name="bar_chart_comparison.html", mime="text/html")
            else:
                st.warning("⚠️ No valid data for selected metrics.")
        else:
            st.info("ℹ️ Select at least one metric to compare.")
else:
    st.info("ℹ️ Add data to the table above to generate visualizations.")

st.markdown("---")
st.markdown("*Glass Coating Analysis Tool - Compare and analyze glass coating performance metrics*")
