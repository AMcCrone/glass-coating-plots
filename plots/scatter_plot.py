import streamlit as st
import plotly.graph_objects as go
import numpy as np


def adjust_label_positions(plot_df, x_axis, y_axis, x_range, y_range):
    """
    Adjust label positions to avoid overlaps using a simple collision detection algorithm.
    
    Returns a list of adjusted positions for each point.
    """
    positions = []
    occupied_zones = []  # Store (x_center, y_center, width, height) for each label
    
    # Normalize coordinates for collision detection
    x_vals = plot_df[x_axis].values
    y_vals = plot_df[y_axis].values
    
    # Label zones (relative to point, in normalized space)
    position_offsets = {
        "top center": (0, 0.08),
        "bottom center": (0, -0.08),
        "middle left": (-0.12, 0),
        "middle right": (0.12, 0),
        "top left": (-0.10, 0.06),
        "top right": (0.10, 0.06),
        "bottom left": (-0.10, -0.06),
        "bottom right": (0.10, -0.06)
    }
    
    position_priority = [
        "top right", "top left", "bottom right", "bottom left",
        "top center", "middle right", "middle left", "bottom center"
    ]
    
    def normalize_coords(x, y):
        """Normalize coordinates to 0-1 range"""
        x_norm = (x - x_vals.min()) / x_range if x_range > 0 else 0.5
        y_norm = (y - y_vals.min()) / y_range if y_range > 0 else 0.5
        return x_norm, y_norm
    
    def check_overlap(x, y, offset_x, offset_y):
        """Check if a label at this position would overlap with existing labels"""
        label_width = 0.15  # Approximate label width in normalized space
        label_height = 0.10  # Approximate label height in normalized space
        
        for occupied in occupied_zones:
            occ_x, occ_y, occ_w, occ_h = occupied
            # Check for rectangle overlap
            if (abs(x + offset_x - occ_x) < (label_width + occ_w) / 2 and
                abs(y + offset_y - occ_y) < (label_height + occ_h) / 2):
                return True
        return False
    
    for idx, row in plot_df.iterrows():
        x_norm, y_norm = normalize_coords(row[x_axis], row[y_axis])
        
        # Try each position in order of priority
        chosen_position = "top center"  # default
        for pos in position_priority:
            offset_x, offset_y = position_offsets[pos]
            if not check_overlap(x_norm, y_norm, offset_x, offset_y):
                chosen_position = pos
                occupied_zones.append((
                    x_norm + offset_x,
                    y_norm + offset_y,
                    0.15,  # width
                    0.10   # height
                ))
                break
        else:
            # If all positions overlap, use default and still mark as occupied
            offset_x, offset_y = position_offsets[chosen_position]
            occupied_zones.append((
                x_norm + offset_x,
                y_norm + offset_y,
                0.15,
                0.10
            ))
        
        positions.append(chosen_position)
    
    return positions


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

    # Get optimized label positions to avoid overlaps
    show_labels = show_supplier or show_coating
    if show_labels:
        label_positions = adjust_label_positions(plot_df, x_axis, y_axis, x_range, y_range)
    
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
        
        # Fix: Only set text mode and position if we have text to display
        if annotation_text:
            textmode = 'markers+text'
            textpos = label_positions[idx]
        else:
            textmode = 'markers'
            textpos = None  # Don't set textposition when there's no text

        hover_text = (
            f"<b>{supplier_txt}</b><br>Coating: {coating_txt}<br>"
            f"Glass: {row.get('Glass Name','')}<br>Type: {row.get('Glass Type','')}<br>"
            f"{x_axis}: {row[x_axis]}<br>{y_axis}: {row[y_axis]}"
        )

        trace_params = {
            'x': [row[x_axis]],
            'y': [row[y_axis]],
            'mode': textmode,
            'marker': dict(size=point_size, color=point_color, line=dict(width=1.2, color=COLORS['TT_DarkBlue'])),
            'hovertemplate': hover_text + "<extra></extra>",
            'showlegend': False,
            'name': ""
        }
        
        # Only add text-related parameters if we have text
        if annotation_text:
            trace_params['text'] = annotation_text
            trace_params['textposition'] = textpos
            trace_params['textfont'] = dict(size=9, color=COLORS['TT_DarkBlue'])
        
        fig_scatter.add_trace(go.Scatter(**trace_params))

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
