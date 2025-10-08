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

# Configure page
st.set_page_config(
    page_title="Glass Coating Analysis",
    page_icon="🔬",
    layout="wide"
)

# Title and description
st.title("🔬 Glass Coating Analysis Tool")
st.markdown("**Analyze and visualize glass coating performance metrics**")

# Initialize session state for data
if 'df' not in st.session_state:
    # Default columns with sample data
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

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("Plot Settings")
    numeric_cols = [col for col in st.session_state.df.columns if col not in 
                    ["Supplier", "Glass Type", "Glass Name", "Coating Name"]]
    
    x_axis = st.selectbox("X-Axis", numeric_cols, index=numeric_cols.index("G-Value"))
    y_axis = st.selectbox("Y-Axis", numeric_cols, index=numeric_cols.index("VLT (%)"))
    
    st.subheader("Display Options")
    show_supplier = st.checkbox("Show Supplier Labels", value=True)
    show_coating = st.checkbox("Show Coating Labels", value=True)
    point_size = st.slider("Point Size", 5, 20, 10)
    
    st.subheader("Color Scheme")
    point_color = st.selectbox(
        "Point Color",
        options=list(COLORS.keys()),
        index=list(COLORS.keys()).index('TT_MidBlue')
    )

# Main content area
st.header("📊 Data Entry")

# Data editor with proper column configuration
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

# Editable dataframe
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    width="stretch",
    column_config=column_config,
    hide_index=True,
)

# Update session state
st.session_state.df = edited_df

# Plotting section
st.header("📈 Visualization")

if len(edited_df) > 0:
    # Filter out rows with missing x or y values
    plot_df = edited_df.dropna(subset=[x_axis, y_axis])
    
    if len(plot_df) > 0:
        # Create Plotly figure
        fig = go.Figure()
        
        # Add scatter plot
        for idx, row in plot_df.iterrows():
            # Build hover text
            hover_text = f"<b>{row['Supplier']}</b><br>"
            hover_text += f"Coating: {row['Coating Name']}<br>"
            hover_text += f"Glass: {row['Glass Name']}<br>"
            hover_text += f"Type: {row['Glass Type']}<br>"
            hover_text += f"{x_axis}: {row[x_axis]}<br>"
            hover_text += f"{y_axis}: {row[y_axis]}"
            
            # Build annotation text
            annotation_text = ""
            if show_supplier:
                annotation_text += f"<b>{row['Supplier']}</b>"
            if show_coating:
                if annotation_text:
                    annotation_text += "<br>"
                annotation_text += f"{row['Coating Name']}"
            
            fig.add_trace(go.Scatter(
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
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"{y_axis} vs {x_axis}",
                font=dict(size=18, color=COLORS['TT_DarkBlue'])
            ),
            xaxis_title=x_axis,
            yaxis_title=y_axis,
            hovermode='closest',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", color=COLORS['TT_DarkBlue']),
            height=600,
            margin=dict(t=80, b=80, l=80, r=80)
        )
        
        fig.update_xaxis(
            showgrid=True,
            gridwidth=1,
            gridcolor=COLORS['TT_LightGrey'],
            linecolor=COLORS['TT_Grey'],
            linewidth=2
        )
        fig.update_yaxis(
            showgrid=True,
            gridwidth=1,
            gridcolor=COLORS['TT_LightGrey'],
            linecolor=COLORS['TT_Grey'],
            linewidth=2
        )
        
        # Display plot
        st.plotly_chart(fig, width="stretch")
        
        # Export options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Export data as CSV
            csv = edited_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Data (CSV)",
                data=csv,
                file_name="glass_coating_data.csv",
                mime="text/csv",
            )
        
        with col2:
            st.info("💡 Use the camera icon on the plot to save as PNG/SVG")
        
    else:
        st.warning("⚠️ No valid data points to plot. Please ensure numeric values are entered for selected axes.")
else:
    st.info("ℹ️ Add data to the table above to generate visualizations.")

# Footer
st.markdown("---")
st.markdown("*Glass Coating Analysis Tool - Compare and analyze glass coating performance metrics*")
