import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from io import BytesIO

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

# Color palette for different metrics
METRIC_COLORS = [
    COLORS['TT_MidBlue'],
    COLORS['TT_Orange'],
    COLORS['TT_Olive'],
    COLORS['TT_LightBlue'],
    COLORS['TT_Grey'],
    'rgb(156,117,95)',
    'rgb(186,176,172)'
]

# Configure page
st.set_page_config(
    page_title="Glass Coating Analysis",
    page_icon="🔬",
    layout="wide"
)

# Title and description
st.title("Glass Coating Analysis Tool")
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

# Main content area - Data Entry
st.header("Data Entry")

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

# Visualization section
st.header("Visualization")

if len(edited_df) > 0:
    # Get numeric columns
    numeric_cols = [col for col in edited_df.columns if col not in 
                    ["Supplier", "Glass Type", "Glass Name", "Coating Name"]]
    
    # Create tabs for different plot types
    tab1, tab2 = st.tabs(["Scatter Plot", "Bar Chart Comparison"])
    
    # TAB 1: SCATTER PLOT
    with tab1:
        st.subheader("Scatter Plot Settings")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            x_axis = st.selectbox("X-Axis", numeric_cols, index=numeric_cols.index("G-Value"), key="scatter_x")
        with col2:
            y_axis = st.selectbox("Y-Axis", numeric_cols, index=numeric_cols.index("VLT (%)"), key="scatter_y")
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
        
        # Filter out rows with missing x or y values
        plot_df = edited_df.dropna(subset=[x_axis, y_axis])
        
        if len(plot_df) > 0:
            # Create Plotly figure
            fig_scatter = go.Figure()
            
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
            
            # Update layout
            fig_scatter.update_layout(
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
            
            fig_scatter.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor=COLORS['TT_LightGrey'],
                linecolor=COLORS['TT_Grey'],
                linewidth=2
            )
            fig_scatter.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor=COLORS['TT_LightGrey'],
                linecolor=COLORS['TT_Grey'],
                linewidth=2
            )
            
            # Display plot
            config = {'displayModeBar': True, 'displaylogo': False}
            st.plotly_chart(fig_scatter, config=config)
            
            # Export button
            pdf_bytes = pio.to_image(fig_scatter, format='pdf')
            st.download_button(
                label="📥 Download Plot as PDF",
                data=pdf_bytes,
                file_name="scatter_plot.pdf",
                mime="application/pdf"
            )
        else:
            st.warning("⚠️ No valid data points to plot. Please ensure numeric values are entered.")
    
    # TAB 2: BAR CHART COMPARISON
    with tab2:
        st.subheader("Bar Chart Comparison Settings")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            metrics_to_compare = st.multiselect(
                "Select Metrics to Compare",
                options=numeric_cols,
                default=[numeric_cols[0]] if len(numeric_cols) > 0 else []
            )
        with col2:
            sort_by = st.selectbox(
                "Sort By",
                options=["Supplier"] + metrics_to_compare if metrics_to_compare else ["Supplier"],
                index=0
            )
        
        if metrics_to_compare:
            # Prepare data for bar chart
            bar_df = edited_df.dropna(subset=metrics_to_compare)
            
            if len(bar_df) > 0:
                # Create bar chart
                fig_bar = go.Figure()
                
                # Create labels for x-axis (Supplier + Coating)
                bar_df['Label'] = bar_df['Supplier'] + '<br>' + bar_df['Coating Name']
                
                # Sort if needed
                if sort_by != "Supplier":
                    bar_df = bar_df.sort_values(by=sort_by, ascending=False)
                
                # Add bars for each metric
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
                
                # Update layout
                fig_bar.update_layout(
                    title=dict(
                        text="Performance Metrics Comparison",
                        font=dict(size=18, color=COLORS['TT_DarkBlue'])
                    ),
                    xaxis_title="Product",
                    yaxis_title="Value",
                    barmode='group',
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial, sans-serif", color=COLORS['TT_DarkBlue']),
                    height=600,
                    margin=dict(t=80, b=120, l=80, r=80),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                fig_bar.update_xaxes(
                    showgrid=False,
                    linecolor=COLORS['TT_Grey'],
                    linewidth=2
                )
                fig_bar.update_yaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor=COLORS['TT_LightGrey'],
                    linecolor=COLORS['TT_Grey'],
                    linewidth=2
                )
                
                # Display plot
                config = {'displayModeBar': True, 'displaylogo': False}
                st.plotly_chart(fig_bar, config=config)
                
                # Export button
                pdf_bytes = pio.to_image(fig_bar, format='pdf')
                st.download_button(
                    label="📥 Download Plot as PDF",
                    data=pdf_bytes,
                    file_name="bar_chart_comparison.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("⚠️ No valid data for selected metrics.")
        else:
            st.info("ℹ️ Select at least one metric to compare.")
else:
    st.info("ℹ️ Add data to the table above to generate visualizations.")

# Footer
st.markdown("---")
st.markdown("*Glass Coating Analysis Tool - Compare and analyze glass coating performance metrics*")
