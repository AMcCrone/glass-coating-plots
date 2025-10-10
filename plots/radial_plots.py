import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def create_radial_plots(current_df, numeric_cols, COLORS, METRIC_COLORS):
    """
    Create radial plot visualization tab.
    
    Args:
        current_df: DataFrame with coating data
        numeric_cols: List of numeric column names
        COLORS: Dictionary of theme colors
        METRIC_COLORS: List of metric colors
    """
    st.subheader("Radial Plot Settings")
    st.markdown("Compare all metrics for each supplier. Each coating from the same supplier is overlaid.")
    
    # Get unique suppliers
    unique_suppliers = sorted(current_df['Supplier'].dropna().unique())
    
    if len(unique_suppliers) == 0:
        st.info("ℹ️ No supplier data available.")
        return
    
    # Multi-select for suppliers (default: all selected)
    selected_suppliers = st.multiselect(
        "Select Suppliers to Display",
        options=unique_suppliers,
        default=unique_suppliers,
        key="radial_supplier_select"
    )
    
    if len(selected_suppliers) == 0:
        st.info("ℹ️ Please select at least one supplier to display.")
        return
    
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
    
    st.markdown("---")
