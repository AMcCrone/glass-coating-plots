import streamlit as st
import plotly.graph_objects as go


def create_scatter_plot(current_df, numeric_cols, COLORS, METRIC_COLORS):
    """
    Create scatter plot visualization tab.
    
    Args:
        current_df: DataFrame with coating data
        numeric_cols: List of numeric column names
        COLORS: Dictionary of theme colors
        METRIC_COLORS: List of metric colors
    """
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

    # Target controls
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
        return
    
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
            x0_rect = float(x_target)
            x1_rect = x_max + margin_x
        else:
            x0_rect = x_min - margin_x
            x1_rect = float(x_target)
        
        # Y-axis zone
        if y_axis in larger_than_metrics:
            y0_rect = float(y_target)
            y1_rect = y_max + margin_y
        else:
            y0_rect = y_min - margin_y
            y1_rect = float(y_target)
        
        # Draw highlight rectangle
        fig_scatter.add_shape(
            type="rect",
            x0=x0_rect, x1=x1_rect,
            y0=y0_rect, y1=y1_rect,
            fillcolor=COLORS['TT_LightBlue'],
            opacity=0.12,
            line=dict(width=0),
            xref='x', yref='y'
        )
        
        # Draw vertical target line
        fig_scatter.add_shape(
            type="line",
            x0=float(x_target), x1=float(x_target),
            y0=y_min - margin_y, y1=y_max + margin_y,
            line=dict(color=COLORS['TT_MidBlue'], width=2, dash='dash'),
            xref='x', yref='y'
        )
        
        # Draw horizontal target line
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
        
        # Build annotation text
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
