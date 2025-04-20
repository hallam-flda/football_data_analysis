import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def radar_spts(df, home_player=None, away_player=None, plot_average=False):
    # Select relevant columns
    keep_columns = df.columns[5:10].tolist()

    # Normalise metrics using Min-Max scaling
    df_norm = df.copy()
    df_norm[keep_columns] = (df[keep_columns] - df[keep_columns].min()) / (df[keep_columns].max() - df[keep_columns].min())

    chart_col_names = ["Live Ball SCAs", "Dead Ball % Taken", "Dead Ball SCAs", "Dead Ball GCAs", "Dead Ball<br>SCA Efficiency"]

    radar_data = []

    if home_player:
        home_player_row = df_norm[df_norm["player_name"] == home_player]
        home_player_values = home_player_row[keep_columns].iloc[0].tolist()
        radar_data.append({
            "Metric": chart_col_names,
            "Value": home_player_values,
            "Label": [home_player] * len(keep_columns)
        })

    if away_player:
        awa_player_row = df_norm[df_norm["player_name"] == away_player]
        away_player_values = awa_player_row[keep_columns].iloc[0].tolist()  
        radar_data.append({
            "Metric": chart_col_names,
            "Value": away_player_values,
            "Label": [away_player] * len(keep_columns)
        })

    # Averages for all players
    if plot_average:
        avg_values = df_norm[keep_columns].mean().tolist()
        radar_data.append({
            "Metric": chart_col_names,
            "Value": avg_values,
            "Label": ["Set Piece Taker Average"] * len(keep_columns)
        })

    # Combine all data into one DataFrame
    radar_df = pd.concat([pd.DataFrame(d) for d in radar_data], ignore_index=True)

    # Plot
    fig = px.line_polar(radar_df, r="Value", theta="Metric", color="Label", title=f"{home_player} vs {away_player}", line_close=True)
    fig.update_traces(fill='toself')
    fig.update_layout(
        title=dict(
            text=f"{home_player} vs {away_player}",
            x=0.3,          
            y=0.85,         
            xanchor='center',
            yanchor='top',
            font=dict(size=20)
            ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        polar=dict(
            domain=dict(x=[0.2, 0.8], y=[0.2, 0.8]),
            bgcolor='rgba(0,0,0,0)',
            angularaxis=dict(
                tickfont=dict(size=14),  
                rotation=90, 
                direction="clockwise" 
            )
        ),
        margin=dict(l=50, r=50, t=50, b=50) 
    )

    return fig

def cb_butterfly(home_player=None, away_player=None):
    # Example data
    metrics = ['Goals', 'Assists', 'Pass Accuracy', 'Tackles', 'Dribbles']
    player_a_stats = np.array([1, 7, 24, 30, 20])
    player_b_stats = np.array([6, 3, 84, 25, 22])

    # Normalise each metric (0-1 range)
    max_vals = np.maximum(player_a_stats, player_b_stats)
    player_a_norm = player_a_stats / max_vals
    player_b_norm = player_b_stats / max_vals

    # Reverse order for top-to-bottom plot
    metrics = metrics[::-1]
    player_a_stats = player_a_stats[::-1]
    player_b_stats = player_b_stats[::-1]
    player_a_norm = player_a_norm[::-1]
    player_b_norm = player_b_norm[::-1]

    fig = go.Figure()

    # Player A bars (left side)
    fig.add_trace(go.Bar(
        y=metrics,
        x=[-x for x in player_a_norm],
        orientation='h',
        name=home_player,
        marker=dict(color='blue', line=dict(width=0), pattern_shape="", opacity=0.9),
        width=0.4,
        hoverinfo='skip',
        text=[str(v) for v in player_a_stats],
        textposition='outside',
        textangle=0,
        insidetextanchor='start',
    ))

    # Player B bars (right side)
    fig.add_trace(go.Bar(
        y=metrics,
        x=player_b_norm,
        orientation='h',
        name=away_player,
        marker=dict(color='red', line=dict(width=0), opacity=0.9),
        width=0.4,
        hoverinfo='skip',
        text=[str(v) for v in player_b_stats],
        textposition='outside',
        insidetextanchor='start',
    ))

    # Add metric labels in the middle
    for i, metric in enumerate(metrics):
        fig.add_annotation(x=0, y=i, text=metric, showarrow=False,
                        font=dict(color='white', size=12, family="Arial"),
                        xanchor='center', yanchor='middle')

    # Layout config
    fig.update_layout(
        title='Player A vs Player B Comparison (Normalised)',
        barmode='relative',
        xaxis=dict(
            showgrid=False,
            zeroline=True,
            zerolinewidth=2,
            tickvals=[],
            showticklabels=False
        ),
        yaxis=dict(showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400,
        margin=dict(l=40, r=40, t=50, b=40),
        bargap=0.2,
    )
    return fig

