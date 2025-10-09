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

EDITOR_KEY = "editor_df"

def sync_editor_to_df():
    widget_val = st.session_state.get(EDITOR_KEY)
    if isinstance(widget_val, pd.DataFrame):
        st.session_state.df = widget_val.copy()

# ------------------ Data Entry UI ------------------
st.header("Data Entry")
st.markdown("Edit the table below.")

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

    tab1, tab2, tab3 = st.tabs(["Scatter Plot", "Bar Chart Comparison", "Radial Plots"])

    # TAB 1: SCATTER PLOT - Fixed version
    with tab1:
        st.subheader("Scatter Plot Settings")
        col1, col2, col3 = st.columns(3)
    
        with col1:
            default_x = "G-Value" if "G-Value" in numeric_cols else (numeric_cols[0] if numeric_cols else None)
            x_axis = st.selectbox("X-Axis", numeric_cols, index=numeric_cols.index(default_x) if default_x in numeric_cols else 0, key="scatter_x")
        with col2:
            default_y = "VLT (%)" if "VLT (%)" in numeric_cols else (numeric_cols[0] if numeric_cols else None)
            y_axis = st.selectbox("Y-Axis", numeric_cols, index=numeric_cols.index(default_y) if default_y in numeric_cols else 0, key="scatter_y")
        with col3:
            show_supplier = st.checkbox("Show Supplier", value=True)
            show_coating = st.checkbox("Show Coating", value=True)
    
        point_size = 15
        point_color = COLORS['TT_Orange']
    
        # Target controls - always show
        st.markdown("**Target lines & highlight zone**")
        tcol1, tcol2, tcol3 = st.columns([1, 1, 1])
        with tcol1:
            show_targets = st.checkbox("Show target lines / highlight zone", value=False)
        with tcol2:
            x_target = st.number_input(f"{x_axis} target", 
                                      min_value=0.0, 
                                      max_value=100.0 if "(%)" in x_axis else 10.0,
                                      step=0.01 if x_axis in ["G-Value", "U-Value (W/m²K)"] else 0.1,
                                      value=0.35 if x_axis == "G-Value" else (60.0 if x_axis == "VLT (%)" else 10.0),
                                      key="x_target_input")
        with tcol3:
            y_target = st.number_input(f"{y_axis} target",
                                      min_value=0.0,
                                      max_value=100.0 if "(%)" in y_axis else 10.0,
                                      step=0.01 if y_axis in ["G-Value", "U-Value (W/m²K)"] else 0.1,
                                      value=60.0 if y_axis == "VLT (%)" else (0.35 if y_axis == "G-Value" else 10.0),
                                      key="y_target_input")
        
        # Define which metrics should be "larger than" target vs "less than" target
        larger_than_metrics = ["VLT (%)", "Color Rendering Index"]
        less_than_metrics = ["External Reflectance (%)", "Internal Reflectance (%)", 
                           "G-Value", "U-Value (W/m²K)", "Embodied Carbon (kgCO2e/m²)"]
    
        plot_df = current_df.dropna(subset=[x_axis, y_axis]).reset_index(drop=True)
        if len(plot_df) == 0:
            st.warning("⚠️ No valid data points to plot. Please ensure numeric values are entered.")
        else:
            x_min, x_max = float(plot_df[x_axis].min()), float(plot_df[x_axis].max())
            y_min, y_max = float(plot_df[y_axis].min()), float(plot_df[y_axis].max())
            
            # Add 15% padding around data points
            x_range = (x_max - x_min) if (x_max > x_min) else max(abs(x_min), 1.0)
            y_range = (y_max - y_min) if (y_max > y_min) else max(abs(y_min), 1.0)
            margin_x = x_range * 0.15
            margin_y = y_range * 0.15
    
            fig_scatter = go.Figure()
    
            # Draw target zone and lines if enabled
            if show_targets:
                # Determine target zone based on metric types
                # X-axis zone
                if x_axis in larger_than_metrics:
                    # Good zone is >= x_target
                    x0_rect = float(x_target)
                    x1_rect = x_max + margin_x
                else:  # x_axis in less_than_metrics
                    # Good zone is <= x_target
                    x0_rect = x_min - margin_x
                    x1_rect = float(x_target)
                
                # Y-axis zone
                if y_axis in larger_than_metrics:
                    # Good zone is >= y_target
                    y0_rect = float(y_target)
                    y1_rect = y_max + margin_y
                else:  # y_axis in less_than_metrics
                    # Good zone is <= y_target
                    y0_rect = y_min - margin_y
                    y1_rect = float(y_target)
                
                # Draw highlight rectangle (intersection of good zones)
                fig_scatter.add_shape(
                    type="rect",
                    x0=x0_rect, x1=x1_rect,
                    y0=y0_rect, y1=y1_rect,
                    fillcolor=COLORS['TT_LightBlue'],
                    opacity=0.12,
                    line=dict(width=0),
                    xref='x', yref='y'
                )
                
                # Draw vertical target line for x-axis
                fig_scatter.add_shape(
                    type="line",
                    x0=float(x_target), x1=float(x_target),
                    y0=y_min - margin_y, y1=y_max + margin_y,
                    line=dict(color=COLORS['TT_MidBlue'], width=2, dash='dash'),
                    xref='x', yref='y'
                )
                
                # Draw horizontal target line for y-axis
                fig_scatter.add_shape(
                    type="line",
                    x0=x_min - margin_x, x1=x_max + margin_x,
                    y0=float(y_target), y1=float(y_target),
                    line=dict(color=COLORS['TT_MidBlue'], width=2, dash='dash'),
                    xref='x', yref='y'
                )
    
            label_positions = [
                "top center", "bottom center", "middle left", "middle right",
                "top left", "top right", "bottom left", "bottom right"
            ]
    
            for idx, row in plot_df.iterrows():
                supplier_txt = str(row.get('Supplier', ''))
                coating_txt = str(row.get('Coating Name', ''))
                
                # Build annotation text based on checkboxes
                annotation_lines = []
                if show_supplier:
                    annotation_lines.append(supplier_txt)
                if show_coating:
                    annotation_lines.append(coating_txt)
                
                annotation_text = "<br>".join(annotation_lines) if annotation_lines else ""
                
                textmode = 'markers+text' if annotation_text else 'markers'
                textpos = label_positions[idx % len(label_positions)] if annotation_text else ""
    
                hover_text = (
                    f"<b>{supplier_txt}</b><br>Coating: {coating_txt}<br>"
                    f"Glass: {row.get('Glass Name','')}<br>Type: {row.get('Glass Type','')}<br>"
                    f"{x_axis}: {row[x_axis]}<br>{y_axis}: {row[y_axis]}"
                )
    
                fig_scatter.add_trace(go.Scatter(
                    x=[row[x_axis]],
                    y=[row[y_axis]],
                    mode=textmode,
                    marker=dict(size=point_size, color=point_color, line=dict(width=1.2, color=COLORS['TT_DarkBlue'])),
                    text=annotation_text,
                    textposition=textpos,
                    textfont=dict(size=9, color=COLORS['TT_DarkBlue']),
                    hovertemplate=hover_text + "<extra></extra>",
                    showlegend=False,
                    name=""
                ))
    
            # Set axis ranges with padding
            x_axis_min = x_min - margin_x
            x_axis_max = x_max + margin_x
            y_axis_min = y_min - margin_y
            y_axis_max = y_max + margin_y
    
            fig_scatter.update_xaxes(range=[x_axis_min, x_axis_max])
            fig_scatter.update_yaxes(range=[y_axis_min, y_axis_max])
    
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

    # TAB 2: BAR CHART - Normalized version
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

                # Normalize each metric to 0-1 range
                for i, metric in enumerate(metrics_to_compare):
                    color = METRIC_COLORS[i % len(METRIC_COLORS)]
                    
                    # Get actual values
                    actual_values = bar_df[metric]
                    
                    # Normalize from 0 to max value (not min to max)
                    max_val = actual_values.max()
                    if max_val > 0:
                        normalized = actual_values / max_val
                    else:
                        normalized = pd.Series([0.0] * len(actual_values))
                    
                    # Create text labels showing actual values
                    text_labels = [f"{val:.2f}" if val < 10 else f"{val:.1f}" for val in actual_values]
                    
                    fig_bar.add_trace(go.Bar(
                        name=metric,
                        x=bar_df['Label'],
                        y=normalized,
                        marker_color=color,
                        text=text_labels,
                        textposition='outside',
                        hovertemplate=f"<b>%{{x}}</b><br>{metric}: %{{text}}<extra></extra>"
                    ))

                fig_bar.update_layout(
                    title=dict(text="Performance Metrics Comparison (Normalized)", font=dict(size=18, color=COLORS['TT_DarkBlue'])),
                    xaxis_title="Product",
                    yaxis_title="",
                    barmode='group',
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Arial, sans-serif", color=COLORS['TT_DarkBlue']),
                    height=600,
                    margin=dict(t=80, b=120, l=80, r=80),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    yaxis=dict(
                        showticklabels=False,
                        showgrid=False,
                        range=[0, 1.2]  # Extra space for text labels
                    )
                )

                fig_bar.update_xaxes(showgrid=False, linecolor=COLORS['TT_Grey'], linewidth=2)
                fig_bar.update_yaxes(showgrid=False, linecolor=COLORS['TT_Grey'], linewidth=2, zeroline=False)

                config = {'displayModeBar': True, 'displaylogo': False, 'toImageButtonOptions': {'format': 'svg', 'filename': 'bar_chart_comparison', 'height': 600, 'width': 1000, 'scale': 1}}
                st.plotly_chart(fig_bar, config=config)
                html_str = fig_bar.to_html(include_plotlyjs='cdn')
                st.download_button(label="📥 Download Interactive Plot (HTML)", data=html_str, file_name="bar_chart_comparison.html", mime="text/html")
            else:
                st.warning("⚠️ No valid data for selected metrics.")
        else:
            st.info("ℹ️ Select at least one metric to compare.")

# TAB 3: RADIAL PLOTS
    with tab3:
        st.subheader("Radial Plot Settings")
        st.markdown("Compare all metrics for each supplier. Each coating from the same supplier is overlaid.")
        
        # Get unique suppliers
        unique_suppliers = sorted(current_df['Supplier'].dropna().unique())
        
        if len(unique_suppliers) == 0:
            st.info("ℹ️ No supplier data available.")
        else:
            # Multi-select for suppliers (default: all selected)
            selected_suppliers = st.multiselect(
                "Select Suppliers to Display",
                options=unique_suppliers,
                default=unique_suppliers,
                key="radial_supplier_select"
            )
            
            if len(selected_suppliers) == 0:
                st.info("ℹ️ Please select at least one supplier to display.")
            else:
                # Calculate global max for each metric for normalization
                global_max = {}
                for col in numeric_cols:
                    max_val = current_df[col].max()
                    global_max[col] = max_val if pd.notna(max_val) and max_val > 0 else 1.0
                
                # Create columns based on number of selected suppliers
                num_suppliers = len(selected_suppliers)
                cols = st.columns(num_suppliers)
                
                # Create a radial plot for each selected supplier
                for col_idx, supplier in enumerate(selected_suppliers):
                    supplier_df = current_df[current_df['Supplier'] == supplier].copy()
                    
                    # Filter out rows with too many missing values
                    supplier_df = supplier_df.dropna(subset=numeric_cols, thresh=len(numeric_cols)//2)
                    
                    if len(supplier_df) == 0:
                        continue
                    
                    with cols[col_idx]:
                        fig_radial = go.Figure()
                        
                        # Plot each coating from this supplier
                        for idx, row in supplier_df.iterrows():
                            coating_name = str(row.get('Coating Name', f'Coating {idx}'))
                            
                            # Normalize values and store actual values for hover
                            normalized_values = []
                            actual_values = []
                            for metric in numeric_cols:
                                val = row[metric]
                                if pd.notna(val):
                                    normalized = val / global_max[metric]
                                    normalized_values.append(normalized)
                                    actual_values.append(val)
                                else:
                                    normalized_values.append(0)
                                    actual_values.append(None)
                            
                            # Close the polygon
                            normalized_values.append(normalized_values[0])
                            actual_values.append(actual_values[0])
                            categories = numeric_cols + [numeric_cols[0]]
                            
                            # Use different colors for different coatings from same supplier
                            color = METRIC_COLORS[idx % len(METRIC_COLORS)]
                            
                            # Build custom hover text with actual values
                            hover_template = '<b>' + coating_name + '</b><br>%{theta}<br>Value: %{customdata:.2f}<extra></extra>'
                            
                            fig_radial.add_trace(go.Scatterpolar(
                                r=normalized_values,
                                theta=categories,
                                name=coating_name,
                                fill='toself',
                                fillcolor=color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                                line=dict(color=color, width=2),
                                customdata=actual_values,
                                hovertemplate=hover_template
                            ))
                        
                        fig_radial.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 1],
                                    showticklabels=False,  # Hide normalized values
                                    ticks='',
                                    gridcolor=COLORS['TT_LightGrey']
                                ),
                                angularaxis=dict(
                                    tickfont=dict(size=10, color=COLORS['TT_DarkBlue']),
                                    linecolor=COLORS['TT_Grey']
                                ),
                                bgcolor='white'
                            ),
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font=dict(family="Arial, sans-serif", color=COLORS['TT_DarkBlue']),
                            height=550,
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="top",
                                y=-0.15,
                                xanchor="center",
                                x=0.5
                            ),
                            title=dict(
                                text=f"{supplier}",
                                font=dict(size=14, color=COLORS['TT_DarkBlue']),
                                y=0.95
                            ),
                            margin=dict(t=50, b=100, l=40, r=40)
                        )
                        
                        config = {
                            'displayModeBar': True,
                            'displaylogo': False,
                            'toImageButtonOptions': {
                                'format': 'svg',
                                'filename': f'radial_plot_{supplier.replace(" ", "_")}',
                                'height': 550,
                                'width': 600,
                                'scale': 1
                            }
                        }
                        st.plotly_chart(fig_radial, config=config, use_container_width=True)
                        
                        html_str = fig_radial.to_html(include_plotlyjs='cdn')
                        st.download_button(
                            label=f"📥 Download HTML", 
                            data=html_str, 
                            file_name=f"radial_plot_{supplier.replace(' ', '_')}.html", 
                            mime="text/html",
                            key=f"download_radial_{supplier}"
                        )
                
                st.markdown("---")
else:
    st.info("ℹ️ Add data to the table above to generate visualizations.")

st.markdown("---")
st.markdown("*Glass Coating Analysis Tool - Compare and analyze glass coating performance metrics*")
