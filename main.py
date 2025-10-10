import streamlit as st
import pandas as pd
from auth import authenticate_user
from plots import create_scatter_plot, create_bar_chart, create_radial_plots, create_parallel_coordinates

authenticate_user()

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
        # AGC Interpane (double-glazing examples from AGC PDF)
        ["AGC Interpane", "Clear Float", "ipasol neutral", "ipasol neutral 72/42 (6/16/4 Ar)",
         72.0, 11.0, 1.0, 0.48, 1.0, 96.0, 42.0],
        ["AGC Interpane", "Clear Float", "ipasol ultraselect", "ipasol ultraselect 67/32 (6/16/4 Ar)",
         67.0, 10.0, 1.0, 0.37, 1.0, 94.0, 42.0],
        ["AGC Interpane", "Clear Float", "ipasol ultraselect", "ipasol ultraselect 62/29 (6/16/4 Ar)",
         62.0, 9.0, 1.0, 0.34, 1.0, 93.0, 42.0],
        ["AGC Interpane", "Planibel", "Energy", "Energy 70/37 (6/16/4 Ar)",
         70.0, 12.0, 1.0, 0.43, 1.0, 96.0, 40.0],
        ["AGC Interpane", "Planibel", "Stopray", "Stopray Vision 70/35 (6/16/4 Ar)",
         70.0, 14.0, 1.0, 0.40, 1.0, 97.0, 44.0],
        ["AGC Interpane", "Planibel", "ipasol platin", "ipasol platin 52/36 (6/16/4 Ar)",
         52.0, 30.0, 1.0, 0.42, 1.1, 97.0, 48.0],

        # Saint-Gobain — COOL-LITE SKN series (values read from your supplied image)
        ["Saint-Gobain", "Clear/Coated", "COOL-LITE SKN", "SKN 183 II",
         75.0, 12.0, 34.0, 0.40, 1.0, 95.0, 50.0],
        ["Saint-Gobain", "Clear/Coated", "COOL-LITE SKN", "SKN 176 II",
         70.0, 13.0, 32.0, 0.37, 1.0, 95.0, 50.0],
        ["Saint-Gobain", "Clear/Coated", "COOL-LITE SKN", "SKN 175 II",
         70.0, 14.0, 37.0, 0.35, 1.0, 96.0, 50.0],
        ["Saint-Gobain", "Clear/Coated", "COOL-LITE SKN", "SKN 165 II",
         61.0, 16.0, 34.0, 0.34, 1.0, 95.0, 50.0],
        ["Saint-Gobain", "Clear/Coated", "COOL-LITE SKN", "SKN 154 II",
         52.0, 18.0, 30.0, 0.28, 1.0, 95.0, 50.0],
        ["Saint-Gobain", "Clear/Coated", "COOL-LITE SKN", "SKN 144 II",
         42.0, 20.0, 31.0, 0.23, 1.1, 95.0, 50.0],
    ]

    st.session_state.df = pd.DataFrame(sample_data, columns=columns)

EDITOR_KEY = "editor_df"

def sync_editor_to_df():
    widget_val = st.session_state.get(EDITOR_KEY)
    if isinstance(widget_val, pd.DataFrame):
        st.session_state.df = widget_val.copy()

# ------------------ Data Entry UI ------------------
st.header("Data Entry")
st.markdown("Edit the table below.")

column_config = {
    "VLT (%)": st.column_config.NumberColumn("VLT (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
    "External Reflectance (%)": st.column_config.NumberColumn("External Reflectance (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
    "Internal Reflectance (%)": st.column_config.NumberColumn("Internal Reflectance (%)", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
    "G-Value": st.column_config.NumberColumn("G-Value", min_value=0.0, max_value=1.0, step=0.01, format="%.2f"),
    "U-Value (W/m²K)": st.column_config.NumberColumn("U-Value (W/m²K)", min_value=0.0, max_value=10.0, step=0.1, format="%.1f"),
    "Color Rendering Index": st.column_config.NumberColumn("Color Rendering Index", min_value=0.0, max_value=100.0, step=0.1, format="%.1f"),
    "Embodied Carbon (kgCO2e/m²)": st.column_config.NumberColumn("Embodied Carbon (kgCO2e/m²)", min_value=0.0, step=0.1, format="%.1f"),
}

try:
    edited_df = st.data_editor(
        st.session_state.df,
        num_rows="dynamic",
        width="stretch",
        column_config=column_config,
        hide_index=True,
        key=EDITOR_KEY,
        on_change=sync_editor_to_df
    )
except TypeError:
    edited_df = st.data_editor(
        st.session_state.df,
        num_rows="dynamic",
        width="stretch",
        column_config=column_config,
        hide_index=True,
        key=EDITOR_KEY
    )

if isinstance(edited_df, pd.DataFrame):
    st.session_state.df = edited_df.copy()
else:
    widget_val = st.session_state.get(EDITOR_KEY)
    if isinstance(widget_val, pd.DataFrame):
        st.session_state.df = widget_val.copy()

col1, _ = st.columns([1, 3])
with col1:
    if st.button("💾 Save edits to session (manual)"):
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

current_df = st.session_state.df.copy()

# ------------------ Visualization ------------------
st.header("Visualization")

if len(current_df) > 0:
    numeric_cols = [col for col in current_df.columns if col not in
                    ["Supplier", "Glass Type", "Glass Name", "Coating Name"]]

    tab1, tab2, tab3, tab4 = st.tabs(["Scatter Plot", "Bar Chart Comparison", "Radial Plots", "Parallel Coordinates Plot"])

    # TAB 1: SCATTER PLOT
    with tab1:
        create_scatter_plot(current_df, numeric_cols, COLORS, METRIC_COLORS)

    # TAB 2: BAR CHART
    with tab2:
        create_bar_chart(current_df, numeric_cols, COLORS, METRIC_COLORS)

    # TAB 3: RADIAL PLOTS
    with tab3:
        create_radial_plots(current_df, numeric_cols, COLORS, METRIC_COLORS)
    
    # TAB 4: PARALLEL COORDINATES PLOT
    with tab4:
        create_parallel_coordinates(current_df, numeric_cols, COLORS, METRIC_COLORS)
else:
    st.info("ℹ️ Add data to the table above to generate visualizations.")

st.markdown("---")
st.markdown("*Glass Coating Analysis Tool - Compare and analyze glass coating performance metrics*")
