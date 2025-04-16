import pandas as pd
import plotly.express as px

def radar_spts(df, player=None, plot_average=False):
    # Select relevant columns
    keep_columns = df.columns[5:10].tolist()

    # Normalise metrics using Min-Max scaling
    df_norm = df.copy()
    df_norm[keep_columns] = (df[keep_columns] - df[keep_columns].min()) / (df[keep_columns].max() - df[keep_columns].min())

    chart_col_names = ["Live Ball SCAs", "Dead Ball % Taken", "Dead Ball SCAs", "Dead Ball GCAs", "Dead Ball<br>SCA Efficiency"]

    radar_data = []

    if player:
        player_row = df_norm[df_norm["player_name"] == player]
        player_values = player_row[keep_columns].iloc[0].tolist()
        radar_data.append({
            "Metric": chart_col_names,
            "Value": player_values,
            "Label": [player] * len(keep_columns)
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
    fig = px.line_polar(radar_df, r="Value", theta="Metric", color="Label", title=player, line_close=True)
    fig.update_traces(fill='toself')
    fig.update_layout(
        title=dict(
            text=player,
            x=0.2,          
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

 