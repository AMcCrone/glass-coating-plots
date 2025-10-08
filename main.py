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

# --- Session state initialization (single source of truth) ---
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

# Editor widget key
EDITOR_KEY = "editor_df"

# Initialize editor widget state from authoritative df if missing
if EDITOR_KEY not in st.session_state:
    st.session_state[EDITOR_KEY] = st.session_state.df.copy()

def sync_editor_to_df():
    """Copy the edited DataFrame from the widget key into st.session_state['df']."""
    new_df = st.session_state.get(EDITOR_KEY)
    if isinstance(new_df, pd.DataFrame):
        st.session_state.df = new_df.copy()

# ------------------ Data Entry UI (paste removed) ------------------
st.header("Data Entry")
st.markdown("Edit the table below. Changes in the editor will be synced into session state.")

# Column configuration (same as before)
column_config = {
    "Glass Type": st.column_config.SelectboxColumn(
        "Glass Type",
        options=["Normal", "Mid-Iron", "Low Iron", "Ultra Clear"],
        required=True
    ),
    "VLT (%)": st.column_config.NumberColumn(
        "VLT (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        format="%.1f"
    ),
    "External Reflectance (%)": st.column_config.NumberColumn(
        "External Reflectance (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        format="%.1f"
    ),
    "Internal Reflectance (%)": st.column_config.NumberColumn(
        "Internal Reflectance (%)",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        format="%.1f"
    ),
    "G-Value": st.column_config.NumberColumn(
        "G-Value",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        format="%.2f"
    ),
    "U-Value (W/m²K)": st.column_config.NumberColumn(
        "U-Value (W/m²K)",
        min_value=0.0,
        max_value=10.0,
        step=0.1,
        format="%.1f"
    ),
    "Color Rendering Index": st.column_config.NumberColumn(
        "Color Rendering Index",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        format="%.1f"
    ),
    "Embodied Carbon (kgCO2e/m²)": st.column_config.NumberColumn(
        "Embodied Carbon (kgCO2e/m²)",
        min_value=0.0,
        step=0.1,
        format="%.1f"
    ),
}

# IMPORTANT: pass the DataFrame positionally (no `value=` keyword)
# Also pass key=EDITOR_KEY so the widget value is stored in st.session_state[EDITOR_KEY].
# on_change will copy from st.session_state[EDITOR_KEY] to st.session_state['df'].
edited_df = st.data_editor(
    st.session_state[EDITOR_KEY],   # positional arg (fixes TypeError from 'value=')
    num_rows="dynamic",
    width="stretch",
    column_config=column_config,
    hide_index=True,
    key=EDITOR_KEY,
    on_change=sync_editor_to_df
)

# Fallback: some Streamlit versions return the edited df, some don't.
# Ensure we always have a DataFrame to work with.
if edited_df is None:
    edited_df = st.session_state.get(EDITOR_KEY)
else:
    # keep editor key updated
    st.session_state[EDITOR_KEY] = edited_df

# Manual save button (optional fallback)
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("💾 Save edits to session (manual)"):
        if isinstance(st.session_state.get(EDITOR_KEY), pd.DataFrame):
            st.session_state.df = st.session_state[EDITOR_KEY].copy()
            st.success("Saved edits to session.")
        else:
            st.error("No valid table to save.")

# Use authoritative df for plotting (ensures plots read the canonical source)
current_df = st.session_state.df.copy()

# ------------------ Visualization (same logic, using current_df) ------------------
st.header("Visualization")

if len(current_df) > 0:
    numeric_cols = [col for col in current_df.columns if col not in
                    ["Supplier", "Glass Type", "Glass Name", "Coating Name"]]

    tab1, tab2 = st.tabs(["Scatter Plot", "Bar Chart Comparison"])

    with tab1:
        st.subheader("Scatter Plot Settings")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            default_x = "G-Value" if "G-Value" in numeric_cols else (numeric_cols[0] if numeric_cols else None)
            x_axis = st.selectbox("X-Axis", numeric_cols, index=numeric_cols.index(default_x) if default_x in numeric_cols else 0, key="scatter_x")
        with c2:
            default_y = "VLT (%)" if "VLT (%)" in numeric_cols else (numeric_cols[0] if numeric_cols else None)
            y_axis = st.selectbox("Y-Axis", numeric_cols, index=numeric_cols.index(default_y) if default_y in numeric_cols else 0, key="scatter_y")
        with c3:
            show_supplier = st.checkbox("Show Supplier Labels", value=True)
        with c4:
            show_coating = st.checkbox("Show Coating Labels", value=True)

        c5, c6 = st.columns(2)
        with c5:
            point_size = st.slider("Point Size", 5, 20, 10)
        with c6:
            point_color = st.selectbox(
                "Point Color",
                options=list(COLORS.keys()),
                index=list(COLORS.keys()).index('TT_MidBlue')
            )

        plot_df = current_df.dropna(subset=[x_axis, y_axis]) if x_axis and y_axis else pd.DataFrame()

        if len(plot_df) > 0:
            fig_scatter = go.Figure()
            for idx, row in plot_df.iterrows():
                hover_text = f"<b>{row['Supplier']}</b><br>Coating: {row['Coating Name']}<br>Glass: {row['Glass Name']}<br>Type: {row['Glass Type']}<br>{x_axis}: {row[x_axis]}<br>{y_axis}: {row[y_axis]}"
                annotation_text = ""
                if show_supplier:
                    annotation_text += f"<b>{row['Supplier']}</b>"
                if show_coating:
                    if annotation_text:
                        annotation_text += "<br>"
                    annotation_text += f"{row['Coating Name']}"
                fig_scatter.add_trace(go.Scatter(
                    x=[row[x_axis]],
                    y=[row[y_axis]],
                    mode='markers+text',
                    marker=dict(size=point_size, color=COLORS[point_color], line=dict(width=1.5, color=COLORS['TT_DarkBlue'])),
                    text=annotation_text if (show_supplier or show_coating) else "",
                    textposition="top center",
                    textfont=dict(size=9, color=COLORS['TT_DarkBlue']),
                    hovertemplate=hover_text + "<extra></extra>",
                    showlegend=False,
                    name=""
                ))
            fig_scatter.update_layout(
                title=dict(text=f"{y_axis} vs {x_axis}", font=dict(size=18, color=COLORS['TT_DarkBlue'])),
                xaxis_title=x_axis, yaxis_title=y_axis, hovermode='closest',
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(family="Arial, sans-serif", color=COLORS['TT_DarkBlue']),
                height=600, margin=dict(t=80, b=80, l=80, r=80)
            )
            fig_scatter.update_xaxes(showgrid=True, gridwidth=1, gridcolor=COLORS['TT_LightGrey'], linecolor=COLORS['TT_Grey'], linewidth=2)
            fig_scatter.update_yaxes(showgrid=True, gridwidth=1, gridcolor=COLORS['TT_LightGrey'], linecolor=COLORS['TT_Grey'], linewidth=2)
            config = {
                'displayModeBar': True,
                'displaylogo': False,
                'toImageButtonOptions': {'format': 'svg', 'filename': 'scatter_plot', 'height': 600, 'width': 1000, 'scale': 1}
            }
            st.plotly_chart(fig_scatter, config=config)
            html_str = fig_scatter.to_html(include_plotlyjs='cdn')
            st.download_button(label="📥 Download Interactive Plot (HTML)", data=html_str, file_name="scatter_plot.html", mime="text/html")
        else:
            st.warning("⚠️ No valid data points to plot. Please ensure numeric values are entered.")

    with tab2:
        st.subheader("Bar Chart Comparison Settings")
        c1, c2 = st.columns([2, 1])
        with c1:
            metrics_to_compare = st.multiselect("Select Metrics to Compare", options=numeric_cols, default=[numeric_cols[0]] if numeric_cols else [])
        with c2:
            sort_by = st.selectbox("Sort By", options=["Supplier"] + metrics_to_compare if metrics_to_compare else ["Supplier"], index=0)
        if metrics_to_compare:
            bar_df = current_df.dropna(subset=metrics_to_compare)
            if len(bar_df) > 0:
                bar_df = bar_df.copy()
                bar_df['Label'] = bar_df['Supplier'] + '<br>' + bar_df['Coating Name']
                if sort_by != "Supplier":
                    bar_df = bar_df.sort_values(by=sort_by, ascending=False)
                fig_bar = go.Figure()
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
                    xaxis_title="Product", yaxis_title="Value", barmode='group',
                    plot_bgcolor='white', paper_bgcolor='white',
                    font=dict(family="Arial, sans-serif", color=COLORS['TT_DarkBlue']),
                    height=600, margin=dict(t=80, b=120, l=80, r=80),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                fig_bar.update_xaxes(showgrid=False, linecolor=COLORS['TT_Grey'], linewidth=2)
                fig_bar.update_yaxes(showgrid=True, gridwidth=1, gridcolor=COLORS['TT_LightGrey'], linecolor=COLORS['TT_Grey'], linewidth=2)
                config = {
                    'displayModeBar': True,
                    'displaylogo': False,
                    'toImageButtonOptions': {'format': 'svg', 'filename': 'bar_chart_comparison', 'height': 600, 'width': 1000, 'scale': 1}
                }
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
