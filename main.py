import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO

# Company theme colors (unchanged)
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

# We'll use a dedicated widget key for the editor so Streamlit stores the widget value in session_state
EDITOR_KEY = "editor_df"

# If the editor widget state isn't present, initialize it from session_state.df
if EDITOR_KEY not in st.session_state:
    # Make a copy to avoid accidental reference sharing
    st.session_state[EDITOR_KEY] = st.session_state.df.copy()

# Callback to sync editor widget state into the authoritative df
def sync_editor_to_df():
    """Copy the edited DataFrame from the widget key into st.session_state['df']."""
    # The editor widget stores its value in st.session_state[EDITOR_KEY]
    new_df = st.session_state.get(EDITOR_KEY)
    if isinstance(new_df, pd.DataFrame):
        st.session_state.df = new_df.copy()

# Optional: helper to import clipboard-like text pasted from Excel into a dataframe
def import_pasted_table(pasted_text: str, sep='\t'):
    """Parse pasted table text (from Excel) into a DataFrame. Returns DataFrame or None."""
    if not pasted_text:
        return None
    try:
        buf = StringIO(pasted_text)
        # try with tab delimiter (Excel copy often uses tabs)
        df = pd.read_csv(buf, sep=sep)
        return df
    except Exception as e:
        # fallback: try comma
        try:
            buf.seek(0)
            df = pd.read_csv(buf, sep=',')
            return df
        except Exception:
            st.error(f"Could not parse pasted table: {e}")
            return None

# ------------------ Data Entry UI ------------------
st.header("Data Entry")

# Provide two ways to update data:
# 1) Paste raw rows from Excel into a textarea and 'Import' them.
# 2) Edit the interactive data_editor (auto-syncs using on_change), and an explicit Save button if desired.

with st.expander("Quick paste from Excel (recommended if copy/paste to the editor is unreliable)"):
    st.markdown("Copy rows from Excel (including header row), then paste below and click **Import pasted table**.")
    pasted = st.text_area("Paste here", height=120, placeholder="Paste tab-separated values from Excel here")
    if st.button("Import pasted table"):
        imported_df = import_pasted_table(pasted, sep='\t')
        if imported_df is not None:
            # we try to align columns if possible: if exact match then replace, otherwise append
            # If the imported has the same columns as our schema -> replace
            expected_cols = list(st.session_state.df.columns)
            if list(imported_df.columns) == expected_cols:
                st.session_state.df = imported_df.copy()
                st.session_state[EDITOR_KEY] = st.session_state.df.copy()
                st.success("Imported and replaced the current table.")
            else:
                # Try to coerce: keep only expected columns + add missing as NaN
                coerced = pd.DataFrame(columns=expected_cols)
                for c in expected_cols:
                    if c in imported_df.columns:
                        coerced[c] = imported_df[c]
                    else:
                        coerced[c] = pd.NA
                # append to existing df
                st.session_state.df = pd.concat([st.session_state.df, coerced], ignore_index=True)
                st.session_state[EDITOR_KEY] = st.session_state.df.copy()
                st.success("Imported table appended to existing data (columns coerced).")

st.markdown("Or edit the table below directly. Edits are stored in the **editor state** and synced automatically to the main dataset.")

# Column config (unchanged)
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

# The interactive editor uses the dedicated widget key and an on_change callback to sync into st.session_state.df
edited_df = st.data_editor(
    value=st.session_state[EDITOR_KEY],
    num_rows="dynamic",
    width="stretch",
    column_config=column_config,
    hide_index=True,
    key=EDITOR_KEY,
    on_change=sync_editor_to_df
)

# Also provide a manual Save button as a fallback
col1, col2 = st.columns([1, 3])
with col1:
    if st.button("💾 Save edits to session (manual)"):
        # copy the widget dataframe into the authoritative df
        # the widget value will be in st.session_state[EDITOR_KEY]
        if isinstance(st.session_state.get(EDITOR_KEY), pd.DataFrame):
            st.session_state.df = st.session_state[EDITOR_KEY].copy()
            st.success("Saved edits to session.")
        else:
            st.error("No valid table to save.")

# Ensure authoritative df reflects the latest editor content (this is idempotent)
# this line ensures downstream visualizations always read from st.session_state.df
current_df = st.session_state.df.copy()

# ------------------ Visualization (unchanged logic, but use current_df) ------------------
st.header("Visualization")

if len(current_df) > 0:
    numeric_cols = [col for col in current_df.columns if col not in
                    ["Supplier", "Glass Type", "Glass Name", "Coating Name"]]

    tab1, tab2 = st.tabs(["Scatter Plot", "Bar Chart Comparison"])

    with tab1:
        st.subheader("Scatter Plot Settings")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # guard index fallback if column names changed
            default_x = "G-Value" if "G-Value" in numeric_cols else (numeric_cols[0] if numeric_cols else None)
            x_axis = st.selectbox("X-Axis", numeric_cols, index=numeric_cols.index(default_x) if default_x in numeric_cols else 0, key="scatter_x")
        with col2:
            default_y = "VLT (%)" if "VLT (%)" in numeric_cols else (numeric_cols[0] if numeric_cols else None)
            y_axis = st.selectbox("Y-Axis", numeric_cols, index=numeric_cols.index(default_y) if default_y in numeric_cols else 0, key="scatter_y")
        with col3:
            show_supplier = st.checkbox("Show Supplier Labels", value=True)
        with col4:
            show_coating = st.checkbox("Show Coating Labels", value=True)

        col5, col6 = st.columns(2)
        with col5:
            point_size = st.slider("Point Size", 5, 20, 10)
        with col6:
            point_color = st.selectbox(
                "Point Color",
                options=list(COLORS.keys()),
                index=list(COLORS.keys()).index('TT_MidBlue')
            )

        plot_df = current_df.dropna(subset=[x_axis, y_axis])

        if len(plot_df) > 0:
            fig_scatter = go.Figure()
            for idx, row in plot_df.iterrows():
                hover_text = f"<b>{row['Supplier']}</b><br>"
                hover_text += f"Coating: {row['Coating Name']}<br>"
                hover_text += f"Glass: {row['Glass Name']}<br>"
                hover_text += f"Type: {row['Glass Type']}<br>"
                hover_text += f"{x_axis}: {row[x_axis]}<br>"
                hover_text += f"{y_axis}: {row[y_axis]}"

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
                    marker=dict(
                        size=point_size,
                        color=COLORS[point_color],
                        line=dict(width=1.5, color=COLORS['TT_DarkBlue'])
                    ),
                    text=annotation_text if (show_supplier or show_coating) else "",
                    textposition="top center",
                    textfont=dict(size=9, color=COLORS['TT_DarkBlue']),
                    hovertemplate=hover_text + "<extra></extra>",
                    showlegend=False,
                    name=""
                ))

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
            metrics_to_compare = st.multiselect("Select Metrics to Compare", options=numeric_cols, default=[numeric_cols[0]] if len(numeric_cols) > 0 else [])
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

                config = {
                    'displayModeBar': True,
                    'displaylogo': False,
                    'toImageButtonOptions': {
                        'format': 'svg',
                        'filename': 'bar_chart_comparison',
                        'height': 600,
                        'width': 1000,
                        'scale': 1
                    }
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
