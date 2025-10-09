import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def create_bar_chart(current_df, numeric_cols, COLORS, METRIC_COLORS):
    """
    Create bar chart comparison visualization tab.
    
    Args:
        current_df: DataFrame with coating data
        numeric_cols: List of numeric column names
        COLORS: Dictionary of theme colors
        METRIC_COLORS: List of metric colors
    """
    st.subheader("Bar Chart Comparison Settings")
    col1, col2 = st.columns([2, 1])
    with col1:
        metrics_to_compare = st.multiselect("Select Metrics to Compare", options=numeric_cols, default=[numeric_cols[0]] if numeric_cols else [])
    with col2:
        sort_by = st.selectbox("Sort By", options=["Supplier"] + metrics_to_compare if metrics_to_compare else ["Supplier"], index=0)

    if not metrics_to_compare:
        st.info("ℹ️ Select at least one metric to compare.")
        return
    
    bar_df = current_df.dropna(subset=metrics_to_compare)
    if len(bar_df) == 0:
        st.warning("⚠️ No valid data for selected metrics.")
        return
    
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
        
        # Normalize from 0 to max value
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
