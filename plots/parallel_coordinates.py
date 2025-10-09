import streamlit as st
import plotly.graph_objects as go


def create_parallel_coordinates(current_df, numeric_cols, COLORS, METRIC_COLORS):
    """
    Create parallel coordinates plot visualization tab.
    
    Args:
        current_df: DataFrame with coating data
        numeric_cols: List of numeric column names
        COLORS: Dictionary of theme colors
        METRIC_COLORS: List of metric colors
    """
    st.subheader("Parallel Coordinates Plot")
    st.markdown("Compare all coatings across multiple performance metrics. Each line represents a coating, colored by supplier.")
    
    # Prepare data - fill NaN with 0
    parallel_df = current_df.copy()
    parallel_df[numeric_cols] = parallel_df[numeric_cols].fillna(0)
    
    if len(parallel_df) == 0:
        st.info("ℹ️ No data available for parallel coordinates plot.")
        return
    
    # Create a color mapping for suppliers
    unique_suppliers_parallel = parallel_df['Supplier'].unique()
    # Generate different shades of blue for each supplier
    blue_shades = [
        'rgb(0,48,60)',      # TT_DarkBlue
        'rgb(0,163,173)',    # TT_MidBlue
        'rgb(136,219,223)',  # TT_LightBlue
        'rgb(70,130,180)',   # Steel Blue
        'rgb(30,144,255)',   # Dodger Blue
        'rgb(0,105,148)',    # Dark Cerulean
        'rgb(65,105,225)',   # Royal Blue
        'rgb(100,149,237)',  # Cornflower Blue
        'rgb(176,224,230)',  # Powder Blue
        'rgb(135,206,250)',  # Light Sky Blue
    ]
    
    supplier_color_map = {}
    for idx, supplier in enumerate(unique_suppliers_parallel):
        supplier_color_map[supplier] = blue_shades[idx % len(blue_shades)]
    
    # Map colors to each row
    parallel_df['Color'] = parallel_df['Supplier'].map(supplier_color_map)
    
    # Convert RGB strings to numeric values for Plotly (0-1 scale)
    def rgb_to_plotly(rgb_str):
        # Extract numbers from 'rgb(r,g,b)'
        rgb_values = rgb_str.replace('rgb(', '').replace(')', '').split(',')
        r, g, b = [int(x) / 255 for x in rgb_values]
        return [r, g, b]
    
    color_numeric = [rgb_to_plotly(c) for c in parallel_df['Color']]
    
    # Create range controls for each metric
    st.markdown("**Filter by metric ranges:**")
    range_controls = {}
    
    # Create columns for range inputs (3 metrics per row)
    num_metrics = len(numeric_cols)
    cols_per_row = 3
    
    for i in range(0, num_metrics, cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < num_metrics:
                metric = numeric_cols[i + j]
                with col:
                    min_val = float(parallel_df[metric].min())
                    max_val = float(parallel_df[metric].max())
                    
                    # Set step size based on metric
                    if metric in ["G-Value", "U-Value (W/m²K)"]:
                        step = 0.01
                    else:
                        step = 0.1
                    
                    range_controls[metric] = st.slider(
                        f"{metric}",
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val),
                        step=step,
                        key=f"parallel_range_{metric}"
                    )
    
    # Build dimensions for parallel coordinates
    dimensions = []
    for metric in numeric_cols:
        min_range, max_range = range_controls[metric]
        dimensions.append(
            dict(
                range=[float(parallel_df[metric].min()), float(parallel_df[metric].max())],
                constraintrange=[min_range, max_range],
                label=metric,
                values=parallel_df[metric].tolist()
            )
        )
    
    # Add labels for hover
    labels = []
    for idx, row in parallel_df.iterrows():
        label = f"{row['Supplier']} - {row['Coating Name']}"
        labels.append(label)
    
    fig_parallel = go.Figure(data=
        go.Parcoords(
            line=dict(
                color=[i for i in range(len(parallel_df))],
                colorscale=[[i/(len(parallel_df)-1 if len(parallel_df) > 1 else 1), 
                           f'rgb({int(c[0]*255)},{int(c[1]*255)},{int(c[2]*255)})'] 
                          for i, c in enumerate(color_numeric)],
                showscale=False,
                cmin=0,
                cmax=len(parallel_df)-1
            ),
            dimensions=dimensions
        )
    )
    
    fig_parallel.update_layout(
        title=dict(
            text="Coating Performance - Parallel Coordinates",
            font=dict(size=18, color=COLORS['TT_DarkBlue'])
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", color=COLORS['TT_DarkBlue'], size=11),
        height=600,
        margin=dict(t=100, b=50, l=100, r=100)
    )
    
    # Add legend for suppliers
    st.markdown("**Supplier Color Legend:**")
    legend_cols = st.columns(min(len(unique_suppliers_parallel), 5))
    for idx, supplier in enumerate(unique_suppliers_parallel):
        with legend_cols[idx % 5]:
            color = supplier_color_map[supplier]
            st.markdown(f"<span style='color:{color}; font-size:20px;'>●</span> {supplier}", unsafe_allow_html=True)
    
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'toImageButtonOptions': {
            'format': 'svg',
            'filename': 'parallel_coordinates',
            'height': 600,
            'width': 1200,
            'scale': 1
        }
    }
    st.plotly_chart(fig_parallel, config=config, use_container_width=True)
    
    html_str = fig_parallel.to_html(include_plotlyjs='cdn')
    st.download_button(
        label="📥 Download Parallel Coordinates Plot (HTML)",
        data=html_str,
        file_name="parallel_coordinates.html",
        mime="text/html",
        key="download_parallel"
    )
